[![GCC Conan](https://github.com/sintef-ocean/conan-cyclonedds/workflows/GCC%20Conan/badge.svg)](https://github.com/sintef-ocean/conan-cyclonedds/actions?query=workflow%3A"GCC+Conan")
[![Clang Conan](https://github.com/sintef-ocean/conan-cyclonedds/workflows/Clang%20Conan/badge.svg)](https://github.com/sintef-ocean/conan-cyclonedds/actions?query=workflow%3A"Clang+Conan")
[![MSVC Conan](https://github.com/sintef-ocean/conan-cyclonedds/workflows/MSVC%20Conan/badge.svg)](https://github.com/sintef-ocean/conan-cyclonedds/actions?query=workflow%3A"MSVC+Conan")


[Conan.io](https://conan.io) recipe for [cyclonedds](https://cyclonedds.io/).

The package is usually consumed using the `conan install` command or a *conanfile.txt*.

## How to use this package

1. Add remote to conan's package [remotes](https://docs.conan.io/en/latest/reference/commands/misc/remote.html?highlight=remotes):

   ```bash
   $ conan remote add sintef https://artifactory.smd.sintef.no/artifactory/api/conan/conan-local
   ```

2. Using *conanfile.txt* in your project with *cmake*

   Add a [*conanfile.txt*](http://docs.conan.io/en/latest/reference/conanfile_txt.html) to your project. This file describes dependencies and your configuration of choice, e.g.:

   ```
   [requires]
   cyclonedds/[>=0.8.2]@sintef/stable

   [options]
   None

   [imports]
   licenses, * -> ./licenses @ folder=True

   [generators]
   cmake_paths
   cmake_find_package
   ```

   Insert into your *CMakeLists.txt* something like the following lines:
   ```cmake
   cmake_minimum_required(VERSION 3.13)
   project(TheProject CXX)

   include(${CMAKE_BINARY_DIR}/conan_paths.cmake)
   find_package(CycloneDDS MODULE REQUIRED)
   # find_package(CycloneDDS CONFIG REQUIRED) # also available
   # idlc_generate function to create from idl is available

   add_executable(the_executor code.cpp)
   target_link_libraries(the_executor CycloneDDS::ddsc)
   ```
   Then, do
   ```bash
   $ mkdir build && cd build
   $ conan install .. -s build_type=<build_type>
   ```
   where `<build_type>` is e.g. `Debug` or `Release`.
   You can now continue with the usual dance with cmake commands for configuration and compilation. For details on how to use conan, please consult [Conan.io docs](http://docs.conan.io/en/latest/)

## Package options

Option | Values | Default
---|---|---
shared | [True, False] | True
with_tls | [True, False] | True
with_shm | [True, False] | True
with_deadline_missed | [True, False] | True
with_lifespan | [True, False] | True
with_network_partitions | [True, False] | True
with_security | [True, False] | True
with_source_specific_multicast | [True, False] | True
with_topic_discovery | [True, False] | False
with_type_discovery | [True, False] | False
with_doc | [True, False] | False
with_examples | [True, False] | False
with_tests | [True, False] | False
with_ddsconf | [True, False] | True
with_idlc | [True, False] | True
with_schema | [True, False] | True
with_dns | [True, False] | True
with_freertos | [True, False] | False
with_lwip | [True, False] | False
with_analyzer | [True, False, "clang-tidy"] | False
with_coverage | [True, False] | False
with_sanitizer | ANY | ""
with_werror | [True, False] | True

## Known recipe issues

 - Several invalid combinations are not handled by the recipe and will fail
 - conan-center bison does not seem to provide `bison_target`, bison may need to be
   installed system-wide instead.
 - RPATH is not stripped from the libraries. Should they be?
 - Building the library for `build_type=Debug` with MSVC fails.
