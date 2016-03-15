"""USAGE: eval <folder> [options]

Evaluate a rectangle detection approach

Options:
    <folder>                A folder with a number of subfolders, one for each test image. [default: ./]
    --meters <meters>       The number of meters per pixel [default: 0.13]
    --boxwidth <bwidth>     The size of a box [default: 1.0]
    --boxsep <bsep>         The separation between a box and the nearest object [default: 0.5]
"""
import os
import numpy as np
import docopt
import skimage
from PIL import Image, ImageChops
from math import degrees

from PIL.ImageChops import offset
from pandas.core.frame import DataFrame
from skimage.filters import gabor_kernel
from pylab import *
from scipy.ndimage.filters import convolve

args = docopt.docopt(__doc__)
folder = args['<folder>']
meters = float(args['--meters'])
box_width = float(args['--boxwidth'])
box_sep = float(args['--boxsep'])
samples = [f for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f)) and f.isdigit()]

print args

# prepare filter bank kernels
sigma = 1 #box_width/(2*meters)
frequency = meters/box_sep
kernels = []
angles = np.linspace(0, np.pi, 18, endpoint=False)
degs = [degrees(x) for x in angles]
print degs

for theta in angles:
    kernel = gabor_kernel(frequency, theta=theta, sigma_x=sigma, sigma_y=sigma)
    kernels.append(kernel)
    # imshow(np.real(kernel))
    # show()

positives = []
negatives = []

for s in samples:
    input_path = os.path.join(folder, s, 'input.tif')
    expected_path = os.path.join(folder, s, 'expected.tif')
    data_path = os.path.join(folder, s, 'data.csv')

    input_image = Image.open(input_path)
    expected_image = Image.open(expected_path)
    data = DataFrame.from_csv(data_path)

    a = np.asarray(input_image)
    responses = np.empty((len(kernels), a.shape[0], a.shape[1]))

    for i, k in enumerate(kernels):
        response = responses[i, :, :] = np.hypot(convolve(a, np.real(k)), convolve(a, np.imag(k)))
        #imshow(response)

    scores = []
    for i in range(9):
        j = (i + 9) % 18
        x_angle = angles[i]
        y_angle = angles[j]

        c = cos(x_angle)
        s = sin(x_angle)
        d = box_width / 2.
        d /= meters

        d = 0 # DELETEME

        dx = int(round(c*d))
        dy = int(round(s*d))

        fxp = (offset(Image.fromarray(responses[i]), dx, dy))
        fxm = (offset(Image.fromarray(responses[i]), -dx, -dy))
        fyp = (offset(Image.fromarray(responses[j]), -dy, dx))
        fym = (offset(Image.fromarray(responses[j]), dy, -dx))

        score = np.sort(np.stack([fxp, fxm, fyp, fym]), axis=0)[3]
        scores.append(score)

    subplot(121)
    imshow(np.max(scores, axis=0))
    gray()
    colorbar()
    subplot(122)
    imshow(a)
    colorbar()
    show()