import numpy as np
import cv2

c = cv2.VideoCapture('coldplay.avi')
for i in range(235*30):
    ret,frame = c.read()

print ret
res = cv2.convertScaleAbs(frame)
cv2.imwrite('background.png',res)
cv2.destroyAllWindows()
c.release()


