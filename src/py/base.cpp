#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>

namespace py = pybind11;

using namespace pybind11::literals; // enables the _a literal

#include <Carna/base/FrameRenderer.h>
#include <Carna/base/Node.h>

using namespace Carna::base;

template< typename T >
void _py_free( T* ptr )
{
    delete ptr;
}

// see: https://pybind11.readthedocs.io/en/stable/advanced/misc.html#generating-documentation-using-sphinx

PYBIND11_MODULE(base, m)
{

    m.def( "free", &_py_free< Spatial > );

    py::class_< Spatial >( m, "Spatial" )
        .def( "detach_from_parent", &Spatial::detachFromParent, py::return_value_policy::reference )
        .def_property_readonly( "has_parent", &Spatial::hasParent )
        .def_property_readonly( "parent", py::overload_cast<>( &Spatial::parent, py::const_ ) )
        .def_property( "movable", &Spatial::isMovable, &Spatial::setMovable )
        .def_property( "tag", &Spatial::tag, &Spatial::setTag )
        .def_readwrite( "local_transform", &Spatial::localTransform );

    py::class_< Node, Spatial >( m, "Node" )
        .def_static( "create", []( const std::string& tag ) { return new Node( tag ); }, py::return_value_policy::reference, "tag"_a = "" )
        .def( "attach_child", &Node::attachChild )
        .def( "detach_child", &Node::detachChild, py::return_value_policy::reference )
        .def( "has_child", &Node::hasChild )
        .def( "delete_all_children", &Node::deleteAllChildren )
        .def( "children", &Node::children );
}

