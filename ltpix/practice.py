import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from scipy import ndimage

DATA_PATH = '/Users/casey.395/projects/love-thy-pixels/images/'

__all__ = ['image']


class image:
    def __init__(self,image_name,data_path=DATA_PATH):
        if (image_name == "dog") or (image_name == "puppy"):
            self.array = mpimg.imread(data_path+'puppy.jpg')
        elif (image_name == "bonnie") or (image_name == "cat"):
            _img = mpimg.imread(data_path+'bonnie.jpeg')
            self.array = ndimage.rotate(_img,-90)
        elif (image_name == "comet") or (image_name == "guinea_pig"):
            _img = mpimg.imread(data_path+'comet.jpg')
            self.array = ndimage.rotate(_img,-90)
        else:
            print('Error: Check image name before proceeding.')
            print('Acceptable names are: dog, puppy, bonnie, cat, comet, and guinea_pig.')
            #raise ValueError 
        reds = self.array.copy()
        reds[:, :, 1] = 0
        reds[:, :, 2] = 0
        self.red_array = reds
        greens = self.array.copy()
        greens[:, :, 0] = 0
        greens[:, :, 2] = 0
        self.green_array = greens
        blues = self.array.copy()
        blues[:, :, 0] = 0
        blues[:, :, 1] = 0
        self.blue_array = blues
    def display(self,which_image=None,xmin=None,xmax=None,ymin=None,ymax=None):
        if which_image == 'red':
            plt.figure(figsize=(8, 8))
            plt.imshow(self.red_array[ymin:ymax,xmin:xmax])
        elif which_image == 'blue':
            plt.figure(figsize=(8, 8))
            plt.imshow(self.blue_array[ymin:ymax,xmin:xmax])
        elif which_image == 'green':
            plt.figure(figsize=(8, 8))
            plt.imshow(self.green_array[ymin:ymax,xmin:xmax])
        elif which_image == 'all':
            fig, axes = plt.subplots(1, 4, figsize=(16, 8), 
                         subplot_kw=dict(xticks=[], yticks=[]))
            fs = 18
            axes[0].imshow(self.array[ymin:ymax,xmin:xmax])
            axes[0].set_title('full color', fontsize=fs)
            axes[1].imshow(self.red_array[ymin:ymax,xmin:xmax])
            axes[1].set_title('red channel', fontsize=fs)
            axes[2].imshow(self.green_array[ymin:ymax,xmin:xmax])
            axes[2].set_title('green channel', fontsize=fs)
            axes[3].imshow(self.blue_array[ymin:ymax,xmin:xmax])
            axes[3].set_title('blue channel', fontsize=fs);
        else:
            plt.figure(figsize=(8, 8))
            plt.imshow(self.array[ymin:ymax,xmin:xmax])
