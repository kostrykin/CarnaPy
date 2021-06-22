import test_tools
import carna.py as cpy
import math
import numpy as np
import scipy.ndimage as ndi

import faulthandler
faulthandler.enable()

# =========================================
# Create toy volume data
# =========================================

data = np.full((16, 8, 4), False)
data[0,0,:] = True
data[0,:,0] = True
data[:,0,0] = True
data[-1,-1,:] = True
data[-1,:,-1] = True
data[:,-1,-1] = True
data[data.shape[0]//2,data.shape[1]//2,data.shape[2]//2] = True

# =========================================
# Define corners (normalized coordinates)
# =========================================

corners = [
    [0, 0, 0],
    [0, 0, 1],
    [0, 1, 0],
    [0, 1, 1],
    [1, 0, 0],
    [1, 0, 1],
    [1, 1, 0],
    [1, 1, 1],
]

# =========================================
# Perform rendering (single segment)
# =========================================

ss_test = test_tools.BatchTest()

for view in ('front', 'left', 'top'):
    with cpy.SingleFrameContext((512, 512), ortho=(-10,+10,-10,+10), near=0.1, far=100, max_segment_bytesize=(2 + np.max(data.shape)) ** 3) as rc:
        if view == 'left': rc.camera.rotate((0, 1, 0), -90, 'deg')
        if view == 'top' : rc.camera.rotate((1, 0, 0), -90, 'deg')
        rc.camera.translate(0, -0.5, 15)
        mask  = rc.mask(data, 'regions', spacing=(1, 1, 1), color=(1, 0, 0, 1), sample_rate=500)
        green = rc.material((0,1,0,1))
        ball  = rc.box(1, 1, 1)
        rc.meshes(ball, green, mask.map_normalized_coordinates(corners), parent=mask)

    test_tools.assert_rendering(f'py.demo4.normalized.ss-{view}', rc.result, batch=ss_test)

ss_test.finish()

# =========================================
# Perform rendering (multiple segments)
# =========================================

ms_test = test_tools.BatchTest()

for view in ('front', 'left', 'top'):
    with cpy.SingleFrameContext((512, 512), ortho=(-10,+10,-10,+10), near=0.1, far=100, max_segment_bytesize=np.prod(data.shape) // 2) as rc:
        if view == 'left': rc.camera.rotate((0, 1, 0), -90, 'deg')
        if view == 'top' : rc.camera.rotate((1, 0, 0), -90, 'deg')
        rc.camera.translate(0, -0.5, 15)
        mask  = rc.mask(data, 'regions', spacing=(1, 1, 1), color=(1, 0, 0, 1), sample_rate=500)
        green = rc.material((0,1,0,1))
        ball  = rc.box(1, 1, 1)
        rc.meshes(ball, green, mask.map_normalized_coordinates(corners), parent=mask)

    test_tools.assert_rendering(f'py.demo4.normalized.ms-{view}', rc.result, batch=ms_test)

ms_test.finish()

# =========================================
# Check corners in voxel coordinates
# =========================================

corners_voxels = corners * np.subtract(data.shape, 1)
mapped_corners = mask.map_normalized_coordinates(corners)

test = test_tools.BatchTest()
test.assert_allclose(mapped_corners, mask.map_voxel_coordinates(corners_voxels), 'map_voxel_coordinates')
test.finish()

