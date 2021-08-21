cmake_minimum_required(VERSION 3.12)

project(dsNodes)
set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

# Set default maya version
if(NOT DEFINED MAYA_VERSION)
    set(MAYA_VERSION 2020)
endif()

# Set cmake modules paths
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
find_package(Maya REQUIRED)

# Set windows compile options
if(WIN32)
    add_compile_options(/wd4068 /EHsc)
endif()

# Create target


add_library(${PROJECT_NAME} SHARED 
                src/dsNodes.cpp)

# Set maya include and link directories
target_include_directories(${PROJECT_NAME} PUBLIC ${MAYA_INCLUDE_DIR}
                                            dsAttract_deformer/src
                                            dsRaycast/src)
link_directories(${MAYA_LIBRARY_DIR})

# Link and set properties
target_link_libraries(${PROJECT_NAME} ${MAYA_LIBRARIES})
set_target_properties(${PROJECT_NAME} PROPERTIES
    COMPILE_DEFINITIONS "${MAYA_COMPILE_DEFINITIONS}"
    PREFIX ""
    SUFFIX ${MAYA_PLUGIN_EXT})

if(WIN32)
    set_target_properties(${PROJECT_NAME} PROPERTIES LINK_FLAGS "/export:initializePlugin /export:uninitializePlugin")
endif()