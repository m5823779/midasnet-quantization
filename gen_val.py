from os import listdir
from os.path import isfile, join

import os
dir = os.path.abspath(os.getcwd())
files = []
for f in listdir('./ReDWeb_V1/Imgs/'):
    rgb_path = 'Imgs/'
    depth_path = 'RDs/'
    depth_img_filename = f.split('.')[0] + '.png'
    line = os.path.join(rgb_path, f) + ' ' + os.path.join(depth_path, depth_img_filename) + '\n'
    files.append(line)

path = 'ReDWeb_validation_360.txt'
f = open(path, 'w')
f.writelines(files)
f.close()

