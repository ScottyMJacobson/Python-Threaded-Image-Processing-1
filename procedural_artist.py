# Scott Jacobson
# 9/17/14
# COMP50 Concurrant Programming

"""procedural_artist.py, a program that spawns threads that paint randomly 
    on a canvas"""

# The following synchronization is required among the threads:
# TODO: THIS

# -*- coding: utf-8 -*-
#! /usr/local/bin/python


def main(argv):
    parser = argparse.ArgumentParser()

    canvas = Image.new('RGB', (512,512), color=(255,255,255))

    canvas.show()

if __name__ == '__main__':
    main()
