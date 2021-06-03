import test_tools
import base
import presets
import egl
import helpers
import numpy as np
import matplotlib.pyplot as plt
import scipy.ndimage as ndi

import faulthandler
faulthandler.enable()

# ============================
# presets.OpaqueRenderingStage
# ============================

w = 200
h = 100

root = base.Node.create()

cam = base.Camera.create()
cam.local_transform = base.math.translation4f(0, 0, 250)
cam.projection = base.math.frustum4f(base.math.deg2rad(45), 1, 10, 2000) @ base.math.scaling4f(1, w/h, 1)
root.attach_child(cam)

box_mesh  = base.create_box(40, 40, 40)
material1 = base.Material.create('unshaded')
material2 = base.Material.create('unshaded')
material1.set_parameter4f('color', [1, 0, 0, 1])
material2.set_parameter4f('color', [0, 1, 0, 1])

GEOMETRY_TYPE_OPAQUE = 0

box1 = base.Geometry.create(GEOMETRY_TYPE_OPAQUE)
box1.put_feature(presets.OpaqueRenderingStage.ROLE_DEFAULT_MESH, box_mesh)
box1.put_feature(presets.OpaqueRenderingStage.ROLE_DEFAULT_MATERIAL, material1)
box1.local_transform = base.math.translation4f(-10, -10, -40)
root.attach_child(box1)

box2 = base.Geometry.create(GEOMETRY_TYPE_OPAQUE)
box2.put_feature(presets.OpaqueRenderingStage.ROLE_DEFAULT_MESH, box_mesh)
box2.put_feature(presets.OpaqueRenderingStage.ROLE_DEFAULT_MATERIAL, material2)
box2.local_transform = base.math.translation4f(+10, +10, +40)
root.attach_child(box2)

box_mesh .release()
material1.release()
material2.release()

ctx = egl.Context.create()
surface = base.Surface.create(ctx, w, h)
renderer = base.FrameRenderer.create( ctx, w, h )

opaque = presets.OpaqueRenderingStage.create(GEOMETRY_TYPE_OPAQUE)
renderer.append_stage(opaque)

surface.begin()
renderer.render(cam)
result = surface.end()
test_tools.assert_rendering('presets.OpaqueRenderingStage', result)

renderer.free()
cam.detach_from_parent()
root.free()

# ============================
# presets.MIPStage
# ============================

GEOMETRY_TYPE_VOLUME = 1

data = np.ones((100, 100, 100), bool)
data_center = np.subtract(data.shape, 1) // 2
data[tuple(data_center)] = False
data = ndi.distance_transform_edt(data)
data = np.exp(-(data ** 2) / (2 * (25 ** 2)))

root = base.Node.create()
grid_helper = helpers.UInt12VolumeGridHelper.create( data.shape );
grid_helper.load_data( data )
volume = grid_helper.create_node( GEOMETRY_TYPE_VOLUME, helpers.Dimensions( [100, 100, 100] ) )
root.attach_child(volume)
root.attach_child(cam)

renderer = base.FrameRenderer.create( ctx, w, h )
mip = presets.MIPStage.create(GEOMETRY_TYPE_VOLUME)
mip.append_layer( presets.MIPLayer.create( 0, 1, [1, 1, 1, 1] ) )
renderer.append_stage(mip)

surface.begin()
renderer.render(cam)
result = surface.end()
test_tools.assert_rendering('presets.MIPStage', result)

grid_helper.free()
root.free()
surface.free()
ctx.free()

