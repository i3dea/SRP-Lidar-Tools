"""USAGE: gtd2 [options]

Generate a test data folder with sample images.
This will produce a folders for each angle, and a folder for images with no box.


Options:
    -s, --square SIZE                   Add a square target with the given size (in meters) [default: 1.0]
    -o <folder>, --output <folder>      An output folder [default: ./].
    -m <meters>, --mpp <meters>         The meters per pixel [default: 0.13].
    --width <width>                     The width [default: 64]
    --height <height>                   The height [default: 64]
    --count <count>                     The number of samples to generate [default: 100]
    --rpos <ratio>                      The fraction of samples that should be positive examples [default: 0.50]
    --anglesteps <n>                    The number of angle steps (90/<n> degrees per step). [default: 9]
"""
import os
from math import radians, hypot, ceil, cos, sin
from random import randrange

import numpy as np
from logging import *
import rasterio
import skimage.morphology
from PIL import  Image, ImageDraw
import pandas as pd
from progressbar import ProgressBar
from progressbar.widgets import SimpleProgress


def pad_image(old_im, padding):
    """
    :param old_im:
    :type old_im: PIL.Image.Image
    :return:
    """
    old_width, old_height = old_size = old_im.size
    new_size = old_width + 2*padding, old_height + 2*padding
    new_im = Image.new("RGB", new_size)
    new_im.paste(old_im, ((new_size[0]-old_size[0])/2,  (new_size[1] - old_size[1]) / 2))
    return new_im



def generate_test_data(folder, targets, meters=0.1, num_rects=3, size=(512, 512)):
    if not os.path.isdir(folder):
        os.makedirs(folder)
    w, h = size
    ppm = 1.0/meters
    buf = Image.new("F", (w, h))
    truth = Image.new("1", (w, h))


    padded_targets = []
    for t in targets:
        assert isinstance(t, Image.Image)
        padding = int(ceil(hypot(t.width, t.height)/2))
        padded_targets.append(pad_image(t, padding))

    data = []
    for i in range(num_rects):
        x = randrange(0, w)
        y = randrange(0, h)
        t = randrange(0, len(padded_targets))
        angle = randrange(0, 360)
        rotated = padded_targets[t].rotate(angle)
        box = x-rotated.width / 2, y -rotated.height/2
        buf.paste(rotated, box)
        truth.putpixel((x, y), True)
        data.append(dict(x=x, y=y, angle=angle, template=t))

    draw = ImageDraw.Draw(buf)
    for i in range(100):
        x = randrange(0, w)
        y = randrange(0, h)
        length = randrange(1, 100)
        angle = randrange(0, 360)
        x2 = x + length*cos(radians(angle))
        y2 = y + length*sin(radians(angle))
        draw.line([(x, y), (x2, y2)])

    buf = Image.fromarray(buf + np.random.poisson(0.1, np.asarray(buf).shape))

    # Write files
    if not os.path.isdir(folder):
        os.makedirs(folder)
    buf.save(os.path.join(folder, 'input.tif'))
    truth.save(os.path.join(folder, 'expected.tif'))
    pd.DataFrame(data).to_csv(os.path.join(folder, 'data.csv'))




if __name__ == '__main__':
    import docopt
    args = docopt.docopt(__doc__)

    getLogger().setLevel(DEBUG)
    debug(args)

    width = int(args['--width'])
    height = int(args['--height'])
    meters = float(args['--mpp'])
    num_rects = int(args['--nr'])
    output = args['--output']
    targets = args['--target']
    count = int(args['--count'])
    target_images = []

    if args['--square'] is not None:
        square_width = int(round(float(args['--square'])/meters))
        square_array = skimage.morphology.square(square_width, dtype=float)
        square_array[0:-1, 1:-1] = 0.0
        square_image = Image.fromarray(square_array)
        target_images.append(square_image)

    for target in targets:
        target_image = Image.open(target)
        target_images.append(target_image)

    debug(target_images)

    bar = ProgressBar()
    for i in bar(range(count)):
        subfolder = os.path.join(output, '{:04}'.format(i))
        generate_test_data(subfolder, target_images, meters, num_rects, (width, height))



