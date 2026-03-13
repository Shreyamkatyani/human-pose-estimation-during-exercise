import streamlit as st
import cv2
import tempfile
import base64
from src.pose_detector import PoseDetector
from src.exercises import ExerciseAnalyzer

st.set_page_config(
    page_title="AI Fitness Trainer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Advanced Custom CSS & Animations ---
st.markdown("""
<style>
/* Animated Gradient Header */
.gradient-text {
    background: linear-gradient(45deg, #FF4B4B, #FF8F00, #FF4B4B);
    background-size: 200% auto;
    color: #000;
    background-clip: text;
    text-fill-color: transparent;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradient 3s ease infinite;
    font-size: 3.5rem;
    font-weight: 900;
    text-align: center;
    margin-bottom: 0px;
    padding-bottom: 10px;
}
@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Sub-header text */
.sub-header {
    text-align: center;
    color: #888888;
    font-size: 1.2rem;
    letter-spacing: 1px;
    margin-bottom: 30px;
}

/* Pulsing Recording Indicator */
.pulse-circle {
    width: 15px;
    height: 15px;
    background-color: #ff3333;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 0 0 rgba(255, 51, 51, 1);
    animation: pulse 1.5s infinite;
    margin-right: 10px;
}
@keyframes pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 51, 51, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(255, 51, 51, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 51, 51, 0); }
}

/* Custom Feedback Cards with Hover effects */
.feedback-card {
    background-color: #1e1e2e;
    border-left: 5px solid #FF4B4B;
    padding: 15px 20px;
    border-radius: 5px;
    margin-bottom: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.feedback-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.2);
}
.feedback-card.positive { border-left-color: #00C851; background-color: #1a2920; }
.feedback-card.warning { border-left-color: #ffa900; background-color: #2b2416; }

/* Video Container glow */
.css-1v0mbdj.etr89bj1 {
    transition: all 0.3s ease;
}
.video-active > div > img {
    border-radius: 12px;
    box-shadow: 0 0 20px rgba(255, 75, 75, 0.15);
    border: 1px solid #333;
}

/* Sidebar styling overrides */
.css-1d391kg { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# --- Header Section ---
st.markdown('<div class="gradient-text">ProFit AI Trainer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">PRO-LEVEL FORM CORRECTION. POWERED BY AI.</div>', unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    # A sleek professional abstract/geometric or icon image from a reliable CDN instead of an emoji
    st.image("https://cdn-icons-png.flaticon.com/512/8243/8243750.png", width=70) 
    st.markdown("### Configuration Panel")
    st.markdown("---")
    
    exercise_type = st.radio(
        "Select Movement Pattern",
        ("Bicep Curl", "Lateral Raise", "Squat")
    )
    
    st.markdown("---")
    input_method = st.radio("Input Source", ("Upload Video", "Live Camera Feed"))
    st.markdown("---")
    
    st.markdown("💡 *Ensure bright lighting and full-body visibility for max accuracy.*")

# Map display names to internal keys
exercise_map = {
    "Bicep Curl": "bicep_curl",
    "Lateral Raise": "lateral_raise",
    "Squat": "squat"
}
selected_exercise = exercise_map[exercise_type]

# Initialize vision components properly cached
@st.cache_resource
def load_models():
    return PoseDetector(), ExerciseAnalyzer()

with st.spinner("Initializing AI Core..."):
    detector, analyzer = load_models()

def process_frame(img, exe_type, frame_width, frame_height):
    target_height = 720
    scale = target_height / frame_height if frame_height > target_height else 1.0
    
    img = detector.find_pose(img)
    lmList = detector.find_position(img, draw=False)
    
    feedback_msg = None
    if len(lmList) != 0:
        if exe_type == "bicep_curl":
            img, feedback_msg = analyzer.analyze_bicep_curl(img, lmList)
        elif exe_type == "lateral_raise":
            img, feedback_msg = analyzer.analyze_lateral_raise(img, lmList)
        elif exe_type == "squat":
            img, feedback_msg = analyzer.analyze_squat(img, lmList)
    else:
        cv2.putText(img, "Scanning Subject...", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 255), 2)
        
    if scale != 1.0:
        img = cv2.resize(img, (int(frame_width * scale), int(frame_height * scale)))
        
    return img, feedback_msg

# --- Dashboard Layout ---
col1, col2 = st.columns([2.5, 1.5])

with col1:
    # We create a placeholder header for the video state
    cam_status = st.empty()
    cam_status.markdown(f"### Visualizer: {exercise_type}")
    
    # Placeholder for the video feed. Wrap in a div that CSS targets for styling
    st.markdown('<div class="video-active">', unsafe_allow_html=True)
    stframe = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("### Telemetry Stream")
    
    # Active feedback placeholder
    active_feedback = st.empty()
    active_feedback.markdown(
       '<div class="feedback-card" style="border-left-color: #555;">Waiting for video feed initialization...</div>',
       unsafe_allow_html=True
    )
    
    st.markdown("<br><hr style='margin: 10px 0;'><br>", unsafe_allow_html=True)
    st.markdown("### Post-Session Report")
    summary_box = st.empty()
    summary_box.markdown("<span style='color:gray;'>Data will compile here after analysis.</span>", unsafe_allow_html=True)

all_feedback = set()

# Helper function to generate styled feedback cards
def draw_feedback_card(text):
    if "Good" in text or "Proper" in text or "Keep" in text:
        return f'<div class="feedback-card positive" style="animation: fadeIn 0.3s;"><strong>Form Accurate:</strong> {text}</div>'
    else:
        return f'<div class="feedback-card warning" style="animation: fadeIn 0.3s;"><strong>Correction Required:</strong> {text}</div>'

if input_method == "Upload Video":
    uploaded_video = st.file_uploader("Upload MP4 / MOV Video", type=["mp4", "mov", "avi"])

    if uploaded_video is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_video.read())
        
        cap = cv2.VideoCapture(tfile.name)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        cam_status.markdown(f"### Visualizer <span class='pulse-circle' style='background-color:#00aaff;'></span> Processing Upload", unsafe_allow_html=True)
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            
            processed_frame, feedback = process_frame(frame, selected_exercise, frame_width, frame_height)
            
            if feedback:
                if feedback not in all_feedback:
                    all_feedback.add(feedback)
                
                # Render the CSS animated feedback card
                active_feedback.markdown(draw_feedback_card(feedback), unsafe_allow_html=True)
            else:
                 active_feedback.markdown(
                     '<div class="feedback-card" style="border-left-color: #00aaff;">Analyzing joint coordinates...</div>', 
                     unsafe_allow_html=True
                 )
                 
            processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            stframe.image(processed_frame, channels="RGB", use_container_width=True)
            
        cap.release()
        cam_status.markdown(f"### Visualizer: {exercise_type} (Complete)")
        active_feedback.markdown('<div class="feedback-card positive">Video processing routine successfully completed.</div>', unsafe_allow_html=True)
        
        if all_feedback:
            summary_html = ""
            for msg in all_feedback:
                 summary_html += draw_feedback_card(msg)
            summary_box.markdown(summary_html, unsafe_allow_html=True)
        else:
            summary_box.markdown('<div class="feedback-card positive">Perfect form detected! No corrections needed.</div>', unsafe_allow_html=True)
            
elif input_method == "Live Camera Feed":
    st.info("Ensure the camera captures your full body.", icon="📷")
    run = st.checkbox("Initialize AI Tracking Protocol")
    
    if run:
        cap = cv2.VideoCapture(0)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        cam_status.markdown(f"### Visualizer <div class='pulse-circle'></div> LIVE Tracking", unsafe_allow_html=True)
        
        while run:
            success, frame = cap.read()
            if not success:
                st.error("Hardware Error: Camera feed inaccessible.")
                break
                
            processed_frame, feedback = process_frame(frame, selected_exercise, frame_width, frame_height)
            
            if feedback:
                if feedback not in all_feedback:
                    all_feedback.add(feedback)
                
                # Render the active feedback card live
                active_feedback.markdown(draw_feedback_card(feedback), unsafe_allow_html=True)
            else:
                 active_feedback.markdown(
                     '<div class="feedback-card" style="border-left-color: #555;">Scanning biometrics...</div>', 
                     unsafe_allow_html=True
                 )
                 
            processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            stframe.image(processed_frame, channels="RGB", use_container_width=True)
            
            # Dynamically update the summary during the live feed
            if all_feedback:
                summary_html = ""
                for msg in all_feedback:
                     summary_html += draw_feedback_card(msg)
                summary_box.markdown(summary_html, unsafe_allow_html=True)
                
        cap.release()
        cam_status.markdown(f"### Visualizer: Offline")
        active_feedback.markdown('<div class="feedback-card" style="border-left-color: #555;">Camera connection terminated.</div>', unsafe_allow_html=True)
