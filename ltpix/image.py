import os, sys
import numpy as np
from astropy.io import fits
from astropy.visualization import make_lupton_rgb
from collections import namedtuple
from .log import logger
from .display import display_image, pixel_histogram


DATA_PATH = '/Users/jgreco/local-io/ltpix-data'
RGBData = namedtuple('RGBData', 'red green blue')


__all__ = ['AstroImage']


class AstroImage(object):

    def __init__(self, object_num=1, object_type='galaxy', 
                 data_path=DATA_PATH):

        self.success = True

        self.path = os.path.join(data_path, 'hsc-galaxies')
        if not os.path.isdir(self.path):
            logger.error('directory {} does not exist'.format(self.path))
            self.success = False

        self.path = os.path.join(
            self.path, '{}-{}'.format(object_type, object_num))
        if not os.path.isdir(self.path):
            logger.error('{} number {} of does not exist'.\
                          format(object_type, object_num))
            self.success = False

        if self.success:
            fn = lambda b: os.path.join(self.path, 'HSC-' + b + '.fits')
            self.red_fn = os.path.join(self.path, fn('I'))
            self.red_data = fits.getdata(self.red_fn)
            self.green_fn = os.path.join(self.path, fn('R'))
            self.green_data = fits.getdata(self.green_fn)
            self.blue_fn = os.path.join(self.path, fn('G'))
            self.blue_data = fits.getdata(self.blue_fn)
            self.rgb_data = RGBData(red=self.red_data, 
                                    green=self.green_data, 
                                    blue=self.blue_data)
            self.band_key = dict(I='red', R='green', G='blue')
            self.bands = 'gri'

    @property
    def object_info(self):
        with open(self.path + '/NOTES') as f:
            for line in f.readlines():
                print(line, end='')

    def make_rgb_image(self, stretch=0.4, Q=8):
        rgb_image = make_lupton_rgb(self.rgb_data.red, 
                                    self.rgb_data.green,
                                    self.rgb_data.blue,
                                    stretch=stretch,
                                    Q=Q)
        return rgb_image

    def display_single_band_image(self, band, cmap='gray_r', figsize=(10, 10),
                                  percentiles=[1, 99]): 

        if len(band) == 1:
            image = getattr(self, self.band_key[band.upper()] + '_data')
        elif band in ['red', 'green', 'blue']:
            image = getattr(self, band + '_data')
        else:
            logger.error(band + ' is not a valid band!')
            return None

        display_image(image, single_band_percentiles=percentiles, 
                      single_band_cmap=cmap, figsize=figsize)


    def display_rgb_image(self, figsize=(10, 10), **kwargs): 

        display_image(self.make_rgb_image(**kwargs), figsize=figsize)

    def display_pixel_histogram(self, band, bins=100, figsize=(8, 6)):

        if len(band) == 1:
            image = getattr(self, self.band_key[band.upper()] + '_data')
            color = 'tab:' + self.band_key[band.upper()]
        elif band in ['red', 'green', 'blue']:
            image = getattr(self, band + '_data')
            color = 'tab:' + band
        else:
            logger.error(band + ' is not a valid band!')
            return None

        fig, ax = pixel_histogram(image, bins=bins, 
                                  figsize=figsize, color=color)

        ax.set_title(color.split(':')[-1] + ' image pixel histogram', 
                     fontsize=26, y=1.01)
