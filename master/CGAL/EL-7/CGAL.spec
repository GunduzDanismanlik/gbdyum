# Min dependencies
%global boost_version 1.39
%global qt_version 4.3
%global cmake_version 2.6.12

# Various variables that defines the release
%global soname 11
%global soversion 11.0.1
%global alphatag %{nil}
%global alphaname %{nil}

Name:		CGAL
Version:	4.13
Release:	1GBD%{alphatag}%{?dist}.1
Summary:	Computational Geometry Algorithms Library

Group:		System Environment/Libraries
License:	LGPLv3+ and GPLv3+ and Boost
URL:		http://www.cgal.org/
Source0:	https://github.com/CGAL/cgal/releases/download/releases/%{name}-%{version}/%{name}-%{version}.tar.xz
Source10:	CGAL-README.Fedora

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# Required devel packages.
BuildRequires:	cmake >= %{cmake_version} gmp-devel boost-devel >= %{boost_version}
%if 0%{?suse_version}
%if 0%{?suse_version} >= 1315
BuildRequires:	libqt4-devel libqt5-qtbase-common-devel
%endif
%else
BuildRequires:	qt3-devel qt-devel >= %{qt_version}
%endif
BuildRequires:	zlib-devel
BuildRequires:	blas-devel lapack-devel mpfr-devel gcc-c++

%description
Libraries for CGAL applications.
CGAL is a collaborative effort of several sites in Europe and
Israel. The goal is to make the most important of the solutions and
methods developed in computational geometry available to users in
industry and academia in a C++ library. The goal is to provide easy
access to useful, reliable geometric algorithms.


%package devel
Group:		Development/Libraries
Summary:	Development files and tools for CGAL applications
Requires:	cmake
Requires:	%{name} = %{version}-%{release}
Requires:	boost-devel%{?_isa} >= %{boost_version}
%if 0%{?suse_version}
%if 0%{?suse_version} >= 1315
Requires:	libqt4-devel libqt5-qtbase-common-devel
%endif
%else
Requires:	qt-devel%{?_isa} >= %{qt_version} qt3-devel%{?_isa}
%endif
Requires:	blas-devel%{?_isa} lapack-devel%{?_isa} zlib-devel%{?_isa} gmp-devel%{?_isa}
Requires:	mpfr-devel%{?_isa}

%description devel
The %{name}-devel package provides the headers files and tools you may need to 
develop applications using CGAL.


%package demos-source
Group:		Documentation
Summary:	Examples and demos of CGAL algorithms
Requires:	%{name}-devel%{?_isa} = %{version}-%{release}

%description demos-source
The %{name}-demos-source package provides the sources of examples and demos of
CGAL algorithms.


%prep
%setup -q -n %{name}-%{version}%{alphaname}

# Fix some file permissions
chmod a-x include/CGAL/export/ImageIO.h
chmod a-x include/CGAL/export/CORE.h
chmod a-x include/CGAL/internal/Static_filters/Equal_3.h
chmod a-x include/CGAL/export/CGAL.h

# Install README.Fedora here, to include it in %%doc
install -p -m 644 %{SOURCE10} ./README.Fedora

%build

%{__mkdir} build
pushd build
%if 0%{?suse_version}
%if 0%{?suse_version} >= 1315
cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr \
%endif
%else
%cmake \
%endif
	-DCGAL_INSTALL_LIB_DIR=%{_lib} -DCGAL_INSTALL_DOC_DIR= ${CHANGE_SOVERSION} ..

make VERBOSE=1 %{?_smp_mflags}
popd


%install
%{__rm} -rf %{buildroot}

pushd build

make install DESTDIR=$RPM_BUILD_ROOT

popd

# Install demos and examples
%{__mkdir} -p %{buildroot}%{_datadir}/CGAL
touch -r demo %{buildroot}%{_datadir}/CGAL/
%{__cp} -a demo %{buildroot}%{_datadir}/CGAL/demo
%{__cp} -a examples %{buildroot}%{_datadir}/CGAL/examples

%clean
%{__rm} -rf %{buildroot}


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc AUTHORS LICENSE LICENSE.FREE_USE LICENSE.LGPL LICENSE.GPL CHANGES README.Fedora
%{_libdir}/libCGAL*.so.%{soname}
%{_libdir}/libCGAL*.so.%{soversion}


%files devel
%defattr(-,root,root,-)
%{_includedir}/CGAL
%{_libdir}/libCGAL*.so
%{_libdir}/CGAL
%dir %{_datadir}/CGAL
%{_bindir}/*
%exclude %{_bindir}/cgal_make_macosx_app
%{_mandir}/man1/cgal_create_cmake_script.1.gz


%files demos-source
%defattr(-,root,root,-)
%dir %{_datadir}/CGAL
%{_datadir}/CGAL/demo
%{_datadir}/CGAL/examples
%exclude %{_datadir}/CGAL/*/*/skip_vcproj_auto_generation

%changelog
* Mon Oct 15 2018 Devrim Gündüz <devrim@gunduz.org> - 4.7-1.1
- GBDSQL için ilk sürüm
