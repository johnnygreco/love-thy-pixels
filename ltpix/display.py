import os
import numpy as np 
import matplotlib.pyplot as plt 
from . import project_dir

try:
    plt.style.use(os.path.join(project_dir, 'ltpix/jpg.mplstyle'))
except:
    pass


__all__ = ['display_image', 'plot_pixel_histogram']


def _check_subplots(subplots, with_ticks=True, **kwargs):
    if subplots is None:
        figsize = kwargs.pop('figsize', (10, 10))
        if with_ticks:
            subplot_kw = {}
        else:
            subplot_kw = dict(xticks=[], yticks=[])
        fig, ax = plt.subplots(
            figsize=figsize, subplot_kw=subplot_kw, **kwargs)
    else:
        fig, ax = subplots
    return fig, ax


def display_image(image, subplots=None, single_band_percentiles=[1, 99],
                  single_band_cmap='gray_r', **kwargs):

    fig, ax = _check_subplots(subplots, False, **kwargs)

    if image.shape[-1] == 3:
        ax.imshow(image, origin='lower')
    else:
        p1, p2 = single_band_percentiles
        vmin, vmax = np.percentile(image, [p1, p2])
        ax.imshow(image, origin='lower', vmin=vmin, vmax=vmax, 
                  cmap=single_band_cmap)
    
    return fig, ax


def pixel_histogram(image, bins=100, subplots=None, color='k', **kwargs):

    fig, ax = _check_subplots(subplots, **kwargs)
    pixels = image.flatten()
    ax.hist(pixels, log=True, bins=bins, alpha=0.4, color=color)
    ax.hist(pixels, log=True, bins=bins, lw=2, histtype='step', color=color)
    ax.set_xlabel('Pixel Value', fontsize=24)
    ax.set_ylabel('Number of Pixels', fontsize=24)
    ax.tick_params('both', labelsize=20)
    ax.minorticks_on()

    return fig, ax
