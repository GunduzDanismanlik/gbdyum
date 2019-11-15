%global         gbddir  /usr/gbd
%global         sname geos
%global		_geosversion	38
%global		geosinstdir %{gbddir}/%{sname}%{_geosversion}

# Specify the subdirectory for the libraries:
%ifarch i686 i386
%global		_geoslibdir lib
%else
%global		_geoslibdir lib64
%endif

%ifarch ppc64 ppc64le
# Define the AT version and path.
%global atstring	at10.0
%global atpath		/opt/%{atstring}
%endif

Name:		%{sname}%{_geosversion}
Version:	3.8.0
Release:	1%{?dist}
Summary:	GEOS is a C++ port of the Java Topology Suite

License:	LGPLv2
URL:		http://trac.osgeo.org/geos/
Source0:	http://download.osgeo.org/%{sname}/%{sname}-%{version}.tar.bz2
Patch0:		%{name}-gcc43.patch

BuildRequires:	doxygen libtool
BuildRequires:	gcc-c++
Obsoletes:	geos36 >= 3.6.0
Provides:	geos36 >= 3.6.0
Provides:	geos%{_geosversion}-python >= %{version}

%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

%ifarch ppc64 ppc64le
BuildRequires:	advance-toolchain-%{atstring}-devel
%endif

%description
GEOS (Geometry Engine - Open Source) is a C++ port of the Java Topology
Suite (JTS). As such, it aims to contain the complete functionality of
JTS in C++. This includes all the OpenGIS "Simple Features for SQL" spatial
predicate functions and spatial operators, as well as specific JTS topology
functions such as IsValid()

%package devel
Summary:	Development files for GEOS
Requires:	%{name} = %{version}-%{release}
Obsoletes:	geos36-devel >= 3.6.0
Provides:	geos36-devel >= 3.6.0

%description devel
GEOS (Geometry Engine - Open Source) is a C++ port of the Java Topology
Suite (JTS). As such, it aims to contain the complete functionality of
JTS in C++. This includes all the OpenGIS "Simple Features for SQL" spatial
predicate functions and spatial operators, as well as specific JTS topology
functions such as IsValid()

This package contains the development files to build applications that
use GEOS

%prep
%setup -q -n %{sname}-%{version}
%patch0 -p0

%build
%ifarch ppc64 ppc64le
	CFLAGS="${CFLAGS} $(echo %{__global_cflags} | sed 's/-O2/-O3/g') -m64 -mcpu=power8 -mtune=power8 -I%{atpath}/include"
	CXXFLAGS="${CXXFLAGS} $(echo %{__global_cflags} | sed 's/-O2/-O3/g') -m64 -mcpu=power8 -mtune=power8 -I%{atpath}/include"
	LDFLAGS="-L%{atpath}/%{_lib}"
	CC=%{atpath}/bin/gcc; export CC
%endif

# disable internal libtool to avoid hardcoded r-path
%if 0%{?rhel} && 0%{?rhel} >= 7
for makefile in $(find . -type f -name 'Makefile.in'); do
sed -i 's|@LIBTOOL@|%{_bindir}/libtool|g' $makefile
done
%endif

./configure --prefix=%{geosinstdir} --libdir=%{geosinstdir}/%{_geoslibdir} --disable-static --disable-dependency-tracking --disable-python
# Touch the file, since we are not using ruby bindings anymore:
# Per http://lists.osgeo.org/pipermail/geos-devel/2009-May/004149.html
touch swig/python/geos_wrap.cxx

%{__make} %{?_smp_mflags}

# Make doxygen documentation files
cd doc
%{__make} doxygen-html

%install
%{__rm} -rf %{buildroot}
%{__make} DESTDIR=%{buildroot} install

# Create linker config file:
%{__mkdir} -p %{buildroot}%{_sysconfdir}/ld.so.conf.d/
echo "%{geosinstdir}/%{_geoslibdir}/" > %{buildroot}%{_sysconfdir}/ld.so.conf.d/%{name}-pgdg-libs.conf

%clean
%{__rm} -rf %{buildroot}

%post
%ifarch ppc64 ppc64le
	%{atpath}/sbin/ldconfig
%else
	/sbin/ldconfig
%endif

%postun
%ifarch ppc64 ppc64le
	%{atpath}/sbin/ldconfig
%else
	/sbin/ldconfig
%endif

%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING NEWS README.md
%{geosinstdir}/%{_geoslibdir}/libgeos-%{version}.so
%{geosinstdir}/%{_geoslibdir}/libgeos.so
%{geosinstdir}/%{_geoslibdir}/libgeos_c.so*
%if 0%{?rhel} && 0%{?rhel} >= 7
%exclude %{geosinstdir}/%{_geoslibdir}/*.a
%endif
%exclude %{geosinstdir}/%{_geoslibdir}/*.la
%config(noreplace) %attr (644,root,root) %{_sysconfdir}/ld.so.conf.d/%{name}-pgdg-libs.conf

%files devel
%defattr(-,root,root,-)
%doc doc/doxygen_docs
%{geosinstdir}/bin/geos-config
%{geosinstdir}/include/*

%changelog
%changelog
* Fri Nov 15 2019 Devrim Gündüz <devrim@gunduz.org> - 3.8.0
- GBDSQL için 3.8.0 paketi
