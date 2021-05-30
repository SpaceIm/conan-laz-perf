from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class LazperfConan(ConanFile):
    name = "laz-perf"
    description = "LAZperf is an alternative LAZ implementation."
    license = "LGPL-2.1-only"
    topics = ("conan", "laz-perf", "laz", "las", "lidar")
    homepage = "https://github.com/hobu/laz-perf"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        cpp_cmakelists = os.path.join(self._source_subfolder, "cpp", "CMakeLists.txt")
        lazperf_cmakelists = os.path.join(self._source_subfolder, "cpp", "lazperf", "CMakeLists.txt")
        install_cmake = os.path.join(self._source_subfolder, "cmake", "install.cmake")

        # Allow to wrap laz-perf with add_subdirectory()
        tools.replace_in_file(cpp_cmakelists, "if (NOT CMAKE_PROJECT_NAME STREQUAL \"LAZPERF\")", "if(0)")

        # Do not build examples, benchmarks and tools
        tools.replace_in_file(cpp_cmakelists, "add_subdirectory(examples)", "")
        tools.replace_in_file(cpp_cmakelists, "add_subdirectory(benchmarks)", "")
        tools.replace_in_file(cpp_cmakelists, "add_subdirectory(tools)", "")

        # Build and install either static or shared
        if self.options.shared:
            tools.replace_in_file(lazperf_cmakelists,
                                  "add_library(${LAZPERF_STATIC_LIB} STATIC ${SRCS})\nlazperf_target_compile_settings(${LAZPERF_STATIC_LIB})",
                                  "")
        else:
            tools.replace_in_file(lazperf_cmakelists,
                                  "add_library(${LAZPERF_SHARED_LIB} SHARED ${SRCS})\n    lazperf_target_compile_settings(${LAZPERF_SHARED_LIB})",
                                  "")
            tools.replace_in_file(install_cmake, "${LAZPERF_SHARED_LIB}", "${LAZPERF_STATIC_LIB}")

        # Fix "non-constant-expression cannot be narrowed" with clang on Linux
        tools.replace_in_file(os.path.join(self._source_subfolder, "cpp", "lazperf", "vlr.cpp"),
                              "htole32(1)",
                              "static_cast<uint8_t>(htole32(1))")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITH_TESTS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "lazperf"
        self.cpp_info.filenames["cmake_find_package_multi"] = "lazperf"
        self.cpp_info.names["cmake_find_package"] = "LAZPERF"
        self.cpp_info.names["cmake_find_package_multi"] = "LAZPERF"
        target_lib_name = "lazperf" if self.options.shared else "lazperf_s"
        self.cpp_info.components["lazperf"].names["cmake_find_package"] = target_lib_name
        self.cpp_info.components["lazperf"].names["cmake_find_package_multi"] = target_lib_name
        self.cpp_info.components["lazperf"].libs = [target_lib_name]
