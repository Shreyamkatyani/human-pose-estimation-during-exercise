# Computer Vision & AI Internship Task Report

**Team Smartan.AI**

## 1. Overview
This project implements a form correctness detection pipeline using MediaPipe Pose. It analyzes exercises (Bicep Curl, Lateral Raise, Squat) by tracking body keypoints and applying geometric rules to provide real-time feedback.

## 2. Posture Rules and Logic

### 2.1 Bicep Curl
**Objective**: Ensure full range of motion.
*   **Keypoints**: Shoulder, Elbow, Wrist.
*   **Metric**: Elbow Angle.
*   **Logic**:
    *   The arm is considered "Down" (Extended) when the angle is > 160°.
    *   The arm is considered "Up" (Flexed) when the angle is < 30°.
    *   A repetition is counted only when the sequence Down -> Up is completed.

### 2.2 Lateral Raise
**Objective**: Target side deltoids safely.
*   **Keypoints**: Hip, Shoulder, Elbow, Wrist.
*   **Metric**: Shoulder Abduction Angle & Wrist-Shoulder Vertical Alignment.
*   **Logic**:
    *   **Alignment**: When the arm is raised (angle > 70°), the wrist should not be significantly higher than the shoulder.
    *   **Feedback**: If `Wrist_Y < Shoulder_Y - Threshold`, the system warns "Wrist too high!", indicating potential internal rotation or excessive elevation.

### 2.3 Squat
**Objective**: Safe depth and neutral spine.
*   **Keypoints**: Shoulder, Hip, Knee, Ankle.
*   **Metrics**: Knee Angle (Depth), Hip Angle (Back Lean).
*   **Logic**:
    *   **Depth**: Classified as "Deep Squat" (< 90°), "Squatting" (< 140°), or "Standing".
    *   **Back Posture**: If the Hip Angle (Shoulder-Hip-Knee) is < 70° during a squat, it indicates excessive forward lean ("Keep back straight!").

## 3. Challenges and Solutions

### 3.1 Keypoint Visibility
*   **Challenge**: Body parts may be occluded or out of frame.
*   **Solution**: The system checks the visibility confidence score provided by MediaPipe. If confidence is low (< 0.5), it pauses analysis and explicitly overlays "Keypoints not visible" on the video feed. Additionally, if no person is detected at all, it displays "No Person Detected".

### 3.4 Runtime Robustness
*   **Challenge**: Ensuring the application exits cleanely and windows resize correctly on different screens.
*   **Solution**: Implemented a robust window handling system that resizes the video frame itself (instead of the window) to 720p height for consistency. Added an auto-shutdown timer that closes the window 5 seconds after video completion to prevent hanging terminals.

### 3.2 Camera Perspective
*   **Challenge**: 2D angles vary based on camera angle (side view vs. front view).
*   **Solution**: The current logic assumes a general side/front-side view which is standard for form checks. Future improvements could use 3D landmarks (also available in MediaPipe) for view-invariant analysis.

### 3.3 Multiple Persons
*   **Challenge**: The standard MediaPipe Pose model tracks a single person.
*   **Handling**:
    *   Current implementation processes the most prominent person in the frame.
    *   To handle multiple people, we would integrate a multi-person detector (like YOLOv8-Pose). We would assign unique IDs to each detection and instantiate a separate `ExerciseAnalyzer` object for each ID to track their individual repetition counters and states.

### 4.2 MLFlow Integration
*   **Feature**: The application supports MLFlow for tracking experiment parameters (exercise type, video source) and metrics (frames processed).
*   **Implementation**: To ensure robustness against dependency conflicts (specifically Protobuf), MLFlow is imported conditionally. If the library is available and compatible, runs are logged; otherwise, the application proceeds without tracking.

## 4. Technical Implementation
*   **Framework**: Python, OpenCV, MediaPipe.
*   **Structure**: Modular design with separate classes for `PoseDetector` and `ExerciseAnalyzer`.
*   **Output**: Real-time video overlay with visual cues (angles, counters, warnings).
