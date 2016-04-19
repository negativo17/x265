Summary:        H.265/HEVC encoder
Name:           x265
Version:        1.9
Release:        1%{?dist}
URL:            http://x265.org/
# source/Lib/TLibCommon - BSD
# source/Lib/TLibEncoder - BSD
# everything else - GPLv2+
License:        GPLv2+ and BSD

Source0:        http://ftp.videolan.org/pub/videolan/%{name}/%{name}_%{version}.tar.gz
Patch0:         %{name}-high-bit-depth-soname.patch
# link test binaries with shared library
Patch1:         %{name}-test-shared.patch
# fix building as PIC
Patch2:         %{name}-pic.patch
Patch4:         %{name}-detect_cpu_armhfp.patch

BuildRequires:  cmake
BuildRequires:  numactl-devel
BuildRequires:  yasm

%description
The primary objective of %{name} is to become the best H.265/HEVC encoder
available anywhere, offering the highest compression efficiency and the highest
performance on a wide variety of hardware platforms.

This package contains the command line encoder.

%package        libs
Summary:        H.265/HEVC encoder library

%description    libs
The primary objective of %{name} is to become the best H.265/HEVC encoder
available anywhere, offering the highest compression efficiency and the highest
performance on a wide variety of hardware platforms.

%ifarch x86_64
This package contains the shared library built with support for 8/10/12 bit
color depths.
%else
This package contains the shared library.
%endif

%package        devel
Summary:        H.265/HEVC encoder library development files
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}

%description    devel
The primary objective of %{name} is to become the best H.265/HEVC encoder
available anywhere, offering the highest compression efficiency and the highest
performance on a wide variety of hardware platforms.

This package contains the shared library development files.

%prep
%setup -q -n x265_%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch4 -p1

%build
# 10/12 bit libraries are supported only on 64 bit.
%ifarch x86_64

mkdir 10bit; pushd 10bit
    %cmake -G "Unix Makefiles" \
        -DCMAKE_SKIP_RPATH:BOOL=YES \
        -DENABLE_CLI=OFF \
        -DENABLE_PIC:BOOL=ON \
        -DENABLE_TESTS:BOOL=ON \
        -DHIGH_BIT_DEPTH=ON \
        ../source
    make %{?_smp_mflags}
popd

mkdir 12bit; pushd 12bit
    %cmake -G "Unix Makefiles" \
        -DCMAKE_SKIP_RPATH:BOOL=YES \
        -DENABLE_CLI=OFF \
        -DENABLE_PIC:BOOL=ON \
        -DENABLE_TESTS:BOOL=ON \
        -DHIGH_BIT_DEPTH=ON \
        -DMAIN12=ON \
        ../source
    make %{?_smp_mflags}
popd

%endif

# 8 bit + CLI
%cmake -G "Unix Makefiles" \
    -DCMAKE_SKIP_RPATH:BOOL=YES \
    -DENABLE_PIC:BOOL=ON \
    -DENABLE_TESTS:BOOL=ON \
    source
make %{?_smp_mflags}


%install
%ifarch x86_64
for i in 10 12; do
    pushd ${i}bit
        %make_install
    popd
done
%endif

%make_install

find %{buildroot} -name "*.a" -delete

%check
LD_LIBRARY_PATH=%{buildroot}%{_libdir} test/TestBench || :

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%files
%{_bindir}/%{name}

%files libs
%{!?_licensedir:%global license %%doc}
%license COPYING
%{_libdir}/lib%{name}.so.*
%ifarch x86_64
%{_libdir}/lib%{name}_main10.so
%{_libdir}/lib%{name}_main10.so.*
%{_libdir}/lib%{name}_main12.so
%{_libdir}/lib%{name}_main12.so.*
%endif

%files devel
%doc doc/*
%{_includedir}/%{name}.h
%{_includedir}/%{name}_config.h
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}.pc

%changelog
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
