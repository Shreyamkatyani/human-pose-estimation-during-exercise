import numpy as np
import cv2

def calculate_angle(a, b, c):
    """
    Calculates the angle between three points a, b, and c.
    Points are expected to be [x, y] or [x, y, z].
    Angle is calculated at point b.
    Returns angle in degrees.
    """
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360-angle
        
    return angle

def draw_text_with_background(image, text, position, font=cv2.FONT_HERSHEY_SIMPLEX, 
                            font_scale=0.6, text_color=(255, 255, 255), bg_color=(0, 0, 0), thickness=1):
    """
    Draws text with a background rectangle for better visibility.
    """
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    x, y = position
    
    # Draw background rectangle
    cv2.rectangle(image, (x, y - text_height - 5), (x + text_width, y + 5), bg_color, -1)
    
    # Draw text
    cv2.putText(image, text, (x, y), font, font_scale, text_color, thickness, cv2.LINE_AA)
