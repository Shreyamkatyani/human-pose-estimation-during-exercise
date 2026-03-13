# AI Fitness Trainer - Form Correctness Detection

This project implements a computer vision pipeline to analyze exercise form using MediaPipe Pose. It detects keypoints and applies geometric rules to evaluate correctness for Bicep Curls, Lateral Raises, and Squats.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Web Application (Recommended)**:
    We have provided a Streamlit interface for easy video uploads and live webcam analysis. To start the app:
    ```bash
    streamlit run app.py
    ```

3.  **Run the Command Line Interface (Alternative)**:
    You can also run the application on a video file or use your webcam directly from the terminal.

    *   **Webcam (Default)**:
        ```bash
        # 1. Bicep Curl
        python main.py --exercise bicep_curl
        
        # 2. Lateral Raise
        python main.py --exercise lateral_raise
        
        # 3. Squat
        python main.py --exercise squat
        ```

    *   **Custom Video File**:
        You can provide your own pre-recorded exercise video to be analyzed by supplying the video path:
        ```bash
        # 1. Bicep Curl
        python main.py --video "path/to/your/bicep_video.mp4" --exercise bicep_curl --output "output/bicep_result.mp4"
        
        # 2. Squat
        python main.py --video "path/to/your/squat_video.mp4" --exercise squat --output "output/squat_result.mp4"
        
        # 3. Lateral Raise
        python main.py --video "path/to/your/lateral_raise_video.mp4" --exercise lateral_raise --output "output/shoulder_result.mp4"
        ```
 
## Supported Exercises

*   **Bicep Curl**: Checks for full range of motion (Elbow Angle).
*   **Lateral Raise**: Checks for wrist-shoulder alignment and arm angle.
*   **Squat**: Checks for depth (Knee Angle) and back posture (Hip Angle).

## Key Features
*   **Interactive Web Dashboard**: A modern, responsive Streamlit web application with animated UI, live pulsing indicators, and interactive layout.
*   **Real-time Posture Analysis**: Visual overlays for angles and repetition counters directly on the video feed.
*   **Dynamic Feedback Cards**: Color-coded alerts and a post-session summary report generated in real-time as you exercise.
*   **Video Uploads & Webcam Support**: Analyze pre-recorded MP4/MOV files or track your form live via your camera.
*   **Robust Error Handling & Auto-Resize**: Gracefully handles missing keypoints and automatically scales output to 720p for optimal performance.
*   **MLFlow Integration**: Stable, crash-resistant experiment tracking for metrics and parameters.

## Project Structure

*   `src/`: Contains source code.
    *   `pose_detector.py`: MediaPipe Pose wrapper.
    *   `exercises.py`: Logic for exercise analysis.
    *   `utils.py`: Geometry helper functions.
*   `app.py`: The Streamlit web application with custom UI elements.
*   `main.py`: Command-line entry point.
*   `docs/`: Documentation.
