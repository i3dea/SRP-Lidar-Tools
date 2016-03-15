"""USAGE: detect <input> <output> --meters <meters>

Detect all boxes in input and produce output files 'detected.tif' that is nonzero for each detected box
ad detected.csv that has the parameters.

Options:
    <input>                     An input image
    <output>                    An output folder, where we will write detected.tif and detected.csv files [default: ./]
    --meters <meters>           The resolution of the input (meters per pixe). [defalut: 0.13]
"""

import docopt

args = docopt.docopt(__doc__)

input_ = args['<input>']
output = args['<output>']
meters = float(args['--meters'])

filters = []
for angle in range(0, 180):
