cmake_minimum_required(VERSION 3.0.2)
project(CarnaPy)
include(FindPackageHandleStandardArgs)

set(MAJOR_VERSION   0)
set(MINOR_VERSION   0)
set(PATCH_VERSION   1)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

############################################

set(FULL_VERSION ${MAJOR_VERSION}.${MINOR_VERSION}.${PATCH_VERSION})
set(TARGET_NAME ${PROJECT_NAME}-${FULL_VERSION})
string(TOUPPER ${PROJECT_NAME} PROJECT_NAME_CAPS)

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

# set default destination for CMake modules
#option_default_to(INSTALL_CMAKE_DIR "${CMAKE_ROOT}/Modules" String "Installation directory for CMake files")

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

# Qt
find_package( Qt5Core QUIET )
find_package( Qt5Widgets QUIET )
find_package( Qt5Gui QUIET )
find_package( Qt5OpenGL QUIET )
find_package( Qt5Xml QUIET )
if(Qt5Core_FOUND AND Qt5Widgets_FOUND AND Qt5Gui_FOUND AND Qt5OpenGL_FOUND AND Qt5Xml_FOUND)
    set(Qt5_FOUND TRUE)
    set(QT_LIBRARIES Qt5::Core Qt5::Widgets Qt5::Gui Qt5::OpenGL Qt5::Xml)
    include_directories(
            ${Qt5Core_INCLUDE_DIRS}
            ${Qt5Widgets_INCLUDE_DIRS}
            ${Qt5Gui_INCLUDE_DIRS}
            ${Qt5OpenGL_INCLUDE_DIRS}
            ${Qt5Xml_INCLUDE_DIRS}
        )
else()
    find_package( Qt4 4.8.0 COMPONENTS QtCore QtGui QtOpenGL QtXml REQUIRED )
    include( ${QT_USE_FILE} )
    add_definitions( ${QT_DEFINITIONS} )
endif()

# pybind11
find_package(pybind11 REQUIRED)

# Eigen
find_package( Eigen3 REQUIRED )
include_directories( ${EIGEN3_INCLUDE_DIR} )

# Carna
find_package( Carna 3.0.0 REQUIRED )
include_directories( ${CARNA_INCLUDE_DIR} )
set(CARNA_VERSION ${FOUND_VERSION})

# CarnaQt
find_package( CarnaQt 1.0.2 REQUIRED )
include_directories( ${CARNAQT_INCLUDE_DIR} )

############################################

configure_file( ${CMAKE_CURRENT_SOURCE_DIR}/misc/__init__.py.in
                ${CMAKE_CURRENT_BINARY_DIR}/__init__.py @ONLY)

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

if(Qt5_FOUND)
    QT5_WRAP_CPP( PRIVATE_HEADERS_MOC ${PRIVATE_QOBJECT_HEADERS} )
    QT5_WRAP_UI( FORMS_HEADERS ${FORMS} )
    QT5_ADD_RESOURCES( RESOURCES_RCC ${RESOURCES} )
else(Qt5_FOUND)
    QT4_WRAP_CPP( PRIVATE_HEADERS_MOC ${PRIVATE_QOBJECT_HEADERS} )
    QT4_WRAP_UI( FORMS_HEADERS ${FORMS} )
    QT4_ADD_RESOURCES( RESOURCES_RCC ${RESOURCES} )
endif(Qt5_FOUND)

############################################
# Exclude all source files from build,
# since we are using unity build.
############################################

#set_source_files_properties(    ${SRC}
#                                ${PRIVATE_HEADERS_MOC}
#                                ${FORMS_HEADERS}
#                                ${RESOURCES_RCC}
#                                ${DOC_SRC}
#    PROPERTIES
#    HEADER_FILE_ONLY TRUE )

############################################
include_directories( ${CMAKE_CURRENT_BINARY_DIR} )
############################################

set(EXTRA_SOURCES_egl src/egl/Context.cpp)
foreach( MODULE ${MODULES} )
    pybind11_add_module(${MODULE} src/py/${MODULE}.cpp ${EXTRA_SOURCES_${MODULE}})
#    add_library(
#        ${MODULE} SHARED
#        src/py/${MODULE}.cpp
#        ${PRIVATE_HEADERS}
#        ${PRIVATE_HEADERS_MOC}
#        ${FORMS_HEADERS}
#        ${RESOURCES_RCC}
#        ${DOC_SRC}
#    )

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
        ${CARNAQT_LIBRARIES}
        ${QT_LIBRARIES}
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

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/__init__.py
        DESTINATION ${INSTALL_LIBRARY_DIR})

# install headers
#install(DIRECTORY ${CMAKE_PROJECT_DIR}include/CarnaPy
#        DESTINATION ${INSTALL_HEADERS_DIR})

# install CMake Find<Module> file
#install(    FILES ${CMAKE_CURRENT_BINARY_DIR}/misc/Find${PROJECT_NAME}.cmake
#            DESTINATION ${INSTALL_CMAKE_DIR})

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

