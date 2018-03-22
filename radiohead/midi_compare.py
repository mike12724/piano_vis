import numpy as np

o = []
m = []
b = []
h = []

with open('original.txt','r') as original:
    f = original.readline()
    for line in original:
        a = line.find('\t')
        if float(line[0:a]) > 4200:
            break
        o.append(float(line[a+1:-1]))

with open('hull.txt','r') as original:
    f = original.readline()
    for line in original:
        a = line.find('\t')
        if float(line[0:a]) > 4200:
            break
        m.append(float(line[a+1:-1]))

with open('bad.txt','r') as original:
    f = original.readline()
    for line in original:
        a = line.find('\t')
        if float(line[0:a]) > 4200:
            break
        b.append(float(line[a+1:-1]))

with open('hsv.txt','r') as original:
    f = original.readline()
    for line in original:
        a = line.find('\t')
        if float(line[0:a]) > 4200:
            break
        h.append(float(line[a+1:-1]))

o = np.array(o)
m = np.array(m)
b = np.array(b)
h = np.array(h)

hullNorm = np.linalg.norm(o-m)
badNorm = np.linalg.norm(o-b)
hsvNorm = np.linalg.norm(o-h)
