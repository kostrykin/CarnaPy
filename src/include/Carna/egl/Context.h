#include <Carna/base/GLContext.h>
#include <Carna/base/noncopyable.h>

namespace Carna
{

namespace egl
{



// ----------------------------------------------------------------------------------
// Context
// ----------------------------------------------------------------------------------

class Context : public base::GLContext
{

    NON_COPYABLE

    struct Details;
    const std::unique_ptr< Details > pimpl;

    Context( Details* );

public:

    static Context* create();

    virtual ~Context();

protected:

    virtual void activate() const;

}; // Context



}  // namespace Carna :: egl

}  // namespace Carna

