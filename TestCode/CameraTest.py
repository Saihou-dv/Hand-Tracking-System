import cv2

#default cam
cam= cv2.VideoCapture(0)

while True:
    ret, frame=cam.read()
    if not ret:
        break
    
    cv2.imshow("Camera Test", frame)
    
    if cv2.waitKey(1) & 0xFF == 27:
        break
    

cam.release()
cv2.destroyAllWindows()