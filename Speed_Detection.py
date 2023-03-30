import os
import cv2
import numpy as np
import dlib
import time
from datetime import datetime

#Haar's Cascade Classifier
carCascade = cv2.CascadeClassifier(r"")

#Video Capture
video = cv2.VideoCapture(r"")

#start and End Trackers
start = {} 
end = {}

#Intialising Values
width = 1000 
height = 800 
crop = 240 
m1 = 100 
m2 = 300 
Gap = 15 
FPS = 3 
Speed_Limit = 25


#blacking out the unecessary area to get a better result
def blackout(image):
    x = 300
    y = 280 
    t1 = np.array( [[0,0], [x,0], [0,y]] )
    t2 = np.array( [[width,0], [width-x,0], [width,y]] )
    cv2.drawContours(image, [t1], 0, (0,0,0), -1)
    cv2.drawContours(image, [t2], 0, (0,0,0), -1)
    return image

#Estimating the speed
def EstimateVelocity(Curr_Vno):
    time_diff = end[Curr_Vno] - start[Curr_Vno] 
    speed = round(Gap / time_diff * FPS * 3.6 , 2)
    return speed

#Save Images of Overspeeding Vehicles
def SaveImage(image):
    imagename = datetime.today().now().strftime("%d-%m-%Y-%H-%M-%S-%f")
    directory = 'speed_limit_violated_vehicles/' + imagename + '.png'
    cv2.imwrite(directory,image)

#Delete Car IDs to prevent reassignment of vehicle No 
def Delete_Car_IDs(image, Track):
    DeleteVehicleNo = []
    for Curr_Vno in Track.keys():
        tracked = Track[Curr_Vno].update(image)
        if tracked < 7:
                DeleteVehicleNo.append(Curr_Vno)
    for Curr_Vno in DeleteVehicleNo:
        Track.pop(Curr_Vno, None)
    
#Tracking Vehicles
def TrackObjects():
    
    Frames = 0 #Frame Count
    VehicleNo = 1 #Vehicle Count
    Track = {} #Tracker

    while True:
        
        rc, image = video.read()
        if type(image) == type(None):
            break

        Frame_Time = time.time()
        image = cv2.resize(image, (width, height))[crop:720,0:1280]
        Blackout_Image = blackout(image)

        #drawing markers
        #cv2.line(Blackout_Image,(0,m1),(1280,m1),(0,0,255),2)
        #cv2.line(Blackout_Image,(0,m2),(1280,m2),(0,0,255),2)

        Frames += 1
        Delete_Car_IDs(image, Track)

        if (Frames % 60 == 0):

            #Grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            #Applying Haar's Cascade Classifier
            cars = carCascade.detectMultiScale(gray, 1.1, 13, 18, (24, 24)) 

            for (x, y, w, h) in cars:
                x = int(x)
                y = int(y)
                w = int(w)
                h = int(h)
                xbar = x + 0.5*w
                ybar = y + 0.5*h
                Matching = None

                for Curr_Vno in Track.keys():
                    Position = Track[Curr_Vno].get_position()
                    tx = int(Position.left())
                    ty = int(Position.top())
                    tw = int(Position.width())
                    th = int(Position.height())
                    txbar = tx + 0.5 * tw
                    tybar = ty + 0.5 * th

                    if ((tx <= xbar <= (tx + tw)) and (ty <= ybar <= (ty + th)) and (x <= txbar <= (x + w)) and (y <= tybar <= (y + h))):
                        Matching = Curr_Vno

                if Matching is None:
                    tracker = dlib.correlation_tracker()
                    tracker.start_track(image, dlib.rectangle(x, y, x + w, y + h))
                    Track[VehicleNo] = tracker
                    VehicleNo += 1


        for Curr_Vno in Track.keys():
            
            Position = Track[Curr_Vno].get_position()
            tx = int(Position.left())
            ty = int(Position.top())
            tw = int(Position.width())
            th = int(Position.height())

            cv2.rectangle(Blackout_Image, (tx, ty), (tx + tw, ty + th), (255,0,0), 2)
            cv2.putText(Blackout_Image, str(Curr_Vno), (tx,ty-5), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 1)

            if Curr_Vno not in start and m2 > ty+th > m1 and ty < m1:
                start[Curr_Vno] = Frame_Time

            elif Curr_Vno in start and Curr_Vno not in end and m2 < ty+th:
                end[Curr_Vno] = Frame_Time
                speed = EstimateVelocity(Curr_Vno)
                status = 'Vehicle No. : ' + str(Curr_Vno) + 'Speed : ' + str(speed) + 'kmph'
                if speed > Speed_Limit:
                    print(status + ' - Overspeeding')
                    SaveImage(image[ty:ty+th, tx:tx+tw])
                else:
                    print(status)
                    
        #press ESC to Exit
        cv2.imshow('Speed Tracking', Blackout_Image)
        if cv2.waitKey(33) == 27:
            break
        
    cv2.destroyAllWindows()

if __name__ == '__main__':
    if not os.path.exists('speed_limit_violated_vehicles/'):
        os.makedirs('speed_limit_violated_vehicles/')
    print('Speed Limit Set at 25 Kmph')
    TrackObjects()
