
import enum
import re
import cv2
import mediapipe as mp
import mediapipe.python.solutions.hands
import time


smoothed_all_handlandmarks= []
previous_landmarks =None
mp_hands = mp.solutions.hands
mp_draw= mp.solutions.drawing_utils
#Intitalise camera

Cam = cv2.VideoCapture(0)



def getCorrectCamera():
    for camera in cv2.VideoCaptureAPIs:
        if cv2.VideoCapture(camera).isOpened():
            Cam= cv2.VideoCapture(camera)
            break

#People May not have the camera on the first index "0" open
if not Cam.isOpened():
    print("Camera not accessible")
    getCorrectCamera()    
    
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)


        
def HandCoordinateTester(results):
    for hand_landmarks in results.multi_hand_landmarks or []:
         for id, lm in enumerate(hand_landmarks.landmark):
             h, w, c = frame.shape
             cx, cy = int(lm.x * w), int(lm.y * h)
             #print(id, cx, cy)
             if id == 8:
                 cv2.circle(frame, (cx, cy), 15, (255, 0, 0), cv2.FILLED)
                 cv2.putText(frame, str(cx)+":"+str(cy), (cx, cy-20), cv2.FONT_HERSHEY_PLAIN,
                             1, (255, 0, 255), 2)
             if id == 0:
                 cv2.circle(frame, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                 cv2.putText(frame, str(cx)+":"+str(cy), (cx, cy-20), cv2.FONT_HERSHEY_PLAIN,
                             1, (255, 0, 255), 2)


def StoreHandLandmarks(results):
    
    allhandpoints= []
    for hand_landmarks in results.multi_hand_landmarks or []:
        handpoints =[]
        h, w, c = frame.shape
        for id, lm in enumerate(hand_landmarks.landmark):
             
             cx, cy = int(lm.x * w), int(lm.y * h)
             handpoints.append((cx,cy))
             allhandpoints.append(handpoints)
    
    return allhandpoints

def HandStabiliser(results):
    #how much i trust the previous frame 
    alpha =0.17
    global previous_landmarks
    global smoothed_all_handlandmarks
    
    smoothed_all_handlandmarks=[]
    if results.multi_hand_landmarks:
        all_current_hands = StoreHandLandmarks(results)
        for handindex, current_landmarks in enumerate(all_current_hands):
            if previous_landmarks is not None and handindex<len(previous_landmarks):
              smoothed_landmarks=[]
              for i in range(21):
                prev = previous_landmarks[handindex][i]
                curr = current_landmarks[i]
                smoothed = (int(prev[0]* alpha +curr[0]*(1-alpha)),int(prev[1]* alpha +curr[1]*(1-alpha)))
                smoothed_landmarks.append(smoothed)
            else:
              smoothed_landmarks = current_landmarks
        
            smoothed_all_handlandmarks.append(smoothed_landmarks)
            for cx,cy in smoothed_landmarks:
                cv2.circle(frame, (cx, cy), 4, (0, 255, 0), cv2.FILLED)
        
        previous_landmarks = all_current_hands.copy()
            

def HandDrawer(results):
    if results.multi_hand_landmarks:
         for hand_landmarks in results.multi_hand_landmarks:
             mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

def GestureDetection(SmoothedResults,frame1):
    if not SmoothedResults:
        return
    h, w, _ = frame1.shape
    
    totalx=0
    total_y=0
    #List Holding the Indexes of all fingertips
    fingertips =[8,12,16,20]
    for handindex, smlk in enumerate(SmoothedResults):
        wristx,wristy = smlk[0]
        
        if wristx <=0 or wristy<=0 or wristx >=w or wristy>=h:
            continue
        for index in fingertips:
            cx,cy = smlk[index]
            #relative_x = cx-wristx
            relative_y = cy -wristy
            
            #totalx += relative_x
            total_y += relative_y
            cv2.arrowedLine(frame1,(int(wristx),int(wristy)),(int(cx),int(cy)),(255,255,255),2,tipLength=.3)
        
        avg_h = int(total_y/4) 
        if avg_h<-1500:
            print("open")
        else:
            print("Closed")
        cv2.circle(frame1,(wristx,wristy),5,(255,255,255),cv2.FILLED)
        #cv2.putText(frame, f"{avg_h}", (wristx, wristy+20), cv2.FONT_HERSHEY_COMPLEX,
       #                      2, (255, 255, 255), 1)
   

#-------------------------------------------------------#
#Main Code            
while Cam.isOpened():
     ret, frame = Cam.read()
     frame =cv2.flip(frame,1)
     if not ret:
         break
     
     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
 
     results = hands.process(rgb_frame)
     #HandDrawer(results)
     if results.multi_hand_landmarks:
              HandStabiliser(results)
              GestureDetection(smoothed_all_handlandmarks,frame)

    
     cv2.imshow("Hand Tracking", frame)     
     if cv2.waitKey(1) & 0xFF == 27:
         break
     
Cam.release()
cv2.destroyAllWindows()
     
     