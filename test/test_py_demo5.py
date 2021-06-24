import test_tools
import carna.py as cpy
import math
import numpy as np
import scipy.ndimage as ndi

import faulthandler
faulthandler.enable()

# ============================
# Create toy volume data
# ============================

def gaussian_filter3d(img, sigma):
    for i in range(3):
        img = ndi.gaussian_filter1d(img, sigma, axis=i)
    return img

np.random.seed(0)
data  = gaussian_filter3d(np.random.randn(256, 256, 32), 20) ## create low-frequency random data
data  = 0.5 ** 3 + (data - 0.5) ** 3                         ## spread intensity distribution to create sharper intensity gradients
data += 1e-4 * np.random.randn(*data.shape)                  ## add white image noise
data[data < 0] = 0                                           ## normalize data to [0, ...)
data /= data.max()                                           ## normalize data to [0, 1]

# ============================
# Define points of interest
# ============================

poi_list = [[ 50, -30, 5], [-100, 100, 10], [110, -110, 0]]

# ============================
# Perform rendering
# ============================

with cpy.SingleFrameContext((256, 512), fov=90, near=1, far=1000) as rc:
    green = rc.material((0,1,0,1))
    box = rc.box(20, 20, 20)
    rc.meshes(box, green, poi_list)
    rc.volume(data, spacing=(1, 1, 1), normals=True, fmt_hint=np.uint8)
    rc.dvr(diffuse_light=1, sample_rate=1000)
    rc.camera.translate(128, -128, 64).look_at((0, 0, 0), (0, 0, 1)).translate(0, 0, 100)

test_tools.assert_rendering('py.demo5', rc.result)

