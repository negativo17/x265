%global commit0 82225f9a56f96f7d252724249b5ba056feac858d
%global date 20221229
%global shortcommit0 %(c=%{commit0}; echo ${c:0:12})
#global tag %{version}

%global api_version 206

Summary:    H.265/HEVC encoder
Name:       x265
Version:    3.6
Release:    2%{!?tag:.%{date}git%{shortcommit0}}%{?dist}
Epoch:      1
URL:        http://x265.org/
# source/Lib/TLibCommon - BSD
# source/Lib/TLibEncoder - BSD
# everything else - GPLv2+
License:    GPLv2+ and BSD

%if 0%{?tag:1}
Source0:    https://bitbucket.org/multicoreware/%{name}_git/downloads/%{name}_%{version}.tar.gz
%else
Source0:    https://bitbucket.org/multicoreware/%{name}_git/get/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz
%endif
Patch0:     %{name}-pic.patch
Patch1:     %{name}-high-bit-depth-soname.patch
Patch2:     %{name}-detect_cpu_armhfp.patch
Patch3:     %{name}-svt-hevc.patch

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
%if 0%{?tag:1}
%autosetup -p1 -n %{name}_%{version}
%else
%autosetup -p1 -n multicoreware-%{name}_git-%{shortcommit0}
%endif

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

# 8 bit + dynamicHDR CLI
# TestBench dlopens the appropriate x265 library
mkdir 8bit; pushd 8bit
  build \
    -DENABLE_CLI=ON \
    -DENABLE_TESTS=ON \
popd

%install
pushd 8bit
  %cmake_install
popd

install -m 0755 -p \
  12bit/%{_vpath_builddir}/libx265_main12.so.%{api_version} \
  10bit/%{_vpath_builddir}/libx265_main10.so.%{api_version} \
  %{buildroot}%{_libdir}

find %{buildroot} -name "*.a" -delete

%files
%{_bindir}/%{name}

%files libs
%license COPYING
%{_libdir}/libhdr10plus.so
%{_libdir}/lib%{name}.so.%{api_version}
%{_libdir}/lib%{name}_main10.so.%{api_version}
%{_libdir}/lib%{name}_main12.so.%{api_version}

%files devel
%doc doc/*
%{_includedir}/hdr10plus.h
%{_includedir}/%{name}.h
%{_includedir}/%{name}_config.h
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}.pc

%changelog
* Tue Jan 03 2023 Simone Caronni <negativo17@gmail.com> - 1:3.6-2.20221229git82225f9a56f9
- Update to latest snapshot.
- Enable HDR10+ on all combinations (#2).

* Fri Sep 16 2022 Simone Caronni <negativo17@gmail.com> - 1:3.6-1.20220912git931178347b3f
- Update to latest 3.6 snapshot.
- Drop arm patch.

* Fri Sep 16 2022 Simone Caronni <negativo17@gmail.com> - 1:3.5-2
- Clean up SPEC file, split per branch.

* Wed Mar 24 2021 Simone Caronni <negativo17@gmail.com> - 1:3.5-1
- Update to 3.5.
- Enable SVT-HEVC support on x86_64.
- Explicitly enable assembler support.
- Improve SPEC file.
- Remove tests as they are not really tests but benchmarks.

* Fri Sep 11 2020 Simone Caronni <negativo17@gmail.com> - 1:3.4-2
- Enable HDR10+.
- Trim changelog.

* Tue Jun 16 2020 Simone Caronni <negativo17@gmail.com> - 1:3.4-1
- Update to 3.4.

* Sun Mar 15 2020 Simone Caronni <negativo17@gmail.com> - 1:3.3-1
- Update to 3.3.

* Wed Nov 27 2019 Simone Caronni <negativo17@gmail.com> - 1:3.2.1-1
- Update to 3.2.1.

* Sun Oct 20 2019 Simone Caronni <negativo17@gmail.com> - 1:3.2-1
- Update to 3.2.

* Tue Sep 03 2019 Simone Caronni <negativo17@gmail.com> - 1:3.1.2-1
- Update to 3.1.2.

* Sat Jul 06 2019 Simone Caronni <negativo17@gmail.com> - 1:3.1-1
- Update to 3.1.

* Tue Feb 26 2019 Simone Caronni <negativo17@gmail.com> - 1:3.0-1
- Update to 3.0.
