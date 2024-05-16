import cv2
import time
import math
import os
import HandTrackingModule as htm

def distance_between_points(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def count_fingers(landmarks_list):
    fingers_list = []
    if len(landmarks_list) != 0:

        #Check for thumb
        print(distance_between_points(landmarks_list[4][1], landmarks_list[4][2],landmarks_list[5][1],landmarks_list[5][2]))
        if (distance_between_points(landmarks_list[4][1], landmarks_list[4][2],landmarks_list[5][1],landmarks_list[5][2]) > 70) and (landmarks_list[7][2] > landmarks_list[8][2]):
            fingers_list.append(1)
            print("offene Hand")
        elif (landmarks_list[tipIds[0]][1] > landmarks_list[tipIds[0] - 1][1] or landmarks_list[tipIds[0]][1] < landmarks_list[tipIds[0] - 1][1]) and (landmarks_list[9][2] > landmarks_list[5][2]):
            fingers_list.append(1)
            print("Daumen")
        else:
            fingers_list.append(0)
        
        #Check for 4 fingers
        for id in range(1, 5):
            if landmarks_list[tipIds[id]][2] < landmarks_list[tipIds[id] - 2][2]:
                fingers_list.append(1)
            else:
                fingers_list.append(0)

    fingers_count = fingers_list.count(1)
    return fingers_count

# wCam, hCam = 1000, 1000

# cap = cv2.VideoCapture(0)
# cap.set(3, wCam)
# cap.set(4, hCam)

# pTime = 0

# detector = htm.handDetector(detectionCon=1)

# tipIds = [4, 8, 12, 16, 20]
# sum = 0

# while True:
#     success, img = cap.read()
#     img = detector.findHands(img)
#     landmarks_list = detector.findPosition(img, draw=False)
#     landmarks_list_2 = detector.findPosition(img, handNo=1, draw=False )

#     finger_count1 = count_fingers(landmarks_list)
#     finger_count2 = count_fingers(landmarks_list_2)


#     # print("1: " + str(len(landmarks_list)) + " 2: " + str(len(landmarks_list_2)))
#     # print("1: " + str(finger_count1) + " 2: " + str(finger_count2))
    
#     fingers_count = finger_count1 + finger_count2
        
#     #display count inside the frame      
#     cv2.rectangle(img, (20, 225), (170, 425), (169, 169, 169), cv2.FILLED)
#     cv2.putText(img, str(fingers_count), (60, 375), cv2.FONT_HERSHEY_PLAIN,
#                 8, (0, 0, 128), 20)

#     cTime = time.time()
#     fps = 1 / (cTime - pTime)
#     pTime = cTime

#     #display FPS inside the frame
#     cv2.putText(img, f'Frames per second =: {int(fps)}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
#                 1, (0, 0, 128), 3)

#     cv2.imshow("Image", img)

#     if cv2.waitKey(1) == 13:
#         break

#     cv2.waitKey(1)
