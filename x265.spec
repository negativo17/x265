%global api_version 216

%ifarch %{ix86}
%global _pkg_extra_ldflags "-Wl,-z,notext"
%endif

Summary:    H.265/HEVC encoder
Name:       x265
Version:    4.2
Release:    1%{?dist}
Epoch:      1
URL:        http://x265.org/
# source/Lib/TLibCommon - BSD
# source/Lib/TLibEncoder - BSD
# everything else - GPLv2+
License:    GPLv2+ and BSD

Source0:    https://bitbucket.org/multicoreware/%{name}_git/downloads/%{name}_%{version}.tar.gz
Patch0:     %{name}-high-bit-depth-soname.patch
Patch1:     %{name}-vmaf.patch
Patch2:     %{name}-fix-aarch64-build.patch
Patch3:     %{name}-gcc15.patch
# https://github.com/HandBrake/HandBrake/tree/2f464fcf93d411ebdd969b39d67739ed658c5e58
# Except:
# contrib/x265/A06-Update-version-strings.patch
# contrib/x265/A08-Fix-inconsistent-bitrate-in-second-pass.patch
Patch4:     %{name}-HandBrake.patch

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  nasm >= 2.13
BuildRequires:  numactl-devel
%ifarch x86_64
BuildRequires:  libvmaf-devel
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
  -DCMAKE_SKIP_RPATH=ON \
  -DENABLE_ALPHA=ON \
  -DENABLE_ASSEMBLY=ON \
  -DENABLE_HDR10_PLUS=ON \
  -DENABLE_MULTIVIEW=ON \
  -DENABLE_PIC=ON \
  -DENABLE_SCC_EXT=ON \
  -DENABLE_SHARED=ON \
  -DGIT_ARCHETYPE="1" \
%ifarch x86_64
  -DENABLE_LIBVMAF=ON \
  -DVMAF_INCLUDE_DIR=%{_includedir}/libvmaf \
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
    -DENABLE_TESTS=ON
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
* Fri May 22 2026 Simone Caronni <negativo17@gmail.com> - 1:4.2-1
- Update to 4.2.
- Update HandBrake patches.
- Trim changelog.

* Wed Feb 11 2026 Simone Caronni <negativo17@gmail.com> - 1:4.1-6
- Fix build on Fedora 44+.

* Mon Nov 03 2025 Simone Caronni <negativo17@gmail.com> - 1:4.1-5
- Fix build on i686.
- Add check section.

* Tue Sep 09 2025 Simone Caronni <negativo17@gmail.com> - 1:4.1-4
- Update HandBrake patches to 1.10.2.

* Sat Mar 15 2025 Simone Caronni <negativo17@gmail.com> - 1:4.1-3
- Fix build on Fedora 42.

* Tue Dec 03 2024 Simone Caronni <negativo17@gmail.com> - 1:4.1-2
- Update patches, drop SVT-HEVC support.

* Tue Dec 03 2024 Simone Caronni <negativo17@gmail.com> - 1:4.1-1
- Update to 4.1.

* Mon Sep 30 2024 Simone Caronni <negativo17@gmail.com> - 1:4.0-1
- Update to 4.0.
- Trim changelog.
- Drop snapshot build support.

* Fri Apr 12 2024 Simone Caronni <negativo17@gmail.com> - 1:3.6-10
- Update to 3.6 final.

* Wed Jan 10 2024 Simone Caronni <negativo17@gmail.com> - 1:3.6-9.20231213gitce8642f22123
- Update to latest snapshot.
