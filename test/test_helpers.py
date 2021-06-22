import test_tools
import carna.base    as base
import carna.presets as presets
import carna.egl     as egl
import carna.helpers as helpers
import math
import numpy as np
import scipy.ndimage as ndi

import faulthandler
faulthandler.enable()

def test_helpers(VolumeGridClass, result_suffix):

    w = 200
    h = 100

    # ============================
    # Scene construction
    # ============================

    GEOMETRY_TYPE_OPAQUE = 0
    GEOMETRY_TYPE_VOLUME = 1

    root = base.Node.create()

    cam = base.Camera.create()
    cam.local_transform = base.math.translation4f(0, 0, 250)
    cam.projection = base.math.frustum4f(base.math.deg2rad(90), 1, 10, 2000) @ base.math.scaling4f(1, w/h, 1)
    root.attach_child(cam)

    box_size   = 50
    box_offset = math.sqrt(2 * ((box_size / 2) ** 2))

    box_mesh  = base.create_box(box_size, box_size, 0)
    material1 = base.Material.create('unshaded')
    material2 = base.Material.create('unshaded')
    material3 = base.Material.create('unshaded')
    material1.set_parameter4f('color', [0, 1, 0, 1])
    material2.set_parameter4f('color', [0, 0, 1, 1])
    material3.set_parameter4f('color', [0, 1, 1, 1])

    box1 = base.Geometry.create(GEOMETRY_TYPE_OPAQUE)
    box1.put_feature(presets.OpaqueRenderingStage.ROLE_DEFAULT_MESH, box_mesh)
    box1.put_feature(presets.OpaqueRenderingStage.ROLE_DEFAULT_MATERIAL, material1)
    box1.local_transform = base.math.translation4f(0, +box_offset, 0) @ base.math.rotation4f([0, 0, 1], base.math.deg2rad(45)) # top
    root.attach_child(box1)

    box2 = base.Geometry.create(GEOMETRY_TYPE_OPAQUE)
    box2.put_feature(presets.OpaqueRenderingStage.ROLE_DEFAULT_MESH, box_mesh)
    box2.put_feature(presets.OpaqueRenderingStage.ROLE_DEFAULT_MATERIAL, material2)
    box2.local_transform = base.math.translation4f(+box_offset, 0, -20) @ base.math.rotation4f([0, 0, 1], base.math.deg2rad(45)) # right
    root.attach_child(box2)

    box3 = base.Geometry.create(GEOMETRY_TYPE_OPAQUE)
    box3.put_feature(presets.OpaqueRenderingStage.ROLE_DEFAULT_MESH, box_mesh)
    box3.put_feature(presets.OpaqueRenderingStage.ROLE_DEFAULT_MATERIAL, material3)
    box3.local_transform = base.math.translation4f(-box_offset, 0, +20) @ base.math.rotation4f([0, 0, 1], base.math.deg2rad(45)) #left
    root.attach_child(box3)

    box_mesh .release()
    material1.release()
    material2.release()
    material3.release()

    data = np.ones((100, 100, 100), bool)
    data_center = np.subtract(data.shape, 1) // 2
    data[tuple(data_center)] = False
    data = ndi.distance_transform_edt(data)
    data = np.exp(-(data ** 2) / (2 * (25 ** 2)))

    grid_helper = VolumeGridClass.create(data.shape)
    grid_helper.load_data(data)
    volume = grid_helper.create_node(GEOMETRY_TYPE_VOLUME, helpers.Dimensions([100, 100, 100]))
    root.attach_child(volume)

    # ============================
    # presets.FrameRendererHelper
    # ============================

    rs_opaque   = presets.OpaqueRenderingStage.create(GEOMETRY_TYPE_OPAQUE)
    rs_occluded = presets.OccludedRenderingStage.create()
    rs_dvr = presets.DVRStage.create(GEOMETRY_TYPE_VOLUME)
    rs_dvr.translucency = 0
    rs_dvr.write_color_map(0.2, 1, [1.0, 0.0, 0.0, 0.0], [1.0, 1.0, 0.0, 0.2])

    ctx = egl.Context.create()
    surface = base.Surface.create(ctx, w, h)
    renderer = base.FrameRenderer.create(ctx, w, h)

    renderer_helper = helpers.FrameRendererHelper(renderer)
    renderer_helper.add_stage(rs_dvr)
    renderer_helper.add_stage(rs_opaque)
    renderer_helper.add_stage(rs_occluded)
    renderer_helper.commit()

    surface.begin()
    renderer.render(cam)
    result = surface.end()
    test_tools.assert_rendering(f'helpers.FrameRendererHelper.{result_suffix}', result)

    # ============================
    # Clean up
    # ============================

    grid_helper.free()
    root.free()
    surface.free()
    renderer.free()
    ctx.free()

test_helpers(helpers.VolumeGrid_UInt16Intensity, 'uint16')
test_helpers(helpers.VolumeGrid_UInt8Intensity , 'uint8' )

