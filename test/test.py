import sys
from IPython.core import ultratb
sys.excepthook = ultratb.FormattedTB(mode='Verbose', color_scheme='Linux', call_pdb=False)

import base

node1 = base.Node()
assert node1.children() == 0
node2 = base.Node()
node1.attach_child(node2)
assert node1.children() == 1

#node1.delete_all_children()
#print(node2.tag())
