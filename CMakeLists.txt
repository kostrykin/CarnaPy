cmake_minimum_required(VERSION 3.0.2)
project(CarnaPy)
include(FindPackageHandleStandardArgs)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION FALSE)

############################################

set(FULL_VERSION ${MAJOR_VERSION}.${MINOR_VERSION}.${PATCH_VERSION})
set(TARGET_NAME ${PROJECT_NAME}-${FULL_VERSION})
string(TOUPPER ${PROJECT_NAME} PROJECT_NAME_CAPS)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/carna)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/carna)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/carna)

############################################
# Set default options for this build
############################################

option(BUILD_DOC  "Build and install the API documentation" OFF)
option(BUILD_TEST "Build the unit tests" OFF)

############################################
# Macro that sets variable to default value
# only when the variable isn't defined yet
############################################

macro( option_default_to var_name default_val var_type doc_string )
    if( NOT DEFINED ${var_name} )
        set(${var_name} ${default_val})
    endif()
    set(${var_name} ${${var_name}} CACHE ${var_type} ${doc_string} FORCE)
endmacro()

############################################
# Locate Find<ModuleName>.cmake scripts
############################################

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/misc/CMake-Modules)

############################################
# Define default paths for the installation
############################################

# set default library and header destinations (relative to CMAKE_INSTALL_PREFIX)
option_default_to(INSTALL_LIBRARY_DIR "${TARGET_NAME}/carna"      String "Installation directory for libraries")
option_default_to(INSTALL_DOC_DIR     "share/doc/${PROJECT_NAME}" String "Installation directory for API documentation")

############################################
# Normalize installation paths
# (get rid of Windows-style delimiters)
############################################

file(TO_CMAKE_PATH ${INSTALL_LIBRARY_DIR} INSTALL_LIBRARY_DIR)

############################################
# Find required dependencies
############################################

# EGL
find_package(OpenGL REQUIRED COMPONENTS OpenGL EGL)
include_directories(${OPENGL_EGL_INCLUDE_DIRS})

# pybind11
find_package(pybind11 REQUIRED)

# Eigen
find_package( Eigen3 REQUIRED )
include_directories( ${EIGEN3_INCLUDE_DIR} )

# Carna
find_package( Carna ${REQUIRED_VERSION_CARNA} REQUIRED )
include_directories( ${CARNA_INCLUDE_DIR} )
set(CARNA_VERSION ${FOUND_VERSION})

############################################

configure_file( ${CMAKE_CURRENT_SOURCE_DIR}/misc/__init__.py.in
                ${CMAKE_CURRENT_BINARY_DIR}/carna/__init__.py @ONLY)

configure_file( ${CMAKE_CURRENT_SOURCE_DIR}/misc/py.py
                ${CMAKE_CURRENT_BINARY_DIR}/carna/py.py COPYONLY)

#configure_file( ${CMAKE_CURRENT_SOURCE_DIR}/src/doc/Doxyfile.in
#                ${CMAKE_CURRENT_SOURCE_DIR}/src/doc/Doxyfile @ONLY)

############################################
# Project
############################################

include_directories(${CMAKE_PROJECT_DIR}include)
include_directories(${CMAKE_PROJECT_DIR}src/include)
set( MODULES
        base
        egl
        presets
        helpers
    )
set( PRIVATE_QOBJECT_HEADERS
        ""
)
set( PRIVATE_HEADERS
        ${PRIVATE_QOBJECT_HEADERS}
    )
set( SRC
        ""
    )
set( FORMS
        ""
    )
set( RESOURCES
        ""
    )
set( DOC_SRC
        ""
#        src/doc/Doxyfile.in
#        src/doc/doc_extra.css
#        src/doc/doc_main.dox
#        src/doc/doc_version_log.dox
    )

############################################
#include_directories( ${CMAKE_CURRENT_BINARY_DIR} )
############################################

set(EXTRA_SOURCES_egl src/egl/Context.cpp)
foreach( MODULE ${MODULES} )
    pybind11_add_module(${MODULE} src/py/${MODULE}.cpp ${EXTRA_SOURCES_${MODULE}})
    target_compile_options(${MODULE} PRIVATE -fvisibility=default -fno-lto)

    SET_TARGET_PROPERTIES(${MODULE} PROPERTIES PREFIX "")
endforeach( MODULE )

add_definitions( -D${PROJECT_NAME_CAPS}_EXPORT -DNOMINMAX )

############################################
# Add dependencies to the linker
############################################

include( "misc/compiler_specific.cmake" )

foreach( MODULE ${MODULES} )
    target_link_libraries(
        ${MODULE}
        PRIVATE
        ${OPENGL_LIBRARIES}
        ${CARNA_LIBRARIES}
        OpenGL::EGL
    )

endforeach( MODULE )

############################################
# Define installation routines
############################################

install(TARGETS ${MODULES}
        RUNTIME DESTINATION ${INSTALL_LIBRARY_DIR}
        ARCHIVE DESTINATION ${INSTALL_LIBRARY_DIR}
        LIBRARY DESTINATION ${INSTALL_LIBRARY_DIR})

install(FILES
        ${CMAKE_CURRENT_BINARY_DIR}/carna/__init__.py
        ${CMAKE_CURRENT_BINARY_DIR}/carna/py.py
        DESTINATION ${INSTALL_LIBRARY_DIR})

############################################
# Process unit tests
############################################

if( BUILD_TEST )
    add_subdirectory( test )
endif()

############################################
# Doxygen API documentation
############################################

#if( BUILD_DOC )
#    add_subdirectory( src/doc )
#endif()

############################################

