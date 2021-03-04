import time
import picamera
import os,datetime

mydir = os.path.join('/mnt/data/', "pics", datetime.datetime.now().strftime('%Y-m-d_%H-%M-%S'))
os.makedirs(mydir)

camera = picamera.PiCamera()
camera.resolution = (1280,960)
time.sleep(5)
i = 1
for filename in camera.capture_continuous(mydir + '/img{counter:03d}.jpg'):
    print('Captured %s' % filename)
    i += 1
    if i > 30:
        break
