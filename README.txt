Contains: smooth criminal, radiohead, coldplay

Each folder contains an mp3 of the music video. You can find the original video by youtubing "Many Hands Play Piano" + folder name
Also contains opencv_ffmpeg340.dll - necessary dll for video processing

Smooth criminal and radiohead contain:
	HSV.mid, Hull.mid, back_mog.mid - generated midi files from final_HSV.py, final_hull.py, bad.py, respectively
	hsv.wav, hull.wav, bad.wav - Above files converted to wave file using TiMidity++ 
	bad/hsv/hull/original.txt - FFT information extracted from wav files using Audacity, 8192 points
	find_background.py - weighted mean code for finding background, saves bg as "background.png"
	midi_compare.py - code for norm-diff-FFT process. Needs to be run from IDE. Outputs "hullNorm", "badNorm", "hsvNorm".

coldplay is unfinished, WIP. Not used in final report.
	