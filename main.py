import asyncio
import httpx
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import Dict, Any

app = FastAPI(title="SIH Real-Time 4-Way Traffic Demo")

# Pre-defined weights for Indian road vehicles
# Note: Standard YOLO models detect cars, trucks, buses, and motorcycles. 
# To detect ambulances, firetrucks, and auto-rickshaws, you just swap the endpoint_url 
# to a custom model trained on Indian traffic later!
VEHICLE_WEIGHTS = {
    "car": 1,
    "motorcycle": 1,      # Two-wheeler
    "bus": 5,
    "truck": 5,
    "ambulance": 30,      # Emergency priority
    "firetruck": 15,      # Emergency priority
    "auto-rickshaw": 2    # Common Indian vehicle
}

async def analyze_image_ultralytics(
    client: httpx.AsyncClient, 
    file: UploadFile, 
    api_key: str, 
    endpoint_url: str, 
    direction: str
) -> Dict[str, Any]:
    """Sends a single image to the Ultralytics API and calculates the weighted score."""
    # Authenticate via Bearer token
    headers = {"Authorization": f"Bearer {api_key}"} 
    
    # Standard inference parameters: 25% confidence, 640px image size
    data = {"conf": 0.25, "iou": 0.7, "imgsz": 640} 
    
    # Read file bytes for multipart/form-data upload
    file_bytes = await file.read()
    files = {"file": (file.filename, file_bytes, file.content_type)}
    
    try:
        response = await client.post(endpoint_url, headers=headers, data=data, files=files, timeout=15.0)
        response.raise_for_status()
        result = response.json()
        
        # Parse Ultralytics JSON response
        detections = result.get("images", [{}])[0].get("results", [])
        
        score = 0
        counts = {k: 0 for k in VEHICLE_WEIGHTS.keys()}
        
        # Calculate scores based on the weights
        for det in detections:
            class_name = det.get("name", "").lower()
            if class_name in VEHICLE_WEIGHTS:
                counts[class_name] += 1
                score += VEHICLE_WEIGHTS[class_name]
                
        return {
            "direction": direction,
            "score": score,
            "vehicle_counts": {k: v for k, v in counts.items() if v > 0},
            "total_recognized_objects": len(detections)
        }
    except Exception as e:
        return {"direction": direction, "error": str(e), "score": 0}

@app.post("/api/v1/analyze-intersection")
async def analyze_intersection(
    north_img: UploadFile = File(...),
    south_img: UploadFile = File(...),
    east_img: UploadFile = File(...),
    west_img: UploadFile = File(...),
    api_key: str = Form("ul_e8a2fd1d8fc065b795ffae84df866a4d271292b9", description="Your Ultralytics API Key (starts with ul_)"),
    endpoint_url: str = Form(
        "https://platform.ultralytics.com/api/models/ultralytics/yolov8/yolov8n/predict", 
        description="Shared API or Dedicated Endpoint URL"
    )
):
    """
    Upload 4 images of an intersection. Analyzes all 4 concurrently via Ultralytics API,
    applies density weights, and determines which lane gets the Green light.
    """
    # Use an async HTTP client to process all 4 images simultaneously (zero blocking)
    async with httpx.AsyncClient() as client:
        tasks = [
            analyze_image_ultralytics(client, north_img, api_key, endpoint_url, "NORTH"),
            analyze_image_ultralytics(client, south_img, api_key, endpoint_url, "SOUTH"),
            analyze_image_ultralytics(client, east_img, api_key, endpoint_url, "EAST"),
            analyze_image_ultralytics(client, west_img, api_key, endpoint_url, "WEST"),
        ]
        
        # Await all 4 API calls concurrently
        results = await asyncio.gather(*tasks)

    # Sort the results by score (descending) to find the winner
    valid_results = [r for r in results if "error" not in r]
    if not valid_results:
        raise HTTPException(status_code=500, detail="All API calls failed. Check API key/URL.")
        
    sorted_results = sorted(valid_results, key=lambda x: x["score"], reverse=True)
    winner = sorted_results[0]

    # Output dynamic duration logic based on traffic density
    return {
        "status": "success",
        "action": f"OPEN {winner['direction']} LANE",
        "dynamic_green_light_duration": 30 + (winner["score"] // 2),
        "winner_details": winner,
        "all_lanes": sorted_results
    }