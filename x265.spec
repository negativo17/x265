%global api_version 209

Summary:    H.265/HEVC encoder
Name:       x265
Version:    3.6
Release:    10%{?dist}
Epoch:      1
URL:        http://x265.org/
# source/Lib/TLibCommon - BSD
# source/Lib/TLibEncoder - BSD
# everything else - GPLv2+
License:    GPLv2+ and BSD

Source0:    https://bitbucket.org/multicoreware/%{name}_git/downloads/%{name}_%{version}.tar.gz
Patch0:     %{name}-detect_cpu_armhfp.patch
Patch1:     %{name}-high-bit-depth-soname.patch
Patch2:     %{name}-svt-hevc.patch
Patch3:     %{name}-fix-aarch64-build.patch
# https://github.com/HandBrake/HandBrake/blob/master/contrib/x265/A03-sei-length-crash-fix.patch
Patch4:     %{name}-sei-length-crash-fix.patch
# https://github.com/HandBrake/HandBrake/blob/master/contrib/x265/A04-ambient-viewing-enviroment-sei.patch
Patch5:     %{name}-ambient-viewing-enviroment-sei.patch

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  nasm >= 2.13
BuildRequires:  numactl-devel
%ifarch x86_64
BuildRequires:  svt-hevc-devel
%endif

%description
The primary objective of x265 is to become the best H.265/HEVC encoder
available anywhere, offering the highest compression efficiency and the highest
performance on a wide variety of hardware platforms.

This package contains the command line encoder.

%package libs
Summary:    H.265/HEVC encoder library

%description libs
The primary objective of x265 is to become the best H.265/HEVC encoder
available anywhere, offering the highest compression efficiency and the
highest performance on a wide variety of hardware platforms.

This package contains the shared library.

%package devel
Summary:    H.265/HEVC encoder library development files
Requires:   %{name}-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description devel
The primary objective of x265 is to become the best H.265/HEVC encoder
available anywhere, offering the highest compression efficiency and the highest
performance on a wide variety of hardware platforms.

This package contains the shared library development files.

%prep
%autosetup -p1 -n %{name}_%{version}

sed -i -e 's|libdir=${exec_prefix}/@LIB_INSTALL_DIR@|libdir=@LIB_INSTALL_DIR@|g' source/x265.pc.in

%build
# High depth libraries (from source/h265.h):
#   If the requested bitDepth is not supported by the linked libx265, it will
#   attempt to dynamically bind from a shared library with an appropriate name:
#     8bit:  libx265_main.so
#     10bit: libx265_main10.so
#     12bit: libx265_main12.so
#
# Trying to link 10/12 bits statically inside the shared library (as per
# https://aur.archlinux.org/cgit/aur.git/tree/PKGBUILD?h=x265-hg#n45) makes the
# library not strippable.

# Setting GIT_ARCHETYPE to 1 is like using git as a build dependency:
build() {
%cmake -G "Unix Makefiles" \
  -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
  -DCMAKE_SKIP_RPATH=YES \
  -DENABLE_ASSEMBLY=ON \
  -DENABLE_HDR10_PLUS=YES \
  -DENABLE_PIC=ON \
  -DENABLE_SHARED=ON \
  -DGIT_ARCHETYPE="1" \
%ifarch x86_64
  -DENABLE_SVT_HEVC=ON \
  -DSVT_HEVC_INCLUDE_DIR=%{_includedir}/svt-hevc \
%endif
  $* \
  ../source
%cmake_build
}

%ifnarch %{ix86}
# 10/12 bit libraries are supported only on 64 bit
mkdir 12bit; pushd 12bit
  build \
    -DENABLE_CLI=OFF \
    -DHIGH_BIT_DEPTH=ON \
    -DMAIN12=ON
popd

mkdir 10bit; pushd 10bit
  build \
    -DENABLE_CLI=OFF \
    -DHIGH_BIT_DEPTH=ON
popd
%endif

# 8 bit + dynamicHDR CLI
# TestBench dlopens the appropriate x265 library
mkdir 8bit; pushd 8bit
  build \
    -DENABLE_CLI=ON \
    -DENABLE_TESTS=ON \
popd

%install
for i in 8 10 12; do
  if [ -d ${i}bit ]; then
    pushd ${i}bit
      %cmake_install
      rm -f %{buildroot}%{_libdir}/libx265_main${i}.so
    popd
  fi
done

find %{buildroot} -name "*.a" -delete

%check
for i in 8 10 12; do
  if [ -d ${i}bit ]; then
    pushd ${i}bit
      test/TestBench || :
    popd
  fi
done

%files
%{_bindir}/%{name}

%files libs
%license COPYING
%{_libdir}/libhdr10plus.so
%{_libdir}/lib%{name}.so.%{api_version}
%ifnarch %{ix86}
%{_libdir}/lib%{name}_main10.so.%{api_version}
%{_libdir}/lib%{name}_main12.so.%{api_version}
%endif

%files devel
%doc doc/*
%{_includedir}/hdr10plus.h
%{_includedir}/%{name}.h
%{_includedir}/%{name}_config.h
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}.pc

%changelog
* Mon Nov 03 2025 Simone Caronni <negativo17@gmail.com> - 1:3.6-10
- Fix build on i686.
- Add check section
- Clean up SPEC file.

* Fri Apr 12 2024 Simone Caronni <negativo17@gmail.com> - 1:3.6-9
- Update to 3.6 final.

* Wed Jan 10 2024 Simone Caronni <negativo17@gmail.com> - 1:3.6-8.20231213gitce8642f22123
- Update to latest snapshot.

* Sat Sep 30 2023 Simone Caronni <negativo17@gmail.com> - 1:3.6-7.20230917git8ee01d45b05c
- Update to latest snapshot.

* Fri Jul 07 2023 Simone Caronni <negativo17@gmail.com> - 1:3.6-6.20230627git8f18e3ad3268
- Update to latest snapshot to silence all NASM warnings.

* Mon Jun 05 2023 Simone Caronni <negativo17@gmail.com> - 1:3.6-5.20230508git34532bda12a3
- Add HandBrake patches.

* Mon May 29 2023 Simone Caronni <negativo17@gmail.com> - 1:3.6-4.20230508git34532bda12a3
- Update to latest snapshot.

* Mon Feb 27 2023 Simone Caronni <negativo17@gmail.com> - 1:3.6-3.20230222git38cf1c379b5a
- Update to latest snapshot.

* Tue Jan 03 2023 Simone Caronni <negativo17@gmail.com> - 1:3.6-2.20221229git82225f9a56f9
- Update to latest snapshot.
- Enable HDR10+ on all combinations (#2).
