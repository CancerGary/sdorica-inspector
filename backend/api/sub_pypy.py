import ETC2ImagePlugin
import time
from PIL import Image
import pickle
import sys

if __name__ == '__main__':
    task_info = pickle.load(open(sys.argv[1] + '.pypy.pkl', 'rb'))
    task_info[2] = open(sys.argv[1] + '.pypy.data', 'rb').read()
    i = Image.frombytes(*task_info).transpose(Image.FLIP_TOP_BOTTOM)
    i.save(sys.argv[1], 'png')
