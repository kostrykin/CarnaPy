#include <Carna/py/Surface.h>
#include <Carna/base/Framebuffer.h>
#include <Carna/base/GLContext.h>
#include <Carna/base/Texture.h>
#include <Carna/base/glew.h>

namespace Carna
{

namespace py
{



// ----------------------------------------------------------------------------------
// createRenderTexture
// ----------------------------------------------------------------------------------

static base::Texture< 2 >* createRenderTexture( const base::GLContext& glContext )
{
    glContext.makeCurrent();
    return base::Framebuffer::createRenderTexture();
}



// ----------------------------------------------------------------------------------
// Surface :: Details
// ----------------------------------------------------------------------------------

struct Surface::Details
{
    Details( const base::GLContext& glContext, unsigned int width, unsigned int height );

    const base::GLContext& glContext;
    const std::size_t frameSize;
    const std::unique_ptr< unsigned char[] > frame;
    const std::unique_ptr< base::Texture< 2 > > renderTexture;
    const std::unique_ptr< base::Framebuffer > fbo;
    std::unique_ptr< base::Framebuffer::Binding > fboBinding;

    void grabFrame();
};


Surface::Details::Details( const base::GLContext& glContext, unsigned int width, unsigned int height )
    : glContext( glContext )
    , frameSize( width * height * 3 )
    , frame( new unsigned char[ frameSize ] )
    , renderTexture( createRenderTexture( glContext ) )
    , fbo( new base::Framebuffer( width, height, *renderTexture ) )
{
}


void Surface::Details::grabFrame()
{
    glContext.makeCurrent();

    glReadBuffer( GL_COLOR_ATTACHMENT0_EXT );
    glReadPixels( 0, 0, this->fbo->width(), this->fbo->height(), GL_RGB, GL_UNSIGNED_BYTE, frame.get() );
}



// ----------------------------------------------------------------------------------
// Surface
// ----------------------------------------------------------------------------------

Surface::Surface( const base::GLContext& glContext, unsigned int width, unsigned int height )
    : pimpl( new Details( glContext, width, height ) )
    , glContext( glContext )
    , size( pimpl->frameSize )
{
}


Surface::~Surface()
{
    glContext.makeCurrent();
}


unsigned int Surface::width() const
{
    return pimpl->fbo->width();
}


unsigned int Surface::height() const
{
    return pimpl->fbo->height();
}


void Surface::begin() const
{
    glContext.makeCurrent();
    pimpl->fboBinding.reset( new base::Framebuffer::Binding( *pimpl->fbo ) );
}


const unsigned char* Surface::end() const
{
    pimpl->grabFrame();
    pimpl->fboBinding.reset();
    return pimpl->frame.get();
}



}  // namespace Carna :: py

}  // namespace Carna

