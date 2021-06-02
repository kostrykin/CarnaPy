#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>

namespace py = pybind11;

using namespace pybind11::literals; // enables the _a literal

#include <Carna/base/GLContext.h>
#include <Carna/base/ManagedMesh.h>
#include <Carna/presets/CuttingPlanesStage.h>
#include <Carna/presets/DRRStage.h>
#include <Carna/presets/DVRStage.h>
#include <Carna/presets/MIPStage.h>
#include <Carna/presets/OccludedRenderingStage.h>
#include <Carna/presets/OpaqueRenderingStage.h>

using namespace Carna::base;
using namespace Carna::presets;

PYBIND11_MODULE(presets, m)
{

    py::class_< OpaqueRenderingStage, RenderStage >( m, "OpaqueRenderingStage" )
        .def_static( "create", []( unsigned int geometryType ) {
            return new OpaqueRenderingStage( geometryType );
        }
        , py::return_value_policy::reference, "geometryType"_a )
        .def_property_readonly_static( "ROLE_DEFAULT_MATERIAL", []( py::object ) { return OpaqueRenderingStage::ROLE_DEFAULT_MATERIAL; } )
        .def_property_readonly_static( "ROLE_DEFAULT_MESH", []( py::object ) { return OpaqueRenderingStage::ROLE_DEFAULT_MESH; } );

}

