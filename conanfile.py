from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import subprocess
import sys
import textwrap

required_conan_version = ">=1.33.0"


class cycloneddsConan(ConanFile):
    name = "cyclonedds"
    license = "EPL-2.0, EDL-1.0"
    author = "SINTEF Ocean"
    url = "https://github.com/sintef-ocean/conan-cyclonedds"
    homepage = "https://cyclonedds.io/"
    description = "Eclipse Cyclone DDS is a very performant and " \
        "robust open-source DDS (Data Distribution Service) implementation " \
        "of the OMG (Object Management Group)."
    topics = ("c-plus-plus", "omg", "dds", "ros2", "middleware", "rtps")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "with_tls": [True, False],
        "with_shm": [True, False],
        "with_deadline_missed": [True, False],
        "with_lifespan": [True, False],
        "with_network_partitions": [True, False],
        "with_security": [True, False],
        "with_source_specific_multicast": [True, False],
        "with_topic_discovery": [True, False],
        "with_type_discovery": [True, False],
        "with_doc": [True, False],
        "with_examples": [True, False],
        "with_tests": [True, False],
        "with_ddsconf": [True, False],
        "with_idlc": [True, False],
        "with_schema": [True, False],
        "with_dns": [True, False],
        "with_freertos": [True, False],
        "with_lwip": [True, False],
        "with_analyzer": [True, False, "clang-tidy"],
        "with_coverage": [True, False],
        "with_sanitizer": "ANY",
        "with_werror": [True, False]

    }
    default_options = {
        "shared": True,
        "with_tls": True,
        "with_shm": True,
        "with_deadline_missed": True,
        "with_lifespan": True,
        "with_network_partitions": True,
        "with_security": True,
        "with_source_specific_multicast": True,
        "with_topic_discovery": False,
        "with_type_discovery": False,
        "with_doc": False,
        "with_examples": False,
        "with_tests": False,
        "with_ddsconf": True,
        "with_idlc": True,
        "with_schema": True,
        "with_dns": True,
        "with_freertos": False,
        "with_lwip": False,
        "with_analyzer": False,
        "with_coverage": False,
        "with_sanitizer": "",
        "with_werror": True

    }
    generators = ("cmake", "cmake_paths", "cmake_find_package")
    exports_sources = ['patches/*']
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        _deps = self.conan_data["dependencies"][self.version]
        if self.options.with_shm:
            self.requires("iceoryx/{}".format(_deps["iceoryx"]))
        if self.options.with_tls:
            self.requires("openssl/{}".format(_deps["openssl"]))

    def build_requirements(self):
        _deps = self.conan_data["dependencies"][self.version]
        if tools.os_info.is_macos:
            self.output.warn("Use system-installed bison")
        else:
            self.build_requires("bison/{}".format(_deps["bison"]))
        if self.options.with_doc:
            self.build_requires("doxygen/{}".format(_deps["doxygen"]))
        if self.options.with_tests:
            self.build_requires("cunit/{}".format(_deps["cunit"]))

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.with_tests:
            self.options["cunit"].shared = True
        if tools.cross_building(self):
            del self.options.with_ddsconf
            del self.options.with_idlc
            del self.options.with_schema

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake is None:
            self._cmake = CMake(self)

            _defs = dict()

            _defs["CMAKE_BUILD_TYPE"] = self.settings.build_type
            _defs["ENABLE_SSL"] = self.options.with_tls
            _defs["ENABLE_SHM"] = self.options.with_shm
            _defs["CYCLONE_BUILD_WITH_ICEORYX"] = self.options.with_shm
            _defs["ENABLE_DEADLINE_MISSED"] = self.options.with_deadline_missed
            _defs["ENABLE_LIFESPAN"] = self.options.with_lifespan
            _defs["ENABLE_NETWORK_PARTITIONS"] = \
                self.options.with_network_partitions
            _defs["ENABLE_SECURITY"] = self.options.with_security
            _defs["ENABLE_SOURCE_SPECIFIC_MULTICAST"] = \
                self.options.with_source_specific_multicast
            _defs["ENABLE_TOPIC_DISCOVERY"] = self.options.with_topic_discovery
            _defs["ENABLE_TYPE_DISCOVERY"] = self.options.with_type_discovery
            _defs["BUILD_DOCS"] = self.options.with_doc
            _defs["BUILD_EXAMPLES"] = self.options.with_examples
            _defs["BUILD_TESTING"] = self.options.with_tests

            if not tools.cross_building(self):
                _defs["BUILD_DDSCONF"] = self.options.with_ddsconf
                _defs["BUILD_IDLC"] = self.options.with_idlc
                _defs["BUILD_SCHEMA"] = self.options.with_schema
            else:
                _defs["BUILD_DDSCONF"] = False
                _defs["BUILD_IDLC"] = False
                _defs["BUILD_SCHEMA"] = False
            _defs["WITH_DNS"] = self.options.with_dns
            _defs["WITH_FREERTOS"] = self.options.with_freertos
            _defs["WITH_LWIP"] = self.options.with_lwip
            if self.options.with_analyzer == 'clang-tidy':
                _defs["ANALYZER"] = self.options.with_analyzer
            elif self.options.with_analyzer is True:
                _defs["ANALYZER"] = 'ON'
            else:
                _defs["ANALYZER"] = 'OFF'
            _defs["ENABLE_COVERAGE"] = self.options.with_coverage
            _defs["SANITIZER"] = self.options.with_sanitizer
            _defs["WERROR"] = self.options.with_werror

            self._cmake.definitions.update(_defs)
            self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def validate(self):
        if (self.options.with_tls or self.options.with_security) and not self.options.shared:
            raise ConanInvalidConfiguration(
                "For 'shared=False', " +
                "options 'with_tls' and 'with_security' must be False")

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

        # TODO: Should ORIGIN be stripped from libraries?

        if self.options.with_tests:
            cmake.test()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy('LICENSE', dst="licenses", src=self._source_subfolder,
                  ignore_case=True, keep_path=False)
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {v["target"]: v["type"]
             for k, v in self._cyclonedds_components.items()})

    @property
    def _cyclonedds_components(self):
        def pthread():
            return ["pthread"] if self.settings.os in ["Linux", "FreeBSD"] else []

        def rt():
            return ["rt"] if self.settings.os in ["Linux", "FreeBSD"] else []

        def dl():
            return ["dl"] if self.settings.os in ["Linux", "FreeBSD"] else []

        def iceoryx():
            return ['iceoryx::iceoryx'] if self.options.with_shm else []

        def tls():
            return ['openssl::openssl'] if self.options.with_tls else []

        def shm():
            return ['SHM_SUPPORT_IS_AVAILABLE'] if self.options.with_shm and \
                self.settings.os in ["Linux", "FreeBSD", "Macos"] else []

        return {
            "ddsc": {
                "target": "CycloneDDS::ddsc",
                "type": "library",
                "lib_names": ['ddsc'],
                "system_libs": pthread() + rt() + dl(),
                "requires": iceoryx() + tls(),
                "defines": shm(),
                "includedirs": ["include"],
            },
            "idl": {
                "target": "CycloneDDS::idl",
                "type": "library",
                "lib_names": ['cycloneddsidl'],
                "system_libs": pthread(),
                "requires": [],
            },
            "dds_security_ac": {
                "target": "CycloneDDS::dds_security_ac",
                "type": "library",
                "lib_names": ['dds_security_ac'],
                "system_libs": pthread() + rt() + dl(),
                "requires": ['ddsc'] + tls(),
            },
            "dds_security_auth": {
                "target": "CycloneDDS::dds_security_auth",
                "type": "library",
                "lib_names": ['dds_security_auth'],
                "system_libs": pthread() + rt() + dl(),
                "requires": ['ddsc'] + tls(),
            },
            "dds_security_crypto": {
                "target": "CycloneDDS::dds_security_crypto",
                "type": "library",
                "lib_names": ['dds_security_crypto'],
                "system_libs": pthread() + rt() + dl(),
                "requires": ['ddsc'] + tls(),
            },
            "idlc": {
                "target": "CycloneDDS::idlc",
                "type": "idlc",
            },
            "ddsconf": {
                "target": "CycloneDDS::ddsconf",
                "type": "ddsconf",
            }
        }

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = textwrap.dedent("""\
        get_filename_component(_MYIMPORT_PREFIX "${CMAKE_CURRENT_LIST_FILE}" DIRECTORY)
        get_filename_component(_MYIMPORT_PREFIX "${_MYIMPORT_PREFIX}" DIRECTORY)
        get_filename_component(_MYIMPORT_PREFIX "${_MYIMPORT_PREFIX}" DIRECTORY)
        if(_MYIMPORT_PREFIX STREQUAL "/")
          set(_MYIMPORT_PREFIX "")
        endif()
        set(CYCLONEDDS_MODULE ON) # To help cxx bindings cmake logic
        """)

        for target, libexe in targets.items():
            if libexe != 'library':
                content += textwrap.dedent("""\
                if(NOT TARGET {target})
                    add_executable({target} IMPORTED GLOBAL)
                    set_property(TARGET {target} PROPERTY IMPORTED_LOCATION ${{_MYIMPORT_PREFIX}}/bin/{libexe})
                endif()
                """.format(target=target, libexe=libexe))
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

    def package_id(self):
        # The following options do not impact package id
        del self.info.options.with_tests
        del self.info.options.with_analyzer
        del self.info.options.with_coverage
        del self.info.options.with_sanitizer
        del self.info.options.with_werror

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "CycloneDDS"
        self.cpp_info.names["cmake_find_package_multi"] = "CycloneDDS"

        opt_outs = []
        if not self.options.with_idlc:
            opt_outs.append('idlc')
        if not self.options.with_ddsconf:
            opt_outs.append('ddsconf')
        if not self.options.with_security:
            opt_outs.append('dds_security_ac')
            opt_outs.append('dds_security_auth')
            opt_outs.append('dds_security_crypto')

        def _register_components(components):
            for cmake_lib_name, values in components.items():
                if cmake_lib_name in opt_outs:
                    continue
                library = values.get("type", "not")
                if library != 'library':
                    continue
                system_libs = values.get("system_libs", [])
                lib_names = values.get("lib_names", [])
                requires = values.get("requires", [])
                defines = values.get("defines", [])
                includedirs = values.get("includedirs", [])

                self.cpp_info.components[cmake_lib_name].names["cmake_find_package"] = cmake_lib_name
                self.cpp_info.components[cmake_lib_name].names["cmake_find_package_multi"] = cmake_lib_name
                self.cpp_info.components[cmake_lib_name].includedirs = includedirs
                self.cpp_info.components[cmake_lib_name].libs = lib_names
                self.cpp_info.components[cmake_lib_name].defines = defines
                self.cpp_info.components[cmake_lib_name].system_libs = system_libs
                self.cpp_info.components[cmake_lib_name].requires = requires
                self.cpp_info.components[cmake_lib_name].builddirs.append(self._module_subfolder)
                if cmake_lib_name == 'ddsc' and self.options.with_idlc:
                    self.cpp_info.components[cmake_lib_name].build_modules["cmake_find_package"] = [self._module_file_rel_path]
                    self.cpp_info.components[cmake_lib_name].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
                    self.cpp_info.components[cmake_lib_name].build_modules["cmake_find_package"].append(
                        "lib/cmake/CycloneDDS/idlc/Generate.cmake")
                    self.cpp_info.components[cmake_lib_name].build_modules["cmake_find_package_multi"].append(
                        "lib/cmake/CycloneDDS/idlc/Generate.cmake")

        _register_components(self._cyclonedds_components)

        self.output.info("Appending environment PATH for binaries of {}"
                         .format(self.name))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

    def system_requirements(self):
        if self.options.with_doc:
            self.output.info("Install python requirements for documentation")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install',
                                   'Sphinx', 'breathe', 'exhale', 'sphinx-rtd-theme'])
