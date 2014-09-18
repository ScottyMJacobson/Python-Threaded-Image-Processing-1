# Scott Jacobson
# 9/17/14
# COMP50 Concurrant Programming

"""procedural_artist.py, a program that spawns threads that paint randomly 
    on a canvas"""

# -*- coding: utf-8 -*-
#! /usr/local/bin/python

import sys
import argparse
import random
import threading
from PIL import Image

class RestrictedPixelMap:
    """A pixel map whose pixel access is regulated by a parallel map of locks"""
    def __init__(self, pix_map, (width, height)):
        self.pix_map = pix_map
        self.width = width
        self.height = height
        self.lock_map = [[threading.Lock()]*width for i in range(height)]

    def draw_to_pixel (self, new_pixel_color, position):
        """attempts to acquire the lock for this pixel and draw to it"""
        success = False
        self.lock_map[position[0]][position[1]].acquire()
        this_pixel = self.pix_map[position[0],position[1]]
        if this_pixel == (255,255,255):
            self.pix_map[position[0],position[1]] = new_pixel_color
            success = True
        self.lock_map[position[0]][position[1]].release()
        return success

    def is_blank (self, position):
        """attempts to acquire the lock for this pixel and returns iswhite"""
        blank = False
        if position[0] > 511 or position[1] > 511:
            return False
        if position[0] < 0 or position[1] < 0:
            return False
        self.lock_map[position[0]][position[1]].acquire()
        this_pixel = self.pix_map[position[0],position[1]]
        if this_pixel == (255,255,255):
            blank = True
        self.lock_map[position[0]][position[1]].release()
        return blank

    def get_color (self, position):
        """attempts to acquire the lock for this pixel and returns its color"""
        self.lock_map[position[0]][position[1]].acquire()
        this_pixel = self.pix_map[position[0],position[1]]
        self.lock_map[position[0]][position[1]].release()
        return this_pixel

class Artist:
    def __init__(self, index, color, start_position, max_steps):
        self.index=index
        self.color=color
        self.max_steps=max_steps
        self.position = start_position
        self.steps_taken = 0
        self.pixels_i_own = list()
        self.completely_trapped = False

    def ready_set_paint (self, restricted_canvas):
        """runs the full paint process for an artist"""
        self.restricted_canvas = restricted_canvas
        while self.steps_taken < self.max_steps:
            if self.completely_trapped:
                return
            if self.restricted_canvas.draw_to_pixel(self.color, self.position):
                self.pixels_i_own.append(self.position)
            self.find_next_position()
            self.steps_taken += 1

    def find_next_position(self):
        """finds the next position randomly"""
        if self.completely_trapped:
            return
        rolls_left = [1,2,3,4]
        valid_position = False
        temp_position = self.position
        while not valid_position: 
            dice_roll = random.choice(rolls_left)
            if dice_roll == 1: #North
                temp_position = (self.position[0],self.position[1]+1)
                valid_position = self.check_position (temp_position)
                if not valid_position:
                    rolls_left.remove(1)
            elif dice_roll == 2: #East
                temp_position = (self.position[0]+1, self.position[1])
                valid_position = self.check_position (temp_position)
                if not valid_position:
                    rolls_left.remove(2)
            elif dice_roll == 3: #South
                temp_position = (self.position[0], self.position[1]-1)
                valid_position = self.check_position (temp_position)
                if not valid_position:
                    rolls_left.remove(3)
            elif dice_roll == 4: #West
                temp_position = (self.position[0]-1, self.position[1])
                valid_position = self.check_position (temp_position)
                if not valid_position:
                    rolls_left.remove(4)
            if not len(rolls_left): #if we just removed the last possible roll
                self.choose_from_owned_pixels()
                return
        if valid_position:
            self.position = temp_position
        else:
            print>>sys.stderr, "THIS SHOULD NEVER HAPPEN"
            return

    def check_position (self, temp_position):
        """checks to see if a position is valid"""
        if (temp_position[0] > 511) or (temp_position[1] > 511):
            return False
        if (temp_position[0] < 0) or (temp_position[1] < 0):
            return False
        return self.restricted_canvas.is_blank(temp_position)

    def choose_from_owned_pixels(self):
        """attempts to choose the next position from the owned pixel list,
        if it fails, it tells the class that it is trapped"""
        temp_position = self.position
        while not self.has_blank_neighbor(temp_position):
            if temp_position in self.pixels_i_own:
                self.pixels_i_own.remove(temp_position)
            if not len(self.pixels_i_own):
                self.completely_trapped = True
                return
            temp_position = random.choice(self.pixels_i_own)
        self.position = temp_position

    def has_blank_neighbor(self, temp_position):
        """checks the four neighboring pixels to see if it is blank"""
        neighbors = [(temp_position[0],temp_position[1]+1), \
                    (temp_position[0]+1, temp_position[1]),\
                    (temp_position[0], temp_position[1]-1),\
                    (temp_position[0]-1, temp_position[1])]
        for temp_neighbor in neighbors:
            if self.restricted_canvas.is_blank(temp_neighbor):    
                return True
        return False


def generate_position(artist_list):
    """generates a random start position, making sure not to duplicate"""
    random_position = (random.randint(0,511),random.randint(0,511))
    attempts = 0
    while random_position in map(lambda artist: artist.position, artist_list):
        random_position = (random.randint(0,511),random.randint(0,511))
        attempts += 1
    return random_position

def generate_color(artist_list):
    """generates a random color that is unique from the other colors,
    using a euclidean distance metric to determine uniqueness"""
    random_color = (random.randint(0,255), random.randint(0,255),\
                                             random.randint(0,255))
    
    def color_too_similar(random_color, artist_list, threshold):
        def find_euclid_distance(color_1, color_2):
            euclid_sum = 0
            for index, color_value1 in enumerate(color_1):
                euclid_sum += ((color_value1 - color_2[index])**2)
            return euclid_sum**(0.5)
        if find_euclid_distance(random_color, (255,255,255)) < threshold:
            return True # makes sure the color isnt too close to white
        for artist in artist_list:
            dist = find_euclid_distance(random_color, artist.color)
            if dist < threshold:
                return True
        return False

    color_tries = 0
    while color_too_similar (random_color, artist_list, threshold=50.):
        random_color = \
        (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        color_tries+= 1
        if color_tries > 50:
            break
    return random_color


def generate_artists(number_of_artists, number_of_steps):
    """returns a list of artists with random start positions and colors"""
    artist_list = list()
    for i in range (number_of_artists):
        artist_list.append(\
                    Artist(i, generate_color(artist_list), \
                        generate_position(artist_list), number_of_steps))
    return artist_list

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("number_of_threads", type=int)
    parser.add_argument("number_of_steps", type=int)

    args = parser.parse_args()

    canvas = Image.new('RGB', (512,512), color=(255,255,255))
    canvas_map = canvas.load()
    canvas.save('canvas.jpg')
    restricted_canvas = RestrictedPixelMap(canvas_map, canvas.size)

    artist_list = generate_artists(args.number_of_threads,args.number_of_steps)

    threads_list = list()

    for artist in artist_list:
        threads_list.append(threading.Thread(target=artist.ready_set_paint,\
                                                 args=((restricted_canvas,))))
    for thread in threads_list:
        thread.start()

    for thread in threads_list:
        thread.join()

    canvas.show()
    canvas.save('masterpiece.jpg')

if __name__ == '__main__':
    main()

