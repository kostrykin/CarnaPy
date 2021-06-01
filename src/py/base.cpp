#include <boost/python.hpp>
#include <Carna/base/FrameRenderer.h>
#include <Carna/base/Node.h>

using namespace boost::python;
using namespace Carna::base;

// See also:
// https://www.boost.org/doc/libs/1_63_0/libs/python/doc/html/tutorial/index.html
// https://wiki.python.org/moin/boost.python/HowTo
// https://stackoverflow.com/questions/24568501/exposing-c-functions-that-return-pointer-using-boost-python
// https://doc.nektar.info/developerguide/5.0.2/developer-guidese55.html
// https://www.boost.org/doc/libs/1_58_0/libs/python/doc/v2/class.html
// https://www.boost.org/doc/libs/1_60_0/libs/python/doc/html/faq/how_can_i_wrap_a_function_which0.html
// https://stackoverflow.com/questions/16731115/how-to-debug-a-python-segmentation-fault

void Node__attachChild( Node& self, std::auto_ptr< Spatial > child )
{
    return self.attachChild( child.release() );
}

BOOST_PYTHON_MODULE(base)
{
    //class_<FrameRenderer>("FrameRenderer", init<, unsigned int, unsigned int>())
    //    .def("width", &FrameRenderer::width)
    //    .def("height", &FrameRenderer::height);

    class_< Spatial, std::auto_ptr< Spatial >, boost::noncopyable >( "Spatial", init< optional< const std::string& > >() )
        .def( "has_parent", &Spatial::hasParent )
        .def( "detach_from_parent", &Spatial::detachFromParent, return_value_policy< manage_new_object >() );
        //.def( "tag", &Spatial::tag, return_value_policy< return_by_value >() );
        //.def( "tag", &Spatial::tag, return_value_policy< copy_const_reference >() );
        //.add_property( "tag", make_function( &Spatial::tag, return_value_policy< copy_const_reference >() ), &Spatial::setTag );

    class_< Node, bases< Spatial >, std::auto_ptr< Node >, boost::noncopyable >( "Node", init< optional< const std::string& > >() )
        .def( "attach_child", &Node__attachChild )
        .def( "detach_child", &Node::detachChild, return_value_policy< manage_new_object >() )
        .def( "has_child", &Node::hasChild )
        .def( "delete_all_children", &Node::deleteAllChildren )
        .def( "children", &Node::children );
}

