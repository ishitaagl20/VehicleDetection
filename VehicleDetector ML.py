import numpy as np
import cv2

def detectCars(filename):
  
  casc = cv2.CascadeClassifier(r"HaarCascadeClassifier.xml")

  vc = cv2.VideoCapture(r"")

  if vc.isOpened():
      val , frame = vc.read()
  else:
      val = False


  while val:
    val, frame = vc.read()
    frameHeight, frameWidth, depth = frame.shape
    
    #frame = cv2.resize(frame, ( 1000,  1000 ))
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    cars = casc.detectMultiScale(frame, 1.3, 3)

    for (x, y, w, h) in cars:
      cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
    crop_img = frame[y:y+h,x:x+w]
    cv2.imshow("Result",frame)

    if cv2.waitKey(1) == 27:
        break

  vc.release()


detectCars(cv2.VideoCapture)
