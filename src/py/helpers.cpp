#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>

namespace py = pybind11;

using namespace pybind11::literals; // enables the _a literal

#include <Carna/base/Color.h>
#include <Carna/base/Geometry.h>
#include <Carna/base/BufferedHUVolume.h>
#include <Carna/helpers/FrameRendererHelper.h>
#include <Carna/helpers/PointMarkerHelper.h>
#include <Carna/helpers/VolumeGridHelper.h>
#include <Carna/py/py.h>

using namespace Carna::base;
using namespace Carna::helpers;

#include <iostream>
void FrameRendererHelper__commit( FrameRendererHelper< >* self, bool clear )
{
    try
    {
        self->commit( clear );
    }
    catch( const CarnaException& ex )
    {
        std::cout << ex.message << std::endl;
        std::cout << ex.details << std::endl;
    }
}

PYBIND11_MODULE(helpers, m)
{

    const static auto PointMarkerHelper__DEFAULT_POINT_SIZE = ([](){ return PointMarkerHelper::DEFAULT_POINT_SIZE; })();

    py::class_< PointMarkerHelper >( m, "PointMarkerHelper" )
        .def_static( "create", []( unsigned int geometryType, unsigned int pointSize )
        {
            return new PointMarkerHelper( geometryType, pointSize );
        }
        , py::return_value_policy::reference, "geometryType"_a, "pointSize"_a = PointMarkerHelper__DEFAULT_POINT_SIZE )
        .def_static( "create_ext", []( unsigned int geometryType, unsigned int meshRole, unsigned int materialRole, unsigned int pointSize )
        {
            return new PointMarkerHelper( geometryType, meshRole, materialRole, pointSize );
        }
        , py::return_value_policy::reference, "geometryType"_a, "meshRole"_a, "materialRole"_a, "pointSize"_a = PointMarkerHelper__DEFAULT_POINT_SIZE )
        .def_readonly_static( "DEFAULT_POINT_SIZE", &PointMarkerHelper__DEFAULT_POINT_SIZE )
        .def( "release_geometry_features", &PointMarkerHelper::releaseGeometryFeatures )
        .def( "create_point_marker", []( const PointMarkerHelper* helper, unsigned int* pointSize, const math::Vector4f* color )
        {
            if( pointSize == nullptr && color == nullptr ) return helper->createPointMarker();
            if( pointSize == nullptr && color != nullptr ) return helper->createPointMarker( *color );
            if( pointSize != nullptr && color == nullptr ) return helper->createPointMarker( *pointSize );
            if( pointSize != nullptr && color != nullptr ) return helper->createPointMarker( *color, *pointSize );
        }
        , py::return_value_policy::reference, "pointSize"_a = nullptr, "color"_a = nullptr )
        .def_readonly( "geometry_type", &PointMarkerHelper::geometryType )
        .def_readonly( "mesh_role", &PointMarkerHelper::meshRole )
        .def_readonly( "material_role", &PointMarkerHelper::materialRole )
        .def_readonly( "point_size", &PointMarkerHelper::pointSize )
        .def_static( "reset_default_color", &PointMarkerHelper::resetDefaultColor )
        .DEF_FREE( PointMarkerHelper );

    py::class_< VolumeGridHelperBase::Spacing >( m, "Spacing" )
        .def( py::init< const math::Vector3f& >() );

    py::class_< VolumeGridHelperBase::Dimensions >( m, "Dimensions" )
        .def( py::init< const math::Vector3f& >() );

    py::class_< VolumeGridHelper< HUVolumeUInt16 > >( m, "UInt12VolumeGridHelper" )
        .def_static( "create", []( const math::Vector3ui& nativeResolution, std::size_t maxSegmentBytesize )
        {
            return new VolumeGridHelper< HUVolumeUInt16 >( nativeResolution, maxSegmentBytesize );
        }
        , py::return_value_policy::reference, "nativeResolution"_a, "maxSegmentBytesize"_a = ([](){ return VolumeGridHelperBase::DEFAULT_MAX_SEGMENT_BYTESIZE; })() )
        .def( "load_data", []( VolumeGridHelper< HUVolumeUInt16 >* self, py::array_t< double > data )
        {
            const auto rawData = data.unchecked< 3 >();
            const auto voxel2huv = [ &rawData ]( const math::Vector3ui voxel ) -> HUV
            {
                return Carna::py::float2huv( rawData( voxel.x(), voxel.y(), voxel.z() ) );
            };
            return self->loadData( voxel2huv );
        }
        , "data"_a )
        .def( "create_node", py::overload_cast< unsigned int, const VolumeGridHelperBase::Spacing& >( &VolumeGridHelper< HUVolumeUInt16 >::createNode, py::const_ ), py::return_value_policy::reference )
        .def( "create_node", py::overload_cast< unsigned int, const VolumeGridHelperBase::Dimensions& >( &VolumeGridHelper< HUVolumeUInt16 >::createNode, py::const_ ), py::return_value_policy::reference )
        .def( "release_geometry_features", &VolumeGridHelper< HUVolumeUInt16 >::releaseGeometryFeatures )
        .DEF_FREE( VolumeGridHelper< HUVolumeUInt16 > );

    py::class_< FrameRendererHelper< > >( m, "FrameRendererHelper" )
        .def( py::init< RenderStageSequence& >() )
        .def( "add_stage", &FrameRendererHelper< >::operator<< )
        .def( "reset", &FrameRendererHelper< >::reset )
        //.def( "commit", &FrameRendererHelper< >::commit, "clear"_a = true );
        .def( "commit", &FrameRendererHelper__commit, "clear"_a = true );

}

