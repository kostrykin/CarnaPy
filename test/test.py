import base
import numpy as np

import faulthandler
faulthandler.enable()

node1 = base.Node.create()
assert node1.children() == 0
node2 = base.Node.create()
node1.attach_child(node2)
assert node1.children() == 1

base.free(node1)

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
