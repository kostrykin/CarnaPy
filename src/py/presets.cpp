#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>

namespace py = pybind11;

using namespace pybind11::literals; // enables the _a literal

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

    const static auto MIPLayer__LAYER_FUNCTION_ADD     = ([](){ return MIPLayer::LAYER_FUNCTION_ADD;     })();
    const static auto MIPLayer__LAYER_FUNCTION_REPLACE = ([](){ return MIPLayer::LAYER_FUNCTION_REPLACE; })();

    py::class_< MIPLayer >( m, "MIPLayer" )
        .def_static( "create", []( float min, float max, const math::Vector4f& color, bool maxExclusive, const BlendFunction& function )
        {
            const HUV huvMin = Carna::py::float2huv( min );
            const HUV huvMax = Carna::py::float2huv( max );
            return new MIPLayer( huvMin, huvMax + (maxExclusive && huvMax > huvMin ? -1 : 0), color, function );
        }
        , py::return_value_policy::reference, "min"_a, "max"_a, "color"_a, "maxExclusive"_a = false, "function"_a = MIPLayer__LAYER_FUNCTION_REPLACE )
        .def_readonly_static( "LAYER_FUNCTION_ADD", &MIPLayer__LAYER_FUNCTION_ADD )
        .def_readonly_static( "LAYER_FUNCTION_REPLACE", &MIPLayer__LAYER_FUNCTION_REPLACE )
        .DEF_FREE( MIPLayer );

    py::class_< MIPStage, RenderStage >( m, "MIPStage" )
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

}

