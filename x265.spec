%global __cmake_in_source_build 1

Summary:    H.265/HEVC encoder
Name:       x265
Version:    3.4
Release:    2%{?dist}
Epoch:      1
URL:        http://x265.org/
# source/Lib/TLibCommon - BSD
# source/Lib/TLibEncoder - BSD
# everything else - GPLv2+
License:    GPLv2+ and BSD

Source0:    https://bitbucket.org/multicoreware/%{name}/downloads/%{name}_%{version}.tar.gz

# fix building as PIC
Patch0:     %{name}-pic.patch
Patch1:     %{name}-high-bit-depth-soname.patch
Patch2:     %{name}-detect_cpu_armhfp.patch
Patch3:     %{name}-arm-cflags.patch

BuildRequires:  cmake3
BuildRequires:  gcc-c++
# Should be >= 2.13:
BuildRequires:  nasm
BuildRequires:  numactl-devel

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
#   If the requested bitDepth is not supported by the linked libx265,
#   it will attempt to dynamically bind x265_api_get() from a shared
#   library with an appropriate name:
#     8bit:  libx265_main.so
#     10bit: libx265_main10.so

build() {
%cmake3 -G "Unix Makefiles" \
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
    -DCMAKE_SKIP_RPATH=YES \
    -DENABLE_PIC=ON \
    -DENABLE_SHARED=ON \
    -DENABLE_TESTS=ON \
    $* \
    ../source
%make_build
}

# 10/12 bit libraries are supported only on 64 bit.
%ifarch x86_64 aarch64
mkdir 10bit; pushd 10bit
    build -DENABLE_CLI=OFF -DHIGH_BIT_DEPTH=ON
popd

mkdir 12bit; pushd 12bit
    build -DENABLE_CLI=OFF -DHIGH_BIT_DEPTH=ON -DMAIN12=ON
popd
%endif

# 8 bit + CLI
mkdir 8bit; pushd 8bit
    build -DENABLE_HDR10_PLUS=YES
popd

%install
for i in 8 10 12; do
    if [ -d ${i}bit ]; then
        pushd ${i}bit
            %make_install
            # Remove unversioned library, should not be linked to
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

%ldconfig_scriptlets libs

%files
%{_bindir}/%{name}

%files libs
%license COPYING
%{_libdir}/libhdr10plus.so
%{_libdir}/lib%{name}.so.*
%ifarch x86_64 aarch64
%{_libdir}/lib%{name}_main10.so.*
%{_libdir}/lib%{name}_main12.so.*
%endif

%files devel
%doc doc/*
%{_includedir}/hdr10plus.h
%{_includedir}/%{name}.h
%{_includedir}/%{name}_config.h
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}.pc

%changelog
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
