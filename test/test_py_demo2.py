import test_tools
import carna.py as cpy
import math
import numpy as np
import scipy.ndimage as ndi

import faulthandler
faulthandler.enable()

# ============================
# Define volume data
# ============================

def gaussian_filter3d(img, sigma):
    for i in range(3):
        img = ndi.gaussian_filter1d(img, sigma, axis=i)
    return img

np.random.seed(0)
data  = gaussian_filter3d(np.random.randn(256, 256, 32), 20)
data += 1e-3 * np.random.randn(*data.shape)
data[data < 0] = 0
data /= data.max()

# ============================
# Define opaque data
# ============================

boxes = [[ 100, -100, 0], [-100, 100, 10]]

# ============================
# Perform rendering
# ============================

with cpy.SingleFrameContext((512, 512), fov=45, near=1, far=1000) as rc:
    green = rc.material((0,1,0,1))
    box = rc.box(20, 20, 20)
    for loc in boxes:
        rc.mesh(box, green).translate(*loc)
    rc.volume(data, spacing=(1, 1, 1))
    dvr = rc.dvr()
    dvr.diffuse_light = 1
    rc.camera.rotate((1.5, 1, 0), 40, 'deg').translate(10, -25, 150)

test_tools.assert_rendering('py.demo2', rc.result)

