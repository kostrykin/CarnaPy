#include <Carna/egl/Context.h>
#include <EGL/egl.h>
#include <cstdlib>

// see: https://developer.nvidia.com/blog/egl-eye-opengl-visualization-without-x-server/

namespace Carna
{

namespace egl
{



// ----------------------------------------------------------------------------------
// REPORT_EGL_ERROR
// ----------------------------------------------------------------------------------

#ifndef NO_EGL_ERROR_CHECKING

    #include <Carna/base/CarnaException.h>

    #define REPORT_EGL_ERROR { \
            const unsigned int err = eglGetError(); \
            CARNA_ASSERT_EX( err == EGL_SUCCESS, "EGL Error State in " \
                << __func__ \
                << " [" << err << "] (" << __FILE__ << ":" << __LINE__ << ")" ); }
#else

    #define REPORT_EGL_ERROR

#endif



// ----------------------------------------------------------------------------------
// CONFIG_ATTRIBS
// ----------------------------------------------------------------------------------

static const EGLint CONFIG_ATTRIBS[] =
{
    EGL_SURFACE_TYPE, EGL_PBUFFER_BIT,
    EGL_BLUE_SIZE, 8,
    EGL_GREEN_SIZE, 8,
    EGL_RED_SIZE, 8,
    EGL_DEPTH_SIZE, 8,
    EGL_RENDERABLE_TYPE, EGL_OPENGL_BIT,
    EGL_NONE
};



// ----------------------------------------------------------------------------------
// PBUFFER_ATTRIBS
// ----------------------------------------------------------------------------------

static const EGLint PBUFFER_ATTRIBS[] =
{
    EGL_WIDTH, 0,
    EGL_HEIGHT, 0,
    EGL_NONE
};



// ----------------------------------------------------------------------------------
// Context :: Details
// ----------------------------------------------------------------------------------

struct Context::Details
{
    EGLDisplay eglDpy;
    EGLSurface eglSurf;
    EGLContext eglCtx;

    void activate() const;
};


void Context::Details::activate() const
{
    eglMakeCurrent( this->eglDpy, this->eglSurf, this->eglSurf, this->eglCtx );
    REPORT_EGL_ERROR;
}



// ----------------------------------------------------------------------------------
// Context
// ----------------------------------------------------------------------------------

Context::Context( Details* _pimpl )
    : base::GLContext( false )
    , pimpl( _pimpl )
{
}


Context* Context::create()
{
    unsetenv( "DISPLAY" ); // see https://stackoverflow.com/q/67885750/1444073

    Details* const pimpl = new Details();
    pimpl->eglDpy = eglGetDisplay( EGL_DEFAULT_DISPLAY );
    EGLint major, minor;
    eglInitialize( pimpl->eglDpy, &major, &minor );
    
    eglBindAPI( EGL_OPENGL_API );
    REPORT_EGL_ERROR;

    EGLint numConfigs;
    EGLConfig eglCfg;

    eglChooseConfig( pimpl->eglDpy, CONFIG_ATTRIBS, &eglCfg, 1, &numConfigs );

    pimpl->eglSurf = eglCreatePbufferSurface( pimpl->eglDpy, eglCfg, PBUFFER_ATTRIBS );
    CARNA_ASSERT( pimpl->eglSurf != EGL_NO_SURFACE );

    pimpl->eglCtx  = eglCreateContext( pimpl->eglDpy, eglCfg, EGL_NO_CONTEXT, NULL );
    CARNA_ASSERT( pimpl->eglCtx != EGL_NO_CONTEXT );

    pimpl->activate();
    return new Context( pimpl );
}


Context::~Context()
{
    eglTerminate( pimpl->eglDpy );
}


void Context::activate() const
{
    pimpl->activate();
}



}  // namespace Carna :: egl

}  // namespace Carna

