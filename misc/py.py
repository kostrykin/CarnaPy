import atexit
import .base
import .egl

ctx = egl.Context.create()

@atexit.register
def shutdown():
    ctx.free()

