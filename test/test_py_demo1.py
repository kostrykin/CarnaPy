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

data = np.ones((100, 100, 100), bool)
data_center = np.subtract(data.shape, 1) // 2
data[tuple(data_center)] = False
data = ndi.distance_transform_edt(data)
data = np.exp(-(data ** 2) / (2 * (25 ** 2)))

# ============================
# Define opaque data
# ============================

dots  = [[-100, -100, 0], [ 100, 100, 0]]
boxes = [[ 100, -100, 0], [-100, 100, 0]]

# ============================
# Perform rendering
# ============================

with cpy.SingleFrameContext((100, 200), fov=90, near=1, far=1000) as rc:
    rc.dots(dots, color=(0,1,0,1), size=8)
    green = rc.material((0,1,0,1))
    box = rc.box(20, 20, 20)
    for loc in boxes:
        rc.mesh(box, green).translate(*loc)
    rc.volume(data, dimensions=(100, 100, 100), fmt_hint=np.uint8)
    rc.mip()
    rc.camera.translate(0, 0, 250)

test_tools.assert_rendering('py.demo1', rc.result)

