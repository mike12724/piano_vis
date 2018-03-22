import numpy as np
import cv2
from collections import Counter
from midiutil import MIDIFile

def identifyBackground(frame,bg):
    gray_blur = bg
    edges = cv2.Canny(gray_blur,270,440)

    top = bottom = left = right = 0 #define piano border
    i = 0
    while sum(edges[i]) == 0:
        i += 1
    top = i+1
    while sum(edges[i]) != 0:
        i+=1
    bottom = i-1
    i = 0
    while edges[top+5,i] == 0:
        i+=1
    left = i
    i = -1
    while edges[top+5,-i] == 0:
        i -= 1
    right = edges.shape[1]+i

    #set up black keys
    black_key_bottom = bottom-10
    while sum(edges[black_key_bottom]) < 5000:
        black_key_bottom -= 1
    black_key_bottom += 1
    black_key_y_loc = top+(black_key_bottom-top)/2
    counter = 0
    black_key_borders = []
    key_loc = []
    for i in range(edges.shape[1]):
        if edges[black_key_y_loc,i] == 255:
            if counter == 0:
                counter += 1
                continue
            if counter%2 == 1: #odd aka left border
                counter += 1
                key_loc.append(i)
            else:
                counter += 1
                key_loc.append(i)
                black_key_borders.append(key_loc)
                key_loc = []
    black_key_borders = np.array(black_key_borders)
    for i in range(len(black_key_borders)):
        frame = cv2.rectangle(frame,(black_key_borders[i,0],black_key_bottom),(black_key_borders[i,1],top),(0,255,0),3)

    #set up white keys by making a different edge detection 
    edges_white = cv2.Canny(gray_blur,30,50)
    white_key_borders = []
    white_key_y_loc = bottom - (bottom-black_key_bottom)/2
    for i in range(edges_white.shape[1]):
        if edges_white[white_key_y_loc,i] != 0:
            white_key_borders.append(i)

    #remove doubles from white keys
    for i in range(len(white_key_borders)/2):
        del white_key_borders[i]
      
    for i in range(len(white_key_borders)):
        frame = cv2.line(frame,(white_key_borders[i],bottom),(white_key_borders[i],top), (255,0,0),2)
    white_key_borders = np.array(white_key_borders)
    #cv2.imshow('piano segmentation',frame)

    return top, bottom, left, right, white_key_borders, black_key_borders

def findNotes(frame,kernel,kernel_keys, bottom, top,bg, white_key_borders):

    gr = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.blur(gr,(3,3))

    ####### Mask operations (MOST IMPORTANT)################
    fgmask = cv2.absdiff(bg,gr)
    fgmask = cv2.blur(fgmask,(3,3))
    fgmask = cv2.inRange(fgmask,60,255) #50 is toooo low!
    fgmask = cv2.morphologyEx(fgmask,cv2.MORPH_OPEN,kernel_keys)
    
    #find hands by color
    lower = np.array([60,70,110])
    upper = np.array([140,160,215])
    mask = cv2.inRange(frame,lower,upper)
    mask = cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernel)
    im2, contours, hier = cv2.findContours(mask,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
    if len(contours) == 0:
        return 1,1

    #using each hand's convex hull, we find the x values that it spans   
    potential_keys_range = []
    for contour in contours:
        if cv2.contourArea(contour) < 400:
            continue
        hull = cv2.convexHull(contour)
        hullpts = np.reshape(hull,(-2,2))
        potential_keys_range.append([min(hullpts[:,0]),max(hullpts[:,0])])
        
        cv2.drawContours(frame,[hull],0,(0,255,0),2)
        cv2.drawContours(fgmask,[hullpts],0,(0,0,0),-1)
 
    #Set areas of interest to be only around hands
    for j in range(1280):
        b = 0
        for key_range in potential_keys_range:
            if j >= key_range[0]-15 and j <= key_range[1]+15:
                b= 1
                break
        if b == 1:
            continue
        else: #column not in key range
            fgmask[:,j] = 0

    #examine top 1/2 for keypress
    key_press_bin = []
    for i in range(bottom-top):
        for j in range(1280):
            if fgmask[top+i,j] and j < white_key_borders[-1]:
                key_press_bin.append(np.where(white_key_borders-j>0)[0][0])
    notes_pressed = Counter(key_press_bin)
    volumes = notes_pressed
    notes_pressed_f = [k for k,v in notes_pressed.iteritems()]

##    cv2.imshow('orig',frame)
##    cv2.waitKey()
          
    return notes_pressed_f, volumes


def createMidi(notes_per_frame,volumes_per_frame,fps):
    #create "key location to MIDI degree" dictionary
    row_1_degrees = [24,26,28,29,31,33,35]
    row_1_bins = [i+2 for i in range(7)]
    white_bin_to_degree = {}
    for j in range(7):
        for i in range(7):
            white_bin_to_degree[row_1_bins[i] + 7*j] = row_1_degrees[i] + 12*j
    white_bin_to_degree[0] = 21
    white_bin_to_degree[1] = 23
    white_bin_to_degree[51] = 108

    #process notes to figure out how long notes are being played
    whites_in_time = []
    for i in range(52):
        temp = []
        length = 0
        isOn = 0
        hit_time = 0
        for j,frame in enumerate(notes_per_frame):
            if isOn:
                if i in frame:
                    length += 1
                else:
                    temp.append((hit_time,length,volume))
                    length = 0
                    hit_time = 0
                    isOn = 0
            else:
                if i in frame:
                    volume = min(40+4*volumes_per_frame[j][i],127)
                    hit_time = j
                    length += 1
                    isOn = 1
                    
        whites_in_time.append(temp)

    #Create the music!!!
    track    = 0
    channel  = 0
    time     = 0   # In beats
    tempo    = 60*fps  # In BPM; tested by hand
    volume   = 100 # 0-127, as per the MIDI standard

    myMIDI = MIDIFile(1)
    myMIDI.addTempo(track,time,tempo)

    for i in range(52):
        notes = whites_in_time[i]
        for note in notes:
            myMIDI.addNote(track,channel,white_bin_to_degree[i],note[0],note[1],note[2])

    with open("Hull.mid","wb") as output_file:
        myMIDI.writeFile(output_file)

if __name__ == "__main__":    
    cap = cv2.VideoCapture('radio2.avi')
    ret, frame = cap.read()
    bg = cv2.imread('background.png')
    bg = cv2.cvtColor(bg,cv2.COLOR_BGR2GRAY)
    bg = cv2.blur(bg,(3,3))
    t,b,l,r, wkb, bkb = identifyBackground(frame,bg)
    ret, frame = cap.read()

    #Define morphology kernels for masking operations
    kernel_hands = np.ones((3,3),np.uint8)
    kernel_keys = np.ones((6,1),np.uint8)
    seconds_counter = 0
    notes_per_frame = []
    volumes_per_frame = []
    while ret == True:
        seconds_counter += 1
        if seconds_counter%30 == 0:
            print seconds_counter/30
        notes_pressed, volumes = findNotes(frame,kernel_hands,kernel_keys, b, t,bg,wkb)
        if notes_pressed == volumes and volumes == 1:
            ret, frame = cap.read()   
            continue
        notes_per_frame.append(notes_pressed)
        volumes_per_frame.append(volumes)
        ret, frame = cap.read()    
    cap.release()
    cv2.destroyAllWindows()

    createMidi(notes_per_frame,volumes_per_frame,60) #FPS of video
    
            
    



