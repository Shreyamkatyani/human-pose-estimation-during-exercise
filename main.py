import sys
import os
import cv2
import argparse
from src.pose_detector import PoseDetector
from src.exercises import ExerciseAnalyzer

# Optional MLFlow Import - Must be robust to crashes
# Import AFTER MediaPipe to ensure core functionality works
try:
    import mlflow
    MLFLOW_AVAILABLE = True
except Exception as e:
    MLFLOW_AVAILABLE = False
    print(f"Warning: MLFlow could not be imported ({e}). Skipping experiment tracking.")

def main():
    global MLFLOW_AVAILABLE
    parser = argparse.ArgumentParser(description="AI Fitness Trainer")
    parser.add_argument("--video", type=str, help="Path to input video file. If not provided, uses webcam.")
    parser.add_argument("--exercise", type=str, default="bicep_curl", 
                        choices=["bicep_curl", "lateral_raise", "squat"],
                        help="Type of exercise to analyze.")
    parser.add_argument("--output", type=str, default="output/result.mp4", help="Path to save output video.")
    
    args = parser.parse_args()
    
    # Initialize Detector and Analyzer
    detector = PoseDetector()
    analyzer = ExerciseAnalyzer()
    
    # Video Capture
    if args.video:
        if not os.path.exists(args.video):
            print(f"Error: Video file not found at {args.video}")
            sys.exit(1)
        cap = cv2.VideoCapture(args.video)
    else:
        cap = cv2.VideoCapture(0) # Webcam
        
    if not cap.isOpened():
        print("Error: Could not open video source.")
        sys.exit(1)
        
    # Video Writer Setup
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps == 0: fps = 30 # Default if unknown
    
    out = cv2.VideoWriter(args.output, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))
    
    print(f"Starting analysis for {args.exercise}...")
    print("Press 'q' to quit.")

    print(f"Video Dimensions: {frame_width}x{frame_height}")

    # Start MLFlow Run (Safe Mode)
    if MLFLOW_AVAILABLE:
        try:
            mlflow.set_experiment("PoseAnalysis")
            mlflow.start_run()
            mlflow.log_param("exercise", args.exercise)
            mlflow.log_param("video_path", args.video if args.video else "Webcam")
        except Exception as e:
            print(f"MLFlow Error: {e}")
            MLFLOW_AVAILABLE = False # Disable if it crashes

    # Calculate resize scale once to fit 720p height
    target_height = 720
    scale = target_height / frame_height if frame_height > target_height else 1.0
    
    frame_count = 0
    while True:
        success, img = cap.read()
        if not success:
            print("Finished reading video.")
            break
        
        frame_count += 1
        if frame_count % 30 == 0:
            print(f"Processing frame {frame_count}...")
            
        # 1. Find Pose
        img = detector.find_pose(img)
        lmList = detector.find_position(img, draw=False)
        
        # 2. Analyze Exercise
        if len(lmList) != 0:
            if args.exercise == "bicep_curl":
                img, feedback = analyzer.analyze_bicep_curl(img, lmList)
            elif args.exercise == "lateral_raise":
                img, feedback = analyzer.analyze_lateral_raise(img, lmList)
            elif args.exercise == "squat":
                img, feedback = analyzer.analyze_squat(img, lmList)
        else:
            cv2.putText(img, "No Person Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
        # Resize image for display if needed
        if scale != 1.0:
            img = cv2.resize(img, (int(frame_width * scale), int(frame_height * scale)))
                
        # 3. Display & Save
        cv2.imshow("AI Trainer", img)
        out.write(img)
        
        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("User interrupted.")
            break
            
    print(f"Analysis complete. Output saved to {args.output}")
    
    if MLFLOW_AVAILABLE:
        try:
            mlflow.log_metric("frames_processed", frame_count)
            mlflow.end_run()
        except Exception:
            pass

    print("--------------------------------------------------")
    print("Closing window in 5 seconds... (Press 'q' to close sooner)")
    print("--------------------------------------------------")
    
    # Wait for 5 seconds or 'q'
    for _ in range(50): # 50 * 100ms = 5000ms = 5s
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
            
    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
