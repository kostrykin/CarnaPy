import test_tools
import carna.py as cpy
import math
import numpy as np
import scipy.ndimage as ndi

import faulthandler
faulthandler.enable()

# ============================
# deduce_volume_format
# ============================

assert 'UInt8Intensity'  in cpy.deduce_volume_format('uint8')
assert 'UInt8Intensity'  in cpy.deduce_volume_format(np.uint8)
assert 'UInt16Intensity' in cpy.deduce_volume_format('uint16')
assert 'UInt16Intensity' in cpy.deduce_volume_format(np.uint16)
assert 'UInt16Intensity' in cpy.deduce_volume_format('float16')
assert 'UInt16Intensity' in cpy.deduce_volume_format(np.float16)

whitelist = [np.uint8, np.uint16, np.float16, np.float32, np.float64]
illegal_formats = [t for t in sum(np.sctypes.values(), []) if t not in whitelist]

for fmt in illegal_formats:
    try:
        cpy.deduce_volume_format(fmt)
        assert False
    except:
        pass

