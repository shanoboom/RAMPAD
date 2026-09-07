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
