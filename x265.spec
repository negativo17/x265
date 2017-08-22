Summary:    H.265/HEVC encoder
Name:       x265
Version:    2.5
Release:    1%{?dist}
Epoch:      1
URL:        http://x265.org/
# source/Lib/TLibCommon - BSD
# source/Lib/TLibEncoder - BSD
# everything else - GPLv2+
License:    GPLv2+ and BSD

Source0:    https://bitbucket.org/multicoreware/%{name}/downloads/%{name}_%{version}.tar.gz

# link test binaries with shared library
Patch1:     x265-test-shared.patch
# fix building as PIC
Patch2:     x265-pic.patch
Patch3:     x265-high-bit-depth-soname.patch
Patch4:     x265-detect_cpu_armhfp.patch

BuildRequires:  cmake
BuildRequires:  yasm

%ifnarch armv7hl armv7hnl s390 s390x
BuildRequires:  numactl-devel
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

%build
# High depth libraries (from source/h265.h):
#   If the requested bitDepth is not supported by the linked libx265,
#   it will attempt to dynamically bind x265_api_get() from a shared
#   library with an appropriate name:
#     8bit:  libx265_main.so
#     10bit: libx265_main10.so

build() {
%cmake -G "Unix Makefiles" \
    -DCMAKE_POSITION_INDEPENDENT_CODE:BOOL=ON \
    -DCMAKE_SKIP_RPATH:BOOL=YES \
    -DENABLE_PIC:BOOL=ON \
    -DENABLE_TESTS:BOOL=ON \
    $* \
    ../source
%make_build
}

# 10/12 bit libraries are supported only on 64 bit.
%ifarch x86_64
mkdir 10bit; pushd 10bit
    build -DENABLE_CLI=OFF -DHIGH_BIT_DEPTH=ON
popd

mkdir 12bit; pushd 12bit
    build -DENABLE_CLI=OFF -DHIGH_BIT_DEPTH=ON -DMAIN12=ON
popd
%endif

# 8 bit + CLI
mkdir 8bit; pushd 8bit
    build
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
            LD_LIBRARY_PATH=%{buildroot}%{_libdir} test/TestBench || :
        popd
    fi
done

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%files
%{_bindir}/%{name}

%files libs
%license COPYING
%{_libdir}/lib%{name}.so.*
%ifarch x86_64
%{_libdir}/lib%{name}_main10.so.*
%{_libdir}/lib%{name}_main12.so.*
%endif

%files devel
%doc doc/*
%{_includedir}/%{name}.h
%{_includedir}/%{name}_config.h
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}.pc

%changelog
* Tue Aug 22 2017 Simone Caronni <negativo17@gmail.com> - 1:2.5-1
- Update to 2.5.

* Sat May 06 2017 Simone Caronni <negativo17@gmail.com> - 1:2.4-1
- Update to 2.4.

* Tue Apr 11 2017 Simone Caronni <negativo17@gmail.com> - 1:2.3-2
- Clean up SPEC file, rework build section.
- Make the main library load the versioned variants of the high depth builds.

* Tue Feb 21 2017 Stefan Bluhm <stefan.bluhm@clacee.eu> - 1:2.3-1
- Update to 2.3.
- Fix to ignore NUNA for ARM processors as ARM is not supported by the nunactl package.

* Tue Jan 03 2017 Simone Caronni <negativo17@gmail.com> - 1:2.2-1
- Update to 2.2.

* Sat Oct 08 2016 Simone Caronni <negativo17@gmail.com> - 1:2.1-2
- Rebuild for 2.1 hotfix, same tarball name, different file.

* Sun Oct 02 2016 Simone Caronni <negativo17@gmail.com> - 1:2.1-1
- Update to version 2.1.

* Wed Aug 17 2016 Simone Caronni <negativo17@gmail.com> - 1:1.9-2
- Bump Epoch.

* Fri Feb 12 2016 Simone Caronni <negativo17@gmail.com> - 1.9-1
- Update to version 1.9.

* Sun Feb 07 2016 Simone Caronni <negativo17@gmail.com> - 1.8-4
- Fix 10/12 bit libraries SONAME.

* Thu Feb 04 2016 Simone Caronni <negativo17@gmail.com> - 1.8-3
- Create 8/10/12 bit libraries for x86_64 builds.
- Add NUMA support. SGI UV 200 I'm coming!!...

* Tue Dec 15 2015 Simone Caronni <negativo17@gmail.com> - 1.8-2
- Make it build also on RHEL/CentOS.
- Add license macro.

* Sun Oct 25 2015 Dominik Mierzejewski <rpm@greysector.net> 1.8-2
- fix building as PIC
- update SO version in file list
