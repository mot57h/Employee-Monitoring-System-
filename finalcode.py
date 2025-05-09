import cv2
import time
import dlib
import smtplib
import numpy as np
from email.message import EmailMessage
from ultralytics import YOLO
from datetime import datetime, timedelta
from scipy.spatial import distance as dist

# Load YOLOv8 Model
model = YOLO("yolov8n.pt")

# Load Dlib Face Detector and Landmark Predictor
face_detector = dlib.get_frontal_face_detector()
landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Email Credentials
EMAIL_ADDRESS = "mo579hit@gmail.com"
EMAIL_PASSWORD = "khep qsxo pnom rntw"
OWNER_EMAIL = "mo579hit@gmail.com"


login_time = "15:00"
logoff_time = "18:00"
login_deadline = (datetime.strptime(login_time, "%H:%M") + timedelta(minutes=15)).strftime("%H:%M")
logged_in = False
logged_off = False
late_alert_sent = False

# Warning Counters
warning_count = 0
warning_threshold = 2  
previous_warning = None  
warning_start_time = None  
warning_duration_threshold = 3
face_not_visible_start = None  

# Eye Blink Detection Parameters
EYE_AR_THRESHOLD = 0.25  
EYE_AR_CONSEC_FRAMES = 20  
closed_eyes_frame_count = 0  

frame_skip = 5  # Process every 5th frame
frame_count = 0

def eye_aspect_ratio(eye):
    """Calculate Eye Aspect Ratio (EAR) to detect closed eyes."""
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def send_email_alert(subject, body, image_path=None):
    """Sends an email with an alert and an attached image."""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD or not OWNER_EMAIL:
        return  
    
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = OWNER_EMAIL
    msg.set_content(body)
    
    if image_path:  # Attach image only if provided
        try:
            with open(image_path, "rb") as img:
                msg.add_attachment(img.read(), maintype="image", subtype="jpeg", filename="alert.jpg")
        except FileNotFoundError:
            print(f"Warning: Image file '{image_path}' not found. Sending email without attachment.")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Failed to send email: {e}")

    # with open(image_path, "rb") as img:
    #     msg.add_attachment(img.read(), maintype="image", subtype="jpeg", filename="alert.jpg")
    
    # with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    #     server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)        
    #     server.send_message(msg)

# Open Webcam
cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % frame_skip != 0:
            continue

        current_time = datetime.now().strftime("%H:%M")
        
        if not logged_in and current_time >= login_time:
            logged_in = True
            send_email_alert("Login Alert", f"Employee logged in at {current_time}.")

        # if not late_alert_sent and current_time > login_deadline:
        #     late_alert_sent = True
        #     send_email_alert("Late Login Alert", f"Employee logged in late by {current_time}.")

        if not late_alert_sent and current_time > login_deadline:
            late_alert_sent = True
            
            # Convert login time and actual login time to datetime objects
            actual_login_time = datetime.strptime(current_time, "%H:%M")
            expected_login_time = datetime.strptime(login_time, "%H:%M")

            # Calculate delay in minutes
            delay_minutes = int((actual_login_time - expected_login_time).total_seconds() // 60)
            
            send_email_alert("Late Login Alert", f"Employee logged in {delay_minutes} minutes late at {current_time}.")


        if not logged_off and current_time >= logoff_time:
            logged_off = True
            send_email_alert("Logoff Alert", f"Employee has not logged off by {logoff_time}.")


        results = model(frame)
        detected_classes = [model.names[int(box.cls[0])] for box in results[0].boxes]
        
        person_detected = False
        phone_detected = False
        sleeping_detected = False
        face_visible = False
        
        for obj in detected_classes:
            if obj == "person":
                person_detected = True
            elif obj == "cell phone":
                phone_detected = True
            elif obj in ["bed", "couch"]:
                sleeping_detected = True
        
        # **Check for Eye Closure (Sleeping Detection)**
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector(gray)
        
        sleeping_detected = False

        for face in faces:
            face_visible = True
            landmarks = landmark_predictor(gray, face)

            # for n in range(0, 68):
            #     x = landmarks.part(n).x
            #     y = landmarks.part(n).y
            #     cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
            
            left_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)]
            right_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)]
            
            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)
            avg_ear = (left_ear + right_ear) / 2.0

            if avg_ear < EYE_AR_THRESHOLD:
                closed_eyes_frame_count += 1
            else:
                closed_eyes_frame_count = 0

            if closed_eyes_frame_count >= EYE_AR_CONSEC_FRAMES:
                sleeping_detected = True
        
        # **Default message and border color (Green)**
        message = "All clear, person is working."
        message_color = (0, 255, 0)  
        border_color = (0, 255, 0)  
        warning_type = None
        
        # # **Detect and Show Warnings**
        # current_time = time.time()
        # if not face_visible:
        #     if face_not_visible_start is None:
        #         face_not_visible_start = current_time
        #     elif current_time - face_not_visible_start >= 3:
        #         message = "Warning: Not focused during work hours!!"
        #         warning_type = "Not focused"
        #         border_color = (0, 0, 255)
        #         message_color = (0, 0, 255)
        # else:
        #     face_not_visible_start = None

        if phone_detected:
            message = "Warning: Unauthorized phone usage detected!"
            warning_type = "Phone Usage"
            border_color = (0, 0, 255)
            message_color = (0, 0, 255)

        current_time = time.time()
        if sleeping_detected:
            message = "Warning: Sleeping detected! Keep your eyes open!"
            warning_type = "Sleeping"
            border_color = (0, 0, 255)
            message_color = (0, 0, 255)

        else:
            if not face_visible:
                if face_not_visible_start is None:
                    face_not_visible_start = current_time
                elif current_time - face_not_visible_start >= 3:
                    message = "Warning: Not focused during work hours!!"
                    warning_type = "Not focused"
                    border_color = (0, 0, 255)
                    message_color = (0, 0, 255)
            else:
                face_not_visible_start = None

        
        if not person_detected:
            message = "Warning: No person detected at the workstation!"
            warning_type = "No Person"
            border_color = (0, 0, 255)
            message_color = (0, 0, 255)

        text_size = cv2.getTextSize(message, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        text_x = (frame.shape[1] - text_size[0]) // 2
        text_y =  50  

        cv2.putText(frame, message, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, message_color, 2)
        cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), border_color, 15)

         #   **Track Warning Duration**
        current_time = time.time()
        if warning_type:
            if warning_type == previous_warning:
                if warning_start_time is None:
                    warning_start_time = current_time
                elif current_time - warning_start_time >= warning_duration_threshold:
                    warning_count += 1
                    warning_start_time = None  
            else:
                warning_start_time = current_time
                warning_count = 1
            previous_warning = warning_type
        else:
            warning_start_time = None
            warning_count = 0  
            previous_warning = None

            #**Send Email Alert with Timestamp**
        if warning_count >= warning_threshold:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            image_path = f"alert_{timestamp.replace(':', '-')}.jpg"  
            
            cv2.putText(frame, timestamp, (50, frame.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imwrite(image_path, frame)

            email_body = f"Alert: {message}\nTime: {timestamp}"
            send_email_alert("Work Monitoring Alert", email_body, image_path)

            warning_count = 0     

        cv2.imshow("Monitoring", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()