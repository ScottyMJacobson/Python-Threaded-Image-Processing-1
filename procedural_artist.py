# Scott Jacobson
# 9/17/14
# COMP50 Concurrant Programming

"""procedural_artist.py, a program that spawns threads that paint randomly 
    on a canvas"""

# The following synchronization is required among the threads:
# TODO: THIS

# -*- coding: utf-8 -*-
#! /usr/local/bin/python

import argparse
import sys
import threading
from PIL import Image

def paint(index):
    #grab a pixel at random
    #lock that pixel's assignerthing
    #check if it's owned by anyone
    #
    steps_taken = 0
    pixels_i_own = list()
    while steps_taken < max_steps:
        #take a step
        steps_taken+= 1

class RestrictedPixelMap:
    def __init__(self, pix_map, (width, height)):
        self.pix_map = pix_map
        self.width = width
        self.height = height
        self.lock_map = [[threading.Lock()]*width for i in range(height)]
    def draw_to_pixel (self, new_pixel, row, column):
        success = False
        self.lock_map[row][column].acquire()
        #acquire the lock to that pixel
        this_pixel = self.pix_map[row,column]
        if this_pixel == (255,255,255):
            this_pixel = new_pixel
            success = True
        self.lock_map[row][column].release()
        return success

def main():
    parser = argparse.ArgumentParser()

    canvas = Image.new('RGB', (512,512), color=(255,255,255))

    canvas_map = canvas.load()

    restricted_canvas = RestrictedPixelMap(canvas_map, canvas.size)

    restricted_canvas.draw_to_pixel((255,1,1), 10, 10)
    restricted_canvas.draw_to_pixel((255,1,1), 11, 11)
    restricted_canvas.draw_to_pixel((255,1,1), 12, 12)
    
    canvas.show()

if __name__ == '__main__':
    main()
