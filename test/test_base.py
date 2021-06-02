import base
import egl
import numpy as np

import faulthandler
faulthandler.enable()

# Scene Graph Manipulation 1

node1 = base.Node.create()
assert node1.children() == 0
node2 = base.Node.create()
node1.attach_child(node2)
assert node1.children() == 1
base.free(node1)

# Scene Graph Manipulation 2

node1 = base.Node.create("root")
assert node1.tag == "root"
node2 = base.Node.create()
assert not node2.has_parent
node1.attach_child(node2)
assert node2.has_parent
assert node2.parent is node1
node2 = node2.detach_from_parent()
assert np.allclose(node2.local_transform, np.eye(4))
base.free(node1)
base.free(node2)

# Basic Rendering

root = base.Node.create()
cam  = base.Camera.create()
cam.local_transform = base.math.rotation4f(0, 1, 0, base.math.deg2rad(20) ) * base.math.translation4f(0, 0, 350)
cam.projection = base.math.frustum4f(base.math.deg2rad(45), 1, 10, 2000)
root.attach_child(cam)

ctx = egl.Context.create()
surface = base.Surface.create(ctx, 100, 100)
renderer = base.FrameRenderer.create( ctx, 100, 100 )
surface.begin()
#renderer.render(cam)
result = surface.end()
assert result.shape == (100, 100, 3)
assert result.sum() == 0
base.free(renderer)
base.free(surface)
base.free(ctx)

base.free(root)

