# Posture Rules and Logic

## 1. Bicep Curl

**Objective**: Ensure full range of motion and proper form.

**Rules**:
*   **Elbow Angle**: Calculated using Shoulder, Elbow, and Wrist keypoints.
*   **Logic**:
    *   **Extension (Down)**: Angle > 160 degrees.
    *   **Flexion (Up)**: Angle < 30 degrees.
    *   **Feedback**: Counts a repetition only when the arm goes from full extension to full flexion.

## 2. Lateral Raise

**Objective**: Target the side deltoids without engaging the traps or risking shoulder impingement.

**Rules**:
*   **Wrist-Shoulder Alignment**: Checks the vertical position of the wrist relative to the shoulder.
*   **Shoulder Abduction Angle**: Angle between Hip, Shoulder, and Elbow.
*   **Logic**:
    *   **Alignment**: At the top of the movement (abduction > 70 degrees), the wrist should not be significantly higher than the shoulder. If `Wrist_Y < Shoulder_Y - Threshold`, it indicates bad form (internal rotation or lifting too high).
    *   **Feedback**: "Wrist too high!" if the wrist exceeds the safe zone.

## 3. Squat

**Objective**: Ensure proper depth and maintain a neutral spine.

**Rules**:
*   **Knee Angle (Depth)**: Angle between Hip, Knee, and Ankle.
*   **Hip Angle (Back Lean)**: Angle between Shoulder, Hip, and Knee.
*   **Logic**:
    *   **Depth**:
        *   < 90 degrees: "Deep Squat"
        *   < 140 degrees: "Squatting"
        *   > 140 degrees: "Standing"
    *   **Back Posture**:
        *   If `Hip Angle < 70 degrees` during a squat, it indicates excessive forward lean.
    *   **Feedback**: "Keep back straight!" if leaning too far forward.

## Challenges & Handling Multiple Persons

*   **Current Implementation**: The current script processes the first detected person. MediaPipe Pose is primarily a single-person tracker.
*   **Multiple Persons**: To handle multiple people, we would need to:
    1.  Use a multi-person detector (like YOLOv8-Pose or MoveNet MultiPose).
    2.  Assign unique IDs to each person.
    3.  Run the logic for each ID independently.
    4.  The current `PoseDetector` class can be extended to iterate over multiple detection results if we switch the underlying model.
