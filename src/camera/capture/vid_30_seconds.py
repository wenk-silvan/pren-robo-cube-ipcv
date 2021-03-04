import time
import picamera
import os,datetime
# os.getcwd() = current working dir
mydir = os.path.join(os.getcwd(), "video", datetime.datetime.now().strftime('%Y-m-d_%H-%M-%S'))
os.makedirs(mydir)

camera = picamera.PiCamera()
camera.resolution = (640,480)

duration = 30

print('start Vide recording for ' + str(duration) + ' seconds')
camera.start_recording(mydir + '/myVid.h264')
camera.wait_recording(duration)
camera.stop_recording()
print('recording done')
