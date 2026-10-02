import cv2
import time
import winsound
from datetime import datetime


# ============================================================
# SAFE NIGHT-TIME NAVIGATION ASSISTANT
# Improved Drowsiness Detection
# ============================================================


# ============================================================
# LOAD MODELS
# ============================================================

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_eye.xml"
)


if face_cascade.empty():
    print("ERROR: Face detection model could not be loaded.")
    exit()

if eye_cascade.empty():
    print("ERROR: Eye detection model could not be loaded.")
    exit()


# ============================================================
# CAMERA
# ============================================================

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Camera could not be opened.")
    exit()


# ============================================================
# SETTINGS
# ============================================================

# Eyes must remain undetected this long
# before drowsiness is declared.
DROWSY_TIME = 2.0

# Minimum time between alarms
ALARM_COOLDOWN = 2.0

# Number of frames required before considering
# the eyes definitely closed.
CLOSED_FRAME_THRESHOLD = 5


# ============================================================
# VARIABLES
# ============================================================

eyes_closed_start = None

last_alarm_time = 0

alert_logged = False

closed_frame_count = 0


# ============================================================
# LOG FILE
# ============================================================

LOG_FILE = "drowsiness_log.txt"


def write_log(event):

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(LOG_FILE, "a") as file:

        file.write(
            f"{current_time} - {event}\n"
        )

    print(
        f"[LOG] {current_time} - {event}"
    )


# ============================================================
# START SESSION
# ============================================================

write_log(
    "Improved monitoring session started"
)


print("==============================================")
print(" SAFE NIGHT-TIME NAVIGATION ASSISTANT")
print("==============================================")
print("Improved drowsiness detection started.")
print("Press Q to exit.")
print("")


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    ret, frame = camera.read()

    if not ret:

        print(
            "ERROR: Could not read camera frame."
        )

        break


    # Mirror camera
    frame = cv2.flip(
        frame,
        1
    )


    # Convert to grayscale
    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )


    # ========================================================
    # FACE DETECTION
    # ========================================================

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=5,
        minSize=(100, 100)
    )


    eyes_detected = False


    # ========================================================
    # PROCESS FACE
    # ========================================================

    for (x, y, w, h) in faces:

        # Draw face rectangle
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (255, 255, 255),
            2
        )


        # Face region
        face_gray = gray[
            y:y + h,
            x:x + w
        ]

        face_color = frame[
            y:y + h,
            x:x + w
        ]


        # ====================================================
        # EYE DETECTION
        # ====================================================

        eyes = eye_cascade.detectMultiScale(
            face_gray,
            scaleFactor=1.1,
            minNeighbors=6,
            minSize=(25, 25)
        )


        if len(eyes) > 0:

            eyes_detected = True


        # Draw eye rectangles
        for (ex, ey, ew, eh) in eyes:

            cv2.rectangle(
                face_color,
                (ex, ey),
                (ex + ew, ey + eh),
                (255, 255, 255),
                2
            )


    # ========================================================
    # IMPROVED DROWSINESS LOGIC
    # ========================================================

    if len(faces) == 0:

        status = "NO FACE DETECTED"
        status_color = (0, 165, 255)

        eyes_closed_start = None

        closed_frame_count = 0

        alert_logged = False


    elif eyes_detected:

        # Eyes visible
        status = "AWAKE"
        status_color = (0, 255, 0)

        eyes_closed_start = None

        closed_frame_count = 0

        alert_logged = False


    else:

        # Eyes not detected
        closed_frame_count += 1


        # Only begin timing after several
        # consecutive frames without eyes.
        if closed_frame_count >= CLOSED_FRAME_THRESHOLD:

            if eyes_closed_start is None:

                eyes_closed_start = time.time()


            closed_duration = (
                time.time()
                - eyes_closed_start
            )


            # =================================================
            # DROWSINESS ALERT
            # =================================================

            if closed_duration >= DROWSY_TIME:

                status = "DROWSINESS ALERT!"
                status_color = (0, 0, 255)


                # ---------------------------------------------
                # LOG ALERT
                # ---------------------------------------------

                if not alert_logged:

                    write_log(
                        "DROWSINESS ALERT DETECTED"
                    )

                    alert_logged = True


                # ---------------------------------------------
                # ALARM
                # ---------------------------------------------

                current_time = time.time()


                if (
                    current_time
                    - last_alarm_time
                    >= ALARM_COOLDOWN
                ):

                    winsound.Beep(
                        1000,
                        500
                    )

                    last_alarm_time = current_time


            else:

                status = "EYES CLOSED"
                status_color = (0, 165, 255)

        else:

            # Possible blink
            status = "BLINK / CHECKING"
            status_color = (0, 165, 255)


    # ========================================================
    # UI STATUS PANEL
    # ========================================================

    cv2.rectangle(
        frame,
        (10, 10),
        (440, 130),
        (25, 25, 25),
        -1
    )


    cv2.rectangle(
        frame,
        (10, 10),
        (440, 130),
        status_color,
        2
    )


    cv2.putText(
        frame,
        "DRIVER STATUS",
        (30, 42),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )


    cv2.putText(
        frame,
        status,
        (30, 82),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.72,
        status_color,
        2
    )


    # ========================================================
    # EYE CLOSURE TIMER
    # ========================================================

    if eyes_closed_start is not None:

        closed_time = (
            time.time()
            - eyes_closed_start
        )

        timer_text = (
            f"Eye closure: "
            f"{closed_time:.1f}s"
        )

        cv2.putText(
            frame,
            timer_text,
            (30, 112),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (220, 220, 220),
            1
        )


    # ========================================================
    # DRIVER MONITORING PANEL
    # ========================================================

    height, width = frame.shape[:2]

    panel_x = width - 275


    cv2.rectangle(
        frame,
        (panel_x, 15),
        (width - 15, 120),
        (25, 25, 25),
        -1
    )


    cv2.rectangle(
        frame,
        (panel_x, 15),
        (width - 15, 120),
        (255, 255, 255),
        1
    )


    cv2.putText(
        frame,
        "DRIVER MONITORING",
        (panel_x + 15, 42),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1
    )


    cv2.putText(
        frame,
        "Face: "
        + (
            "Detected"
            if len(faces) > 0
            else "Not Detected"
        ),
        (panel_x + 15, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (220, 220, 220),
        1
    )


    cv2.putText(
        frame,
        "Eyes: "
        + (
            "Detected"
            if eyes_detected
            else "Not Detected"
        ),
        (panel_x + 15, 95),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (220, 220, 220),
        1
    )


    # ========================================================
    # WARNING MESSAGE
    # ========================================================

    if status == "DROWSINESS ALERT!":

        cv2.putText(
            frame,
            "WARNING: DRIVER DROWSINESS DETECTED",
            (
                width // 2 - 235,
                height - 65
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            (0, 0, 255),
            2
        )


    # ========================================================
    # PROJECT TITLE
    # ========================================================

    cv2.rectangle(
        frame,
        (0, height - 45),
        (width, height),
        (20, 20, 20),
        -1
    )


    cv2.putText(
        frame,
        "SAFE NIGHT-TIME NAVIGATION ASSISTANT",
        (20, height - 18),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2
    )


    # ========================================================
    # SHOW WINDOW
    # ========================================================

    cv2.imshow(
        "Safe Night-Time Navigation Assistant",
        frame
    )


    # ========================================================
    # EXIT
    # ========================================================

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


# ============================================================
# CLEANUP
# ============================================================

camera.release()

cv2.destroyAllWindows()


write_log(
    "Improved monitoring session ended"
)


print("")
print(
    "Driver monitoring stopped."
)

print(
    "Log saved to:",
    LOG_FILE
)

print(
    "Safe Night-Time Navigation Assistant closed."
)