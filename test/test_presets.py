import base
import presets
import egl
import numpy as np

import faulthandler
faulthandler.enable()

# =========================

root = base.Node.create()

cam = base.Camera.create()
cam.local_transform = base.math.translation4f(0, 0, 350)
cam.projection = base.math.frustum4f(base.math.deg2rad(45), 1, 10, 2000)
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
surface = base.Surface.create(ctx, 100, 100)
renderer = base.FrameRenderer.create( ctx, 100, 100 )

opaque = presets.OpaqueRenderingStage.create(GEOMETRY_TYPE_OPAQUE)
renderer.append_stage(opaque)

surface.begin()
renderer.render(cam)
result = surface.end()
assert result.shape == (100, 100, 3)
print('Sum:', result.sum())
assert result.sum() == 0
base.free(renderer)
base.free(surface)
base.free(ctx)

base.free(root)

