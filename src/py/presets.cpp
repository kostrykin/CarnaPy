#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>

namespace py = pybind11;

using namespace pybind11::literals; // enables the _a literal

#include <Carna/base/Color.h>
#include <Carna/base/GLContext.h>
#include <Carna/base/ManagedMesh.h>
#include <Carna/presets/CuttingPlanesStage.h>
#include <Carna/presets/DRRStage.h>
#include <Carna/presets/DVRStage.h>
#include <Carna/presets/MIPLayer.h>
#include <Carna/presets/MIPStage.h>
#include <Carna/presets/OccludedRenderingStage.h>
#include <Carna/presets/OpaqueRenderingStage.h>
#include <Carna/py/py.h>

using namespace Carna::base;
using namespace Carna::presets;

void CuttingPlanesStage__set_windowing( CuttingPlanesStage* self, float min, float max )
{
    const auto huvMin = Carna::py::float2huv( min );
    const auto huvMax = Carna::py::float2huv( max );
    const auto huvLevel = (huvMin + huvMax) / 2;
    const auto huvWidth = (huvMax - huvMin) / 2;
    self->setWindowingLevel( static_cast< HUV >( huvLevel ) );
    self->setWindowingWidth( static_cast< unsigned int >( huvWidth ) );
}

PYBIND11_MODULE(presets, m)
{

    py::class_< OpaqueRenderingStage, RenderStage >( m, "OpaqueRenderingStage" )
        .def_static( "create", []( unsigned int geometryType )
        {
            return new OpaqueRenderingStage( geometryType );
        }
        , py::return_value_policy::reference, "geometryType"_a )
        .def_property_readonly_static( "ROLE_DEFAULT_MATERIAL", []( py::object ) { return OpaqueRenderingStage::ROLE_DEFAULT_MATERIAL; } )
        .def_property_readonly_static( "ROLE_DEFAULT_MESH", []( py::object ) { return OpaqueRenderingStage::ROLE_DEFAULT_MESH; } );

    py::class_< OccludedRenderingStage, RenderStage >( m, "OccludedRenderingStage" )
        .def_static( "create", []()
        {
            return new OccludedRenderingStage();
        }
        , py::return_value_policy::reference )
        .def_property_readonly_static( "DEFAULT_OCCLUSION_TRANSLUCENCY", []( py::object ) { return OccludedRenderingStage::DEFAULT_OCCLUSION_TRANSLUCENCY; } )
        .def_property( "occlusion_translucency", &OccludedRenderingStage::occlusionTranslucency, &OccludedRenderingStage::setOcclusionTranslucency )
        .def( "disable_all_stages", &OccludedRenderingStage::disableAllStages )
        .def( "enable_stage", &OccludedRenderingStage::enableStage )
        .def( "disable_stage", &OccludedRenderingStage::disableStage )
        .def( "is_stage_enabled", &OccludedRenderingStage::isStageEnabled );

    py::class_< VolumeRenderingStage, RenderStage >( m, "VolumeRenderingStage" )
        .def_property( "sample_rate", &VolumeRenderingStage::sampleRate, &VolumeRenderingStage::setSampleRate );

    const static auto MIPLayer__LAYER_FUNCTION_ADD     = ([](){ return MIPLayer::LAYER_FUNCTION_ADD;     })();
    const static auto MIPLayer__LAYER_FUNCTION_REPLACE = ([](){ return MIPLayer::LAYER_FUNCTION_REPLACE; })();

    py::class_< MIPLayer >( m, "MIPLayer" )
        .def_static( "create", []( float min, float max, const math::Vector4f& color, bool maxExclusive, const BlendFunction& function )
        {
            const HUV huFirst = Carna::py::float2huv( min );
            const HUV huLast  = Carna::py::float2huv( max );
            return new MIPLayer( huFirst, huLast + (maxExclusive && huLast > huFirst ? -1 : 0), color, function );
        }
        , py::return_value_policy::reference, "min"_a, "max"_a, "color"_a, "maxExclusive"_a = false, "function"_a = MIPLayer__LAYER_FUNCTION_REPLACE )
        .def_readonly_static( "LAYER_FUNCTION_ADD", &MIPLayer__LAYER_FUNCTION_ADD )
        .def_readonly_static( "LAYER_FUNCTION_REPLACE", &MIPLayer__LAYER_FUNCTION_REPLACE )
        .DEF_FREE( MIPLayer );

    py::class_< MIPStage, VolumeRenderingStage >( m, "MIPStage" )
        .def_static( "create", []( unsigned int geometryType )
        {
            return new MIPStage( geometryType );
        }
        , py::return_value_policy::reference, "geometryType"_a )
        .def_property_readonly_static( "ROLE_VOLUME", []( py::object ) { return MIPStage::ROLE_HU_VOLUME; } )
        .def( "ascend_layer", &MIPStage::ascendLayer )
        .def( "append_layer", &MIPStage::appendLayer )
        .def( "remove_layer", &MIPStage::removeLayer )
        .def_property_readonly( "layers_count", &MIPStage::layersCount )
        .def( "layer", py::overload_cast< std::size_t >( &MIPStage::layer, py::const_ ) )
        .def( "clear_layers", &MIPStage::clearLayers );

    py::class_< CuttingPlanesStage, RenderStage >( m, "CuttingPlanesStage" )
        .def_static( "create", []( unsigned int volumeGeometryType, unsigned int planeGeometryType )
        {
            const auto cps = new CuttingPlanesStage( volumeGeometryType, planeGeometryType );
            CuttingPlanesStage__set_windowing( cps, 0.f, 1.f );
            return cps;
        }
        , py::return_value_policy::reference, "volumeGeometryType"_a, "planeGeometryType"_a )
        .def_property_readonly_static( "ROLE_VOLUME", []( py::object ) { return CuttingPlanesStage::ROLE_HU_VOLUME; } )
        .def_property_readonly( "min_intensity", []( const CuttingPlanesStage* self )
        {
            return Carna::py::huv2float( self->minimumHUV() );
        } )
        .def_property_readonly( "max_intensity", []( const CuttingPlanesStage* self )
        {
            return Carna::py::huv2float( self->maximumHUV() );
        } )
        .def( "set_windowing", &CuttingPlanesStage__set_windowing )
        .def_property( "rendering_inverse", &CuttingPlanesStage::isRenderingInverse, &CuttingPlanesStage::setRenderingInverse );

    py::class_< DVRStage, VolumeRenderingStage >( m, "DVRStage" )
        .def_static( "create", []( unsigned int geometryType )
        {
            return new DVRStage( geometryType );
        }
        , py::return_value_policy::reference, "geometryType"_a )
        .def_property_readonly_static( "DEFAULT_TRANSLUCENCY", []( py::object ) { return DVRStage::DEFAULT_TRANSLUCENCE; } )
        .def_property_readonly_static( "DEFAULT_DIFFUSE_LIGHT", []( py::object ) { return DVRStage::DEFAULT_DIFFUSE_LIGHT; } )
        .def_property_readonly_static( "ROLE_VOLUME", []( py::object ) { return DVRStage::ROLE_HU_VOLUME; } )
        .def_property_readonly_static( "ROLE_NORMALS", []( py::object ) { return DVRStage::ROLE_NORMALS; } )
        .def_property( "translucency", &DVRStage::translucence, &DVRStage::setTranslucence )
        .def_property( "diffuse_light", &DVRStage::diffuseLight, &DVRStage::setDiffuseLight )
        .def( "clear_color_map", &DVRStage::clearColorMap )
        .def( "write_color_map", []( DVRStage* self, float min, float max, const math::Vector4f& color1, const math::Vector4f& color2, bool maxExclusive )
        {
            const HUV huFirst = Carna::py::float2huv( min );
            const HUV huLast  = Carna::py::float2huv( max );
            self->writeColorMap( huFirst, huLast + ( maxExclusive && huLast > huFirst ? -1 : 0 ), color1, color2 );
        }
        , "min"_a, "max"_a, "color1"_a, "color2"_a, "maxExclusive"_a = false );

}

