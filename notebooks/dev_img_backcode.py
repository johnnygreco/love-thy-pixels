import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def circle(xx, yy):    
    r = np.sqrt((xx - 5)**2 + (yy - 5)**2)
    circ = (r < 5).astype(int)
    return circ
