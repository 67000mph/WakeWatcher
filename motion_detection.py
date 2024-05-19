import cv2
import math
import mediapipe as mp
import time

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose


def check_jumping_jack(landmarks, status_jumping_jack, cTime, reset_Time_jumping_jack):
    if (cTime - reset_Time_jumping_jack) > 3:
        status_jumping_jack = 0
        reset_Time_jumping_jack = cTime
    # Ausgangsposition: Beine zusammen, Arme neben dem Körper
    if (
        status_jumping_jack == 0
        and landmarks[12].y < landmarks[14].y
        and landmarks[11].y < landmarks[13].y
        and landmarks[26].x >= landmarks[12].x
        and landmarks[25].x <= landmarks[11].x
        and landmarks[16].y > landmarks[14].y
        and landmarks[15].y > landmarks[13].y
    ):
        status_jumping_jack = 1
        reset_Time_jumping_jack = cTime
    # Arme über dem Kopf, Beine auseinander
    if (
        status_jumping_jack == 1
        and landmarks[12].y > landmarks[14].y
        and landmarks[11].y > landmarks[13].y
        and landmarks[26].x <= landmarks[12].x
        and landmarks[25].x >= landmarks[11].x
        and landmarks[16].y < landmarks[14].y
        and landmarks[15].y < landmarks[13].y
    ):
        status_jumping_jack = 0
        return True, status_jumping_jack, reset_Time_jumping_jack
    return False, status_jumping_jack, reset_Time_jumping_jack


def check_push_up(landmarks, status_push_up, cTime, reset_Time_push_up):
    if (cTime - reset_Time_push_up) > 3:
        status_push_up = 0
        reset_Time_push_up = cTime
        # print("Reset")
    # Ausgangsposition: Arme gestreckt
    if (
        status_push_up == 0
        and landmarks[14].y > landmarks[12].y
        and landmarks[13].y > landmarks[11].y
        and landmarks[16].y > landmarks[14].y
        and landmarks[15].y > landmarks[13].y
    ):
        status_push_up = 1
        reset_Time_push_up = cTime
    # im Liegestütz: Ellebogen höher als die Schultern
    if (
        status_push_up == 1
        and landmarks[14].y <= landmarks[12].y
        and landmarks[13].y <= landmarks[11].y
        and landmarks[16].y > landmarks[14].y
        and landmarks[15].y > landmarks[13].y
    ):
        status_push_up = 2
        reset_Time_push_up = cTime
    # wieder in Ausgangspostion
    if (
        status_push_up == 2
        and landmarks[14].y > landmarks[12].y
        and landmarks[13].y > landmarks[11].y
        and landmarks[24].y > landmarks[12].y
        and landmarks[23].y > landmarks[11].y
        and landmarks[16].y > landmarks[14].y
        and landmarks[15].y > landmarks[13].y
    ):
        status_push_up = 0
        return True, status_push_up, reset_Time_push_up
    return False, status_push_up, reset_Time_push_up


def calculate_angle(x1, y1, x2, y2):
    dy = y2 - y1
    dx = x2 - x1
    angle_in_radians = math.atan2(dy, dx)
    angle_in_degrees = math.degrees(angle_in_radians)
    return angle_in_degrees


def angle_between_three_points(x1, y1, x2, y2, x3, y3):
    a = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    b = math.sqrt((x3 - x2) ** 2 + (y3 - y2) ** 2)
    c = math.sqrt((x3 - x1) ** 2 + (y3 - y1) ** 2)
    # Calculate the angle using the law of cosines
    angle_rad = math.acos((a**2 + b**2 - c**2) / (2 * a * b))
    angle = math.degrees(angle_rad)
    return angle


def distance_between_points(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# def check_wave(landmarks,status_wave):
#     if landmarks[20].y < landmarks[12].y:
#         if status_wave == 0 and 110 < calculate_angle(landmarks[20].x, landmarks[20].y, landmarks[14].x, landmarks[14].y) < 160:
#             status_wave = 1
#         if status_wave == 1 and 70 < calculate_angle(landmarks[20].x, landmarks[20].y, landmarks[14].x, landmarks[14].y) < 110:
#             status_wave = 2
#         if status_wave == 2 and 0 < calculate_angle(landmarks[20].x, landmarks[20].y, landmarks[14].x, landmarks[14].y) < 60:
#             status_wave = 3
#     return status_wave

# For webcam input:
wCam, hCam = 2000, 2000
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
status_wave = 0
count_hampel = 0
elbow_higher = False

status_jumping_jack = 0
reset_Time_jumping_jack = 0
count_jumping_jack = 0
status_push_up = 0
reset_Time_push_up = 0
count_push_up = 0

if __name__ == "__main__":
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            cTime = time.time()  #!!!!!
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image)

            # Check if the user is waving
            if hasattr(results.pose_landmarks, "landmark"):
                if len(results.pose_landmarks.landmark) != 0:
                    jumping_jack, status_jumping_jack, reset_Time_jumping_jack = (
                        check_jumping_jack(
                            results.pose_landmarks.landmark,
                            status_jumping_jack,
                            cTime,
                            reset_Time_jumping_jack,
                        )
                    )
                    if jumping_jack:
                        count_jumping_jack += 1
                        print(f"Anzahl Hampelmann {count_jumping_jack}")

                    push_up, status_push_up, reset_Time_push_up = check_push_up(
                        results.pose_landmarks.landmark,
                        status_push_up,
                        cTime,
                        reset_Time_push_up,
                    )
                    if push_up:
                        count_push_up += 1
                        print(f"Anzahl Liegestuetze {count_push_up}")

            # Draw the pose annotation on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
            )
            # Flip the image horizontally for a selfie-view display.
            cv2.imshow("MediaPipe Pose", cv2.flip(image, 1))
            if cv2.waitKey(5) & 0xFF == 27:
                break

    cap.release()
