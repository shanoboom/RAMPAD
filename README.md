Running the Environment

To test this locally on your Linux environment, open your terminal and run:
Bash

# Set up a clean environment
python3 -m venv traffic_env
source traffic_env/bin/activate

# Install the necessary web libraries
pip install fastapi uvicorn pydantic

# Run the server
uvicorn main:app --reload

Once running, navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser. This will open the auto-generated Swagger UI where you can visually test sending 5 frames (as mock strings) and watch the algorithm dynamically route the green lights based on your weights.





If you are seeing the old endpoint instead of the 4-image upload interface, Uvicorn is still running the old Python script in memory or loading a cached main.py file.

Step-by-Step Fix

    Stop the running server: In your terminal where Uvicorn is running, press Ctrl + C to completely kill the process.

    Verify file contents & location: Make sure you saved the new code into main.py in the exact directory where your terminal is open. You can check by running:
    Bash

    cat main.py

    (Ensure you see analyze_intersection and the UploadFile parameters inside).

    Re-run Uvicorn: Start the server again with the reload flag:
    Bash

    uvicorn main:app --reload

    Hard-refresh your browser: Go to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and press Ctrl + Shift + R (or Cmd + Shift + R on Mac) to clear the browser cache.

How to verify it updated

Once reloaded, click the dropdown for /api/v1/analyze-intersection in the Swagger UI and hit "Try it out". You should see four file upload inputs:

    north_img

    south_img

    east_img

    west_img
