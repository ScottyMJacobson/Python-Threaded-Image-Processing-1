# Scott Jacobson
# 9/17/14
# COMP50 Concurrant Programming
# 3 hours

"""transform_image.py, a program that takes in an image and performs 
    one of four transforms using one specified threading"""

# The following synchronization is required among the threads:
# Every thread has to finish its processing before the
# function can return to main and print the picture.

# -*- coding: utf-8 -*-
#! /usr/local/bin/python

MAX_THREADS = 500

import argparse
import sys
import threading
from PIL import Image

def switch_r_b(pixel_tuple):
    """takes in a tuple of RGB values, 
    and returns a pixel with swapped red and blue channels"""
    return ((pixel_tuple[2], pixel_tuple[1], pixel_tuple[0]))

def grayscale(pixel_tuple):
    """takes in a tuple of RGB values, 
    and returns its grayscale equivalent using the luminosity formula"""
    gray_val = int(0.21*pixel_tuple[0]+0.72*pixel_tuple[1]+0.07*pixel_tuple[2])
    return ((gray_val, gray_val, gray_val))

def invert(pixel_tuple):
    """takes in a tuple of RGB values
    and returns the pixel with its colors inverted"""
    return ((255-pixel_tuple[2], 255-pixel_tuple[1], 255-pixel_tuple[0]))

def transform_pixels(pix_map, row_limits, col_limits, function_to_use):
    """takes in an array of pixels, width, and height, 
    and applies function_to_use to each"""
    for col in range(row_limits[0], row_limits[1]):
        for row in range(col_limits[0], col_limits[1]):
            pix_map[col,row] = function_to_use (pix_map[col,row])

def threaded_transform(image_to_transform, rows_to_use, columns_to_use, function_to_use):
    """takes in the full pix map, divides it into threads based on 
        rows and columns given, and calls transform on that thread"""
    pix_map = image_to_transform.load()
    width, height = image_to_transform.size
    width_per_block = width/rows_to_use + (0 if width%rows_to_use == 0 else 1)
    height_per_block = height/columns_to_use + \
                                        (0 if width%columns_to_use == 0 else 1)
    all_threads = list()
    for row_block in range(rows_to_use):
        for col_block in range (columns_to_use):
            min_row = row_block * width_per_block
            max_row = (row_block + 1) * width_per_block
            if max_row > width:
                max_row = width
            min_col = col_block * height_per_block
            max_col = (col_block + 1) * height_per_block
            if max_col > height:
                max_col = height
            print (min_row, max_row), (min_col,max_col)
            all_threads.append(threading.Thread(target=transform_pixels, \
                args=(pix_map, (min_row, max_row), \
                    (min_col,max_col), function_to_use)))
    for thread in all_threads:
        thread.start()
    for thread in all_threads:
        thread.join()

    return image_to_transform

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("image_file", type=str)
    parser.add_argument("output_name", type=str)
    parser.add_argument("transformation", type=str)
    parser.add_argument("rows", nargs='?', default=2, type=int)
    parser.add_argument("columns", nargs='?', default=2, type=int)

    args = parser.parse_args()

    transform_functions = dict([('switch-r-b', switch_r_b), \
                                 ('grayscale', grayscale), \
                                 ('invert', invert)])
    rows_to_use = args.rows
    columns_to_use = args.columns
    number_of_threads = args.rows * args.columns
    if number_of_threads > MAX_THREADS:
        print>>sys.stderr,"ERROR: Thread count {0} is greater than max of {1}"\
        .format(number_of_threads, MAX_THREADS)
        exit(2)

    if args.transformation in transform_functions:
        function_to_use = transform_functions[args.transformation] 
    else:
        print>> sys.stderr, "Unkown transform: {0}".format(args.transformation)
        exit(3)

    image_to_transform = Image.open(image_file)

    if image_to_transform.mode is not 'RGB':
        print>> sys.stderr, "Unkown color mode: {0}"\
                                            .format(image_to_transform.mode)
        exit(4)

    final_image = threaded_transform(image_to_transform, rows_to_use, columns_to_use, function_to_use)

    final_image.show()
    final_image.save(args.output_name)
    

if __name__ == '__main__':
    main(sys.argv)
