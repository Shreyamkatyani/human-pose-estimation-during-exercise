import numpy as np
import cv2
from .utils import calculate_angle, draw_text_with_background
import mediapipe as mp

class ExerciseAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        
        # State variables for counting reps or tracking status
        self.bicep_stage = None
        self.bicep_counter = 0
        
        self.lateral_raise_stage = None
        self.lateral_raise_counter = 0
        
        self.squat_stage = None
        self.squat_counter = 0

    def analyze_bicep_curl(self, img, lmList):
        """
        Rule 1: Elbow Angle
        - Down: > 160 degrees
        - Up: < 30 degrees
        """
        feedback = "Good"
        color = (0, 255, 0)
        
        # Right arm (12, 14, 16) or Left arm (11, 13, 15)
        # We'll detect which side is more visible or process both. 
        # For simplicity, let's process the right arm.
        
        # Indices for Right Arm
        shoulder = 12
        elbow = 14
        wrist = 16
        
        # Check visibility
        if lmList[shoulder][3] < 0.5 or lmList[elbow][3] < 0.5 or lmList[wrist][3] < 0.5:
            draw_text_with_background(img, "Keypoints not visible", (50, 200), bg_color=(0, 0, 255))
            return img, "Keypoints not visible"

        angle = calculate_angle(lmList[shoulder][1:3], lmList[elbow][1:3], lmList[wrist][1:3])
        
        # Visualize angle
        cv2.putText(img, str(int(angle)), (lmList[elbow][1], lmList[elbow][2]), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Logic
        if angle > 160:
            self.bicep_stage = "down"
        if angle < 30 and self.bicep_stage == 'down':
            self.bicep_stage = "up"
            self.bicep_counter += 1
            
        # Feedback logic (e.g., if angle stays in middle too long, or if form is bad)
        # Here we just track reps for now, but we can add specific warnings.
        # Example: Check if shoulder is moving too much (cheating)
        
        draw_text_with_background(img, f"Reps: {self.bicep_counter}", (50, 50))
        draw_text_with_background(img, f"Stage: {self.bicep_stage}", (50, 100))
        
        return img, feedback

    def analyze_lateral_raise(self, img, lmList):
        """
        Rule 2: Wrist-Shoulder Alignment
        - At the top of the movement, wrist should not be significantly higher than shoulder.
        - Elbow should be slightly bent, not locked.
        """
        feedback = "Good"
        
        # Right side
        shoulder = 12
        elbow = 14
        wrist = 16
        hip = 24
        
        if lmList[shoulder][3] < 0.5 or lmList[wrist][3] < 0.5:
            draw_text_with_background(img, "Keypoints not visible", (50, 200), bg_color=(0, 0, 255))
            return img, "Keypoints not visible"
            
        # Calculate angle of arm with body (abduction)
        # Vertical line from shoulder down to hip vs shoulder to elbow
        # Actually, simpler: angle at shoulder (hip-shoulder-elbow)
        shoulder_angle = calculate_angle(lmList[hip][1:3], lmList[shoulder][1:3], lmList[elbow][1:3])
        
        # Check wrist height relative to shoulder
        wrist_y = lmList[wrist][2]
        shoulder_y = lmList[shoulder][2]
        
        # Feedback
        if shoulder_angle > 70: # Arm is raised
            if wrist_y < shoulder_y - 20: # Wrist significantly above shoulder (y is inverted in image coords)
                feedback = "Wrist too high!"
                draw_text_with_background(img, feedback, (lmList[wrist][1], lmList[wrist][2] - 20), bg_color=(0, 0, 255))
            else:
                feedback = "Good alignment"
                
        draw_text_with_background(img, f"Angle: {int(shoulder_angle)}", (50, 50))
        
        return img, feedback

    def analyze_squat(self, img, lmList):
        """
        Rule 3: Back Posture / Depth
        - Check hip angle (shoulder-hip-knee) for back lean.
        - Check knee angle (hip-knee-ankle) for depth.
        """
        feedback = "Good"
        
        # Right side
        shoulder = 12
        hip = 24
        knee = 26
        ankle = 28
        
        if lmList[hip][3] < 0.5 or lmList[knee][3] < 0.5 or lmList[ankle][3] < 0.5:
             draw_text_with_background(img, "Keypoints not visible", (50, 200), bg_color=(0, 0, 255))
             return img, "Keypoints not visible"

        # Knee Angle (Depth)
        knee_angle = calculate_angle(lmList[hip][1:3], lmList[knee][1:3], lmList[ankle][1:3])
        
        # Hip Angle (Back lean)
        hip_angle = calculate_angle(lmList[shoulder][1:3], lmList[hip][1:3], lmList[knee][1:3])
        
        # Logic
        if knee_angle < 90:
            status = "Deep Squat"
        elif knee_angle < 140:
            status = "Squatting"
        else:
            status = "Standing"
            
        # Back lean check
        if status == "Squatting" or status == "Deep Squat":
            if hip_angle < 70: # Leaning too forward
                feedback = "Keep back straight!"
                draw_text_with_background(img, feedback, (lmList[hip][1], lmList[hip][2]), bg_color=(0, 0, 255))
        
        draw_text_with_background(img, f"Depth: {int(knee_angle)}", (50, 50))
        draw_text_with_background(img, f"Back: {int(hip_angle)}", (50, 100))
        
        return img, feedback
