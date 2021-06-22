import test_tools
import carna.base    as base
import carna.presets as presets
import carna.egl     as egl
import carna.helpers as helpers
import numpy as np
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
cam.projection = base.math.frustum4f(base.math.deg2rad(90), 1, 10, 2000) @ base.math.scaling4f(1, w/h, 1)
root.attach_child(cam)

box_mesh  = base.create_box(40, 40, 40)
ball_mesh = base.create_ball(35)
material1 = base.Material.create('unshaded')
material2 = base.Material.create('unshaded')
material3 = base.Material.create('solid')
material1.set_parameter4f('color', [1, 0, 0, 1])
material2.set_parameter4f('color', [0, 1, 0, 1])
material3.set_parameter4f('color', [0, 0, 1, 1])

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

ball = base.Geometry.create(GEOMETRY_TYPE_OPAQUE)
ball.put_feature(presets.OpaqueRenderingStage.ROLE_DEFAULT_MESH, ball_mesh)
ball.put_feature(presets.OpaqueRenderingStage.ROLE_DEFAULT_MATERIAL, material3)
ball.local_transform = base.math.translation4f(-20, +25, 40)
root.attach_child(ball)

box_mesh .release()
ball_mesh.release()
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
grid_helper = helpers.VolumeGrid_UInt16Intensity.create(data.shape);
grid_helper.load_data( data )
volume = grid_helper.create_node(GEOMETRY_TYPE_VOLUME, helpers.Dimensions([100, 100, 100]))
root.attach_child(volume)
root.attach_child(cam)

renderer = base.FrameRenderer.create(ctx, w, h)
mip = presets.MIPStage.create(GEOMETRY_TYPE_VOLUME)
mip.append_layer( presets.MIPLayer.create(0, 1, [1, 1, 1, 1]))
renderer.append_stage(mip)

surface.begin()
renderer.render(cam)
result = surface.end()
test_tools.assert_rendering('presets.MIPStage', result)

# ============================
# presets.CuttingPlanesStage
# ============================

GEOMETRY_TYPE_PLANE = 2

cps = presets.CuttingPlanesStage.create(GEOMETRY_TYPE_VOLUME, GEOMETRY_TYPE_PLANE)
renderer.clear_stages()
renderer.append_stage(cps);

plane = base.Geometry.create(GEOMETRY_TYPE_PLANE)
plane.local_transform = base.math.plane4f([1, 1, 1], 0)
root.attach_child(plane);

surface.begin()
renderer.render(cam)
result = surface.end()
test_tools.assert_rendering('presets.CuttingPlanesStage', result)

# ============================
# presets.DVRStage
# ============================

dvr = presets.DVRStage.create(GEOMETRY_TYPE_VOLUME)
dvr.write_color_map(0.2, 1, [1.0, 0.0, 0.0, 0.9], [1.0, 1.0, 0.0, 1.0])
renderer.clear_stages()
renderer.append_stage(dvr)

surface.begin()
renderer.render(cam)
result = surface.end()
test_tools.assert_rendering('presets.DVRStage', result)

# ============================
# presets.MaskRenderingStage
# ============================

GEOMETRY_TYPE_MASK = 3

mr = presets.MaskRenderingStage.create(GEOMETRY_TYPE_MASK)
renderer.clear_stages()
renderer.append_stage(mr)

mask_grid_helper = helpers.VolumeGrid_UInt8Intensity.create(data.shape);
mask_grid_helper.load_data( data > 0.5 )
mask = mask_grid_helper.create_node(GEOMETRY_TYPE_MASK, helpers.Dimensions([100, 100, 100]))
root.attach_child(mask)

mr.render_borders = False
surface.begin()
renderer.render(cam)
result = surface.end()
test_tools.assert_rendering('presets.MaskRenderingStage', result)

mr.render_borders = True
surface.begin()
renderer.render(cam)
result = surface.end()
test_tools.assert_rendering('presets.MaskRenderingStage.render_borders', result)

# ============================
# Clean up
# ============================

renderer.free()
mask_grid_helper.free()
grid_helper.free()
root.free()
surface.free()
ctx.free()

