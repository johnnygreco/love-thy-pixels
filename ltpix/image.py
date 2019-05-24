import os, sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from astropy.io import fits
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.visualization import make_lupton_rgb
from astropy.wcs import WCS
from photutils import CircularAperture, SkyCircularAperture
from photutils import aperture_photometry
from collections import namedtuple
from scipy import ndimage
import webbrowser
from .log import logger
from .display import display_image, pixel_histogram


if os.path.expanduser("~") == '/Users/jgreco':
    DATA_PATH = '/Users/jgreco/local-io/ltpix-data'
elif os.path.expanduser("~") == '/root':
    DATA_PATH = '/content/gdrive/My Drive/ASPIRE2019/ltpix-data'
else:
    DATA_PATH = '.'

RGBData = namedtuple('RGBData', 'red green blue')
_galaxy_distance_Mpc = {1: 25.5, 2: 571.9, 3: 29.4, 4: 618.2, 5: 154.7}

__all__ = ['make_circle_image', 'AstroImage', 'AnimalImage']


def make_circle_image():
    yy, xx = np.mgrid[:15, :15]
    r = np.sqrt((xx - 7)**2 + (yy - 7)**2)
    circ = (r < 7).astype(int)
    plt.imshow(circ, cmap='gray')
    return circ

class AstroImage(object):

    def __init__(self, object_num=1, object_type='galaxy', 
                 data_path=DATA_PATH):

        self.success = True

        self.path = os.path.join(data_path, 'hsc-galaxies')
        if not os.path.isdir(self.path):
            logger.error('directory {} does not exist'.format(self.path))
            self.success = False

        if self.success:
            self.path = os.path.join(
                self.path, '{}-{}'.format(object_type, object_num))
            if not os.path.isdir(self.path):
                logger.error('{} number {} of does not exist'.\
                              format(object_type, object_num))
                self.success = False

        if self.success:
            fn = lambda b: os.path.join(self.path, 'HSC-' + b + '.fits')
            self.red_fn = fn('I')
            self.red_data = fits.getdata(self.red_fn)
            self.green_fn = fn('R')
            self.green_data = fits.getdata(self.green_fn)
            self.blue_fn = fn('G')
            self.blue_data = fits.getdata(self.blue_fn)
            self.rgb_data = RGBData(red=self.red_data, 
                                    green=self.green_data, 
                                    blue=self.blue_data)
            self.band_key = dict(I='red', R='green', G='blue')
            self.bands = 'gri'
            self.wcs = WCS(fits.getheader(self.red_fn, ext=1))
            y_c, x_c = np.array(self.red_data.shape) / 2
            self.sky_coord = SkyCoord.from_pixel(x_c, y_c, wcs=self.wcs)
            self.object_num = object_num

            logger.info('Successfully loaded {} number {}!'.\
                format(object_type, object_num))

    @property
    def object_info(self):
        with open(self.path + '/NOTES') as f:
            for line in f.readlines():
                print(line, end='')

    @property
    def distance_lyr(self):
        Mpc_to_lyr = 3.262e6
        return _galaxy_distance_Mpc[self.object_num] * Mpc_to_lyr

    @property
    def distance_Mpc(self):
        return _galaxy_distance_Mpc[self.object_num] 

    def open_in_legacy_viewer(self):
        url = 'http://legacysurvey.org/viewer?ra={}&'
        url += 'dec={}&zoom=14&layer=decals-dr7'
        ra = self.sky_coord.ra.deg
        dec = self.sky_coord.dec.deg
        url = url.format(ra, dec)
        webbrowser.open(url, new=1)

    def make_rgb_image(self, stretch=0.4, Q=8):
        rgb_image = make_lupton_rgb(self.rgb_data.red, 
                                    self.rgb_data.green,
                                    self.rgb_data.blue,
                                    stretch=stretch,
                                    Q=Q)
        return rgb_image

    def display_single_band_image(self, band, cmap='gray_r', figsize=(10, 10),
                                  percentiles=[1, 99], positions=None, 
                                  radius=None, apcolor='lime'): 

        if len(band) == 1:
            image = getattr(self, self.band_key[band.upper()] + '_data')
        elif band in ['red', 'green', 'blue']:
            image = getattr(self, band + '_data')
        else:
            logger.error(band + ' is not a valid band!')
            return None

        fig, ax = display_image(image, single_band_percentiles=percentiles, 
                                 single_band_cmap=cmap, figsize=figsize)

        if positions is not None:
            if radius is None:
                logger.error('You must give aperture radius to plot circles')
            else:
                positions = np.asarray(positions)
                positions -= 1
                apertures = CircularAperture(positions, radius)
                apertures.plot(ax=ax, color=apcolor, lw=2)
                for num, (x, y) in enumerate(positions):
                    ax.text(x + radius * 2.5, y, 
                            num + 1, 
                            va='center', 
                            ha='left',
                            fontsize=16, 
                            color='red')

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

    def measure_light_in_circle(self, positions, radius, sky_coords=False):

        positions = np.asarray(positions) 
        
        if sky_coords:
            wcs = self.wcs
            positions = SkyCoord(positions, unit='deg')
            apertures = SkyCircularAperture(positions, radius * u.arcsec)
        else:
            wcs = None
            positions -= 1
            apertures = CircularAperture(positions, radius)

        light = {}

        for b in ['red', 'green', 'blue']:
            data = getattr(self, b + '_data')
            phot = aperture_photometry(data, apertures, wcs=wcs)
            light[b] = np.array(phot['aperture_sum'])

        return light['red'], light['green'], light['blue']


class AnimalImage(object):

    def __init__(self, animal_name, data_path=DATA_PATH):

        self.success = True
        self.path = os.path.join(data_path, 'animal-images')

        if (animal_name == "dog") or (animal_name == "puppy"):
            self.fn = os.path.join(self.path, 'puppy.jpg')
        elif (animal_name == "bonnie") or (animal_name == "cat"):
            self.fn = os.path.join(self.path, 'bonnie.jpg')
        elif (animal_name == "comet") or (animal_name == "guinea pig"):
            self.fn = os.path.join(self.path, 'comet.jpg')
        else:
            self.success = False
            logger.error('Check image name before proceeding.')
            logger.error('Acceptable names are: dog, puppy, bonnie, '\
                         'cat, comet, and guinea pig.')

        if self.success:

            self.array = mpimg.imread(self.fn)

            reds = self.array.copy()
            reds[:, :, 1] = 0
            reds[:, :, 2] = 0
            self.red_data = reds

            greens = self.array.copy()
            greens[:, :, 0] = 0
            greens[:, :, 2] = 0
            self.green_data = greens

            blues = self.array.copy()
            blues[:, :, 0] = 0
            blues[:, :, 1] = 0
            self.blue_data = blues

    def display(self, which_image=None, xmin=None, xmax=None, 
                ymin=None, ymax=None, **kwargs):

        figsize = kwargs.pop('figsize', (8, 8))
        if which_image == 'red':
            figsize = kwargs.pop('figsize', (8, 8))
            plt.figure(figsize=figsize)
            plt.imshow(self.red_data[ymin:ymax,xmin:xmax])
        elif which_image == 'blue':
            plt.figure(figsize=figsize)
            plt.imshow(self.blue_data[ymin:ymax,xmin:xmax])
        elif which_image == 'green':
            plt.figure(figsize=figsize)
            plt.imshow(self.green_data[ymin:ymax,xmin:xmax])
        elif which_image == 'all':
            figsize = kwargs.pop('figsize', (16, 8))
            fig, axes = plt.subplots(1, 4, figsize=figsize,
                         subplot_kw=dict(xticks=[], yticks=[]))
            fs = 18
            axes[0].imshow(self.array[ymin:ymax, xmin:xmax])
            axes[0].set_title('full color', fontsize=fs)
            axes[1].imshow(self.red_data[ymin:ymax, xmin:xmax])
            axes[1].set_title('red channel', fontsize=fs)
            axes[2].imshow(self.green_data[ymin:ymax, xmin:xmax])
            axes[2].set_title('green channel', fontsize=fs)
            axes[3].imshow(self.blue_data[ymin:ymax, xmin:xmax])
            axes[3].set_title('blue channel', fontsize=fs);
        else:
            plt.figure(figsize=figsize)
            plt.imshow(self.array[ymin:ymax,xmin:xmax])
