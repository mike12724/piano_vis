import numpy as np
import cv2

c = cv2.VideoCapture('smooth2.avi')
ret, frame = c.read()

f = 0
avg1 = np.float32(frame)
ret,frame = c.read()
while ret == True:
    f += 1
    if f % 30 == 0:
        print f/30
    cv2.accumulateWeighted(frame,avg1,0.1)
    ret,frame = c.read()

res = cv2.convertScaleAbs(avg1)
cv2.imwrite('background.png',res)
cv2.destroyAllWindows()
c.release()


