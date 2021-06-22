import atexit
import carna
import carna.base
import carna.egl
import carna.presets
import carna.helpers
import numpy as np
import warnings


version    = carna.version
py_version = carna.py_version


# Create the OpenGL context when module is loaded
ctx = carna.egl.Context.create()

# Release the OpenGL context when module is unloaded
@atexit.register
def shutdown():
    ctx.free()


class SpatialWrapper:
    def __init__(self, spatial):
        self._ = spatial

    def translate(self, *args):
        self._.local_transform = self._.local_transform @ carna.base.math.translation4f(*args)
        return self

    def rotate(self, axis, amount, units='rad'):
        assert units in ('rad', 'deg')
        axis = axis / np.linalg.norm(axis)
        if units == 'deg': amount = carna.base.math.deg2rad(amount)
        self._.local_transform = self._.local_transform @ carna.base.math.rotation4f(axis, amount)
        return self

    def scale(self, *args):
        self._.local_transform = self._.local_transform @ carna.base.math.scaling4f(*args)
        return self


class VolumeWrapper(SpatialWrapper):
    def __init__(self, volume, data_shape, dimensions=None, spacing=None):
        assert (dimensions is None) != (spacing is None)
        super().__init__(volume)
        if dimensions is None: dimensions = spacing * (np.array(data_shape) - 1)[None, :]
        self.dimensions = dimensions
        self.data_shape = data_shape

    def map_normalized_coordinates(self, coordinates):
        """Maps normalized coordinates to volume coordinates.
        """
        coordinates = np.asarray(coordinates)
        assert coordinates.ndim == 2 and coordinates.shape[1] == 3
        return (coordinates - 0.5) * self.dimensions

    def map_voxel_coordinates(self, coordinates):
        """Maps voxel coordinates to volume coordinates.
        """
        coordinates = np.asarray(coordinates)
        assert coordinates.ndim == 2 and coordinates.shape[1] == 3
        coordinates = coordinates / np.subtract(self.data_shape, 1)[None, :]
        return self.map_normalized_coordinates(coordinates)


def deduce_volume_format(dtype, dtype_fallback='float16'):
    dtype = str(np.dtype(dtype))
    if dtype in ('float32', 'float64'):
        warnings.warn(f'Unsupported data type: {dtype} (will be treated as {dtype_fallback})')
        dtype = dtype_fallback
    return {
        'uint8'  : 'VolumeGrid_UInt8Intensity',
        'uint16' : 'VolumeGrid_UInt16Intensity',
        'float16': 'VolumeGrid_UInt16Intensity',
    }[dtype]


def preprocess_mask_data(data):
    dtype = str(np.dtype(data.dtype))
    if dtype == 'bool': return 'VolumeGrid_UInt8Intensity', data
    if (dtype.startswith('int') or dtype.startswith('uint')):
        if data.max() < (1 << 8):
            return 'VolumeGrid_UInt8Intensity', (data / data.max()).clip(0, 1)
        if data.max() < (1 << 16):
            return 'VolumeGrid_UInt16Intensity', (data / data.max()).clip(0, 1)
    if dtype.startswith('float'):
        return 'VolumeGrid_UInt16Intensity', (data / data.max()).clip(0, 1)
    else:
        raise ValueError(f'Unsupported mask format')


class SingleFrameContext:

    GEOMETRY_TYPE_OPAQUE = 0
    GEOMETRY_TYPE_VOLUME = 1
    GEOMETRY_TYPE_PLANE  = 2
    GEOMETRY_TYPE_MASK   = 3

    def __init__(self, shape, near, far, fov=None, ortho=None,
            max_segment_bytesize=carna.helpers.VolumeGridHelperBase.DEFAULT_MAX_SEGMENT_BYTESIZE):
        assert (fov is None) != (ortho is None), f'Either "fov" or "ortho" musst be supplied (fov={fov}, ortho={ortho})'
        assert ortho is None or (isinstance(ortho, tuple) and len(ortho) == 4), str(ortho)
        self.result = None
        self.shape  = shape
        self.near   = near
        self.far    = far
        self.fov    = fov
        self.ortho  = ortho
        self.max_segment_bytesize = max_segment_bytesize

    def __enter__(self):
        self. result       = None
        self._camera       = carna.base.Camera.create()
        self._renderer     = carna.base.FrameRenderer.create(ctx, self.shape[1], self.shape[0])
        self._helper       = carna.helpers.FrameRendererHelper(self._renderer)
        self._extra_stages = {}
        self._points       = None
        self._root         = carna.base.Node.create()
        self._stages       = dict()
        self._grids        = []
        self._meshes       = []
        self._materials    = []
        if self.fov is not None:
            self._camera.projection = carna.base.math.frustum4f(carna.base.math.deg2rad(self.fov), self.shape[0] / self.shape[1], self.near, self.far)
        else:
            self._camera.projection = carna.base.math.ortho4f(*self.ortho, self.near, self.far)
        self._root.attach_child(self._camera)
        return self

    def _get_stage(self, stage_type, *create_args):
        if stage_type not in self._stages:
            stage = stage_type.create(*create_args)
            self._stages[stage_type] = stage
            if stage_type is not carna.presets.MaskRenderingStage:
                self._helper.add_stage(stage)
        return self._stages[stage_type]

    def _render(self):
        surface = carna.base.Surface.create(ctx, self._renderer.width, self._renderer.height)
        surface.begin()
        self._renderer.render(self._camera)
        return surface.end()

    def _append_extra_render_stages(self, current_render_time):
        assert current_render_time in ('before', 'after')
        for stage, scheduled_render_time in self._extra_stages.items():
            if scheduled_render_time == current_render_time:
                self._renderer.append_stage(stage)

    def __exit__(self, ex_type, ex_value, ex_traceback):
        self._append_extra_render_stages('before')
        self._helper.commit(False)
        self._append_extra_render_stages('after')
        self.result = self._render()
        for material in self._materials: material.release()
        for mesh in self._meshes: mesh.release()
        for grid in self._grids: grid.free()
        if self._points is not None: self._points.free()
        self._renderer.free()
        self._root.free()

    @property
    def camera(self):
        return SpatialWrapper(self._camera)

    def _get_parent(self, parent):
        if isinstance(parent, str) and parent == 'root': return self._root
        elif isinstance(parent, SpatialWrapper): return parent._
        else: raise ValueError('parent must be either "root" or SpatialWrapper instance')

    def volume(self, data, dimensions=None, spacing=None, normals=False, fmt_hint=None, parent='root'):
        assert data.ndim == 3
        assert (dimensions is None) != (spacing is None)
        if dimensions is not None: size_hint = carna.helpers.Dimensions(dimensions)
        if spacing    is not None: size_hint = carna.helpers.Spacing   (spacing)
        grid_helper_type = deduce_volume_format(data.dtype if fmt_hint is None else fmt_hint)
        if normals: grid_helper_type += '_Int8Normal'
        grid = getattr(carna.helpers, grid_helper_type).create(data.shape, self.max_segment_bytesize)
        grid.load_data(data)
        volume = grid.create_node(SingleFrameContext.GEOMETRY_TYPE_VOLUME, size_hint)
        pivot = carna.base.Node.create()
        pivot.attach_child(volume)
        self._get_parent(parent).attach_child(pivot)
        self._grids.append(grid)
        return VolumeWrapper(pivot, data.shape, dimensions, spacing)

    def masks(self, flavor='default', **kwargs):
        """Configures the mask rendering stage.
        """
        assert flavor in ('regions', 'regions-on-top', 'borders-on-top', 'borders-in-background')
        mr = self._get_stage(carna.presets.MaskRenderingStage, SingleFrameContext.GEOMETRY_TYPE_MASK)
        for key, val in kwargs.items():
            setattr(mr, key, val)
        if flavor == 'default' and mr not in self._extra_stages: flavor = 'regions'
        if flavor == 'regions':
            render_time       = 'before'
            mr.render_borders =  False
        if flavor == 'regions-on-top':
            render_time       = 'after'
            mr.render_borders =  False
        if flavor == 'borders-on-top':
            render_time       = 'after'
            mr.render_borders =  True
        if flavor == 'borders-in-background':
            render_time       = 'before'
            mr.render_borders =  True
        self._extra_stages[mr] = render_time
        return mr

    def mask(self, data, *args, dimensions=None, spacing=None, parent='root', **kwargs):
        mr = self.masks(*args, **kwargs) ## require mask rendering stage
        assert (dimensions is None) != (spacing is None)
        if dimensions is not None: size_hint = carna.helpers.Dimensions(dimensions)
        if spacing    is not None: size_hint = carna.helpers.Spacing   (spacing)
        grid_helper_type, data = preprocess_mask_data(data)
        grid = getattr(carna.helpers, grid_helper_type).create(data.shape, self.max_segment_bytesize)
        grid.intensities_role = mr.mask_role
        grid.load_data(data)
        volume = grid.create_node(SingleFrameContext.GEOMETRY_TYPE_MASK, size_hint)
        pivot = carna.base.Node.create()
        pivot.attach_child(volume)
        self._get_parent(parent).attach_child(pivot)
        self._grids.append(grid)
        return VolumeWrapper(pivot, data.shape, dimensions, spacing)

    def plane(self, *args, parent='root'):
        self.planes() ## require cutting planes rendering stage
        plane = carna.base.Geometry.create(SingleFrameContext.GEOMETRY_TYPE_PLANE)
        plane.local_transform = carna.base.math.plane4f(*args)
        self._get_parent(parent).attach_child(plane)
        return SpatialWrapper(plane)

    def planes(self):
        return self._get_stage(carna.presets.CuttingPlanesStage, SingleFrameContext.GEOMETRY_TYPE_VOLUME, SingleFrameContext.GEOMETRY_TYPE_PLANE)

    def opaque(self):
        return self._get_stage(carna.presets.OpaqueRenderingStage, SingleFrameContext.GEOMETRY_TYPE_OPAQUE)

    def occluded(self):
        return self._get_stage(carna.presets.OccludedRenderingStage)

    def mip(self, layers=[(0, 1, (1,1,1,1))], **kwargs):
        mip = self._get_stage(carna.presets.MIPStage, SingleFrameContext.GEOMETRY_TYPE_VOLUME)
        mip.clear_layers()
        for layer in layers:
            mip.append_layer(carna.presets.MIPLayer.create(*layer))
        for key, val in kwargs.items():
            setattr(mip, key, val)
        return mip

    def dvr(self, translucency=0, color_map=[(0, 1, (1,1,1,0), (1,1,1,1))], **kwargs):
        dvr = self._get_stage(carna.presets.DVRStage, SingleFrameContext.GEOMETRY_TYPE_VOLUME)
        dvr.translucency = translucency
        dvr.clear_color_map()
        for color_map_entry in color_map:
            dvr.write_color_map(*color_map_entry)
        for key, val in kwargs.items():
            setattr(dvr, key, val)
        return dvr

    def dots(self, data, color, size, parent='root'):
        opaque = self.opaque()
        if self._points is None: self._points = carna.helpers.PointMarkerHelper.create(SingleFrameContext.GEOMETRY_TYPE_OPAQUE)
        dots = []
        for location in data:
            dot = self._points.create_point_marker(size, color)
            dot.local_transform = carna.base.math.translation4f(*location)
            self._get_parent(parent).attach_child(dot)
            dots.append(SpatialWrapper(dot))
        return dots

    def material(self, color, shader='solid'):
        material = carna.base.Material.create(shader)
        material.set_parameter4f('color', color)
        self._materials.append(material)
        return material

    def box(self, width, height, depth):
        box = carna.base.create_box(width, height, depth)
        self._meshes.append(box)
        return box

    def ball(self, radius, degree=3):
        ball = carna.base.create_ball(radius, degree)
        self._meshes.append(ball)
        return ball

    def mesh(self, mesh, material, parent='root'):
        self.opaque() ## require opaque rendering stage
        geom = carna.base.Geometry.create(SingleFrameContext.GEOMETRY_TYPE_OPAQUE)
        geom.put_feature(carna.presets.OpaqueRenderingStage.ROLE_DEFAULT_MESH, mesh)
        geom.put_feature(carna.presets.OpaqueRenderingStage.ROLE_DEFAULT_MATERIAL, material)
        self._get_parent(parent).attach_child(geom)
        return SpatialWrapper(geom)

    def meshes(self, mesh, material, locations, parent='root'):
        geoms = []
        for loc in locations:
            geom = self.mesh(mesh, material, parent=parent).translate(*loc)
            geoms.append(geom)
        return geoms


