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

    exports_sources = ["CMakeLists.txt", "patches/**"]
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

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITH_TESTS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
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
