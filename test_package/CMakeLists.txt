#
# Copyright(c) 2021 ADLINK Technology Limited and others
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v. 2.0 which is available at
# http://www.eclipse.org/legal/epl-2.0, or the Eclipse Distribution License
# v. 1.0 which is available at
# http://www.eclipse.org/org/documents/edl-v10.php.
#
# SPDX-License-Identifier: EPL-2.0 OR BSD-3-Clause
#
project(helloword LANGUAGES C)
cmake_minimum_required(VERSION 3.5)

if(EXISTS "${CMAKE_BINARY_DIR}/conan_paths.cmake")
  include(${CMAKE_BINARY_DIR}/conan_paths.cmake)
endif()

find_package(CycloneDDS MODULE REQUIRED COMPONENTS ddsc)

#find_package(CycloneDDS CONFIG REQUIRED)


# This is a convenience function, provided by the CycloneDDS package,
# that will supply a library target related the the given idl file.
# In short, it takes the idl file, generates the source files with
# the proper data types and compiles them into a library.
if(WITH_IDLC)
  message(STATUS "Generating files from idl")

  if(CycloneDDS_VERSION VERSION_LESS "0.10.2")
    set(_idl_file HelloWorldDataOld.idl_in)
  else()
    set(_idl_file HelloWorldData.idl_in)
  endif()
  configure_file(${_idl_file} HelloWorldData.idl)
  idlc_generate(TARGET HelloWorldData_lib FILES "${CMAKE_CURRENT_BINARY_DIR}/HelloWorldData.idl")
else()
  message(STATUS "idlc not available using precompiled files")
  add_library(HelloWorldData_lib gen/HelloWorldData.c gen/HelloWorldData.h)
  target_link_libraries(HelloWorldData_lib PRIVATE CycloneDDS::ddsc)
  target_include_directories(HelloWorldData_lib
    PUBLIC "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/gen>")
endif()

# Both executables have only one related source file.
add_executable(HelloworldPublisher publisher.c)
add_executable(HelloworldSubscriber subscriber.c)

# Both executables need to be linked to the idl data type library and
# the ddsc API library.
target_link_libraries(HelloworldPublisher HelloWorldData_lib CycloneDDS::ddsc)
target_link_libraries(HelloworldSubscriber HelloWorldData_lib CycloneDDS::ddsc)
