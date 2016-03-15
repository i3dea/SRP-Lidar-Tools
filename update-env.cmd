conda install scikit-learn -y
conda install scikit-image -y
conda install gdal -y
conda install rasterio -y
conda install fiona -y
:: conda install shapely -y
pip install shapely --only-binary :all:
conda install pywget -y

conda install liblas --only-binary :all:
::If that does not work for liblas, use python -m wget (URL for wheel)

conda install rtree -c IOOS -y
conda install matplotlib -y
conda install ipython-notebook -y
conda install docopt -y
conda install pandas -y
conda install progressbar -y