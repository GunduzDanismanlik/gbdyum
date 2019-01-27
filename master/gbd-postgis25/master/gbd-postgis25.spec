%undefine _debugsource_packages
%global gbddir /usr/gbd
%global postgismajorversion 2.5
%global postgiscurrmajorversion %(echo %{postgismajorversion}|tr -d '.')
%global postgisprevmajorversion 2.4
%global sname	postgis
%global	geosinstdir %{gbddir}/geos37
%global	projinstdir %{gbddir}/proj49

%{!?utils:%global	utils 1}
%if 0%{?fedora} >= 27 || 0%{?rhel} >= 7 || 0%{?suse_version} >= 1315
%{!?shp2pgsqlgui:%global	shp2pgsqlgui 1}
%else
%{!?shp2pgsqlgui:%global	shp2pgsqlgui 0}
%endif
%if 0%{?fedora} >= 27 || 0%{?rhel} >= 6 || 0%{?suse_version} >= 1315
%{!?raster:%global     raster 1}
%else
%{!?raster:%global     raster 0}
%endif
%if 0%{?fedora} >= 27 || 0%{?rhel} >= 7 || 0%{?suse_version} >= 1315
%ifnarch ppc64 ppc64le
# TODO
%{!?sfcgal:%global     sfcgal 1}
%else
%{!?sfcgal:%global     sfcgal 0}
%endif
%else
%{!?sfcgal:%global    sfcgal 0}
%endif

%ifarch ppc64 ppc64le
# Define the AT version and path.
%global atstring	at10.0
%global atpath		/opt/%{atstring}
%endif
%global _smp_mflags	-j1

Summary:	Geographic Information Systems Extensions to GBDSQL
Name:		gbd-%{sname}%{postgiscurrmajorversion}_%{pgmajorversion}
Version:	%{postgismajorversion}.1
Release:	4GBD%{?dist}
License:	GPLv2+
Group:		Applications/Databases
Source0:	http://download.osgeo.org/%{sname}/source/%{sname}-%{version}.tar.gz
Source2:	http://download.osgeo.org/%{sname}/docs/%{sname}-%{version}.pdf
Source4:	gbd-%{sname}%{postgiscurrmajorversion}-filter-requires-perl-Pg.sh
Patch0:		gbd-%{sname}%{postgiscurrmajorversion}-%{postgismajorversion}.0-gdalfpic.patch

URL:		http://www.postgis.net/
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:	gbdsql%{pgmajorversion}-devel, gbd-geos37-devel >= 3.7.0, pcre-devel
%if 0%{?suse_version}
%if 0%{?suse_version} >= 1315
BuildRequires:	libjson-c-devel libproj-devel
%endif
%else
BuildRequires:	gbd-proj49-devel, flex, json-c-devel
%endif
BuildRequires:	libxml2-devel
%if %{shp2pgsqlgui}
BuildRequires:	gtk2-devel > 2.8.0
%endif
%if %{sfcgal}
BuildRequires:	gbd-sfcgal-devel
Requires:	gbd-sfcgal
%endif
%if %{raster}
  %if 0%{?rhel} && 0%{?rhel} < 6
BuildRequires:	gdal-devel >= 1.9.2-9
  %else
BuildRequires:	gdal-devel >= 1.11.4-3
  %endif
%endif
%ifarch ppc64 ppc64le
BuildRequires:	advance-toolchain-%{atstring}-devel
%endif

Requires:	gbdsql%{pgmajorversion} gbd-geos37 >= 3.7.0
Requires:	gbdsql%{pgmajorversion}-contrib gbd-proj49
%if 0%{?rhel} && 0%{?rhel} < 6
Requires:	hdf5 < 1.8.7
%else
Requires:	hdf5
%endif

Requires:	pcre
%if 0%{?suse_version} >= 1315
Requires:	libjson-c2 libgdal20
%else
Requires: json-c
%if 0%{?rhel} && 0%{?rhel} < 6
Requires:	gdal-libs >= 1.9.2-9
%else
Requires:	gdal-libs >= 1.11.4-3
%endif
%endif
Requires(post):	%{_sbindir}/update-alternatives
%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

Provides:	%{sname} = %{version}-%{release}
Obsoletes:	%{sname}2_%{pgmajorversion} <= %{postgismajorversion}.2-1
Provides:	%{sname}2_%{pgmajorversion} => %{postgismajorversion}.0

%description
PostGIS adds support for geographic objects to the GBDSQL object-relational
database. In effect, PostGIS "spatially enables" the GBDSQL server,
allowing it to be used as a backend spatial database for geographic information
systems (GIS), much like ESRI's SDE or Oracle's Spatial extension. PostGIS
follows the OpenGIS "Simple Features Specification for SQL" and has been
certified as compliant with the "Types and Functions" profile.

%package client
Summary:	Client tools and their libraries of PostGIS
Group:		Applications/Databases
Requires:	%{name}%{?_isa} = %{version}-%{release}
Provides:	%{sname}-client = %{version}-%{release}
%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif
Obsoletes:	%{sname}2_%{pgmajorversion}-client <= %{postgismajorversion}.2-1
Provides:	%{sname}2_%{pgmajorversion}-client => %{postgismajorversion}.0

%description client
The %{name}-client package contains the client tools and their libraries
of PostGIS.

%package devel
Summary:	Development headers and libraries for PostGIS
Group:		Development/Libraries
Requires:	%{name}%{?_isa} = %{version}-%{release}
Provides:	%{sname}-devel = %{version}-%{release}
Obsoletes:	%{sname}2_%{pgmajorversion}-devel <= %{postgismajorversion}.2-1
Provides:	%{sname}2_%{pgmajorversion}-devel => %{postgismajorversion}.0
%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

%description devel
The %{name}-devel package contains the header files and libraries
needed to compile C or C++ applications which will directly interact
with PostGIS.

%package docs
Summary:	Extra documentation for PostGIS
Group:		Applications/Databases
Obsoletes:	%{sname}2_%{pgmajorversion}-docs <= %{postgismajorversion}.2-1
Provides:	%{sname}2_%{pgmajorversion}-docs => %{postgismajorversion}.0
%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

%description docs
The %{name}-docs package includes PDF documentation of PostGIS.

%if %utils
%package utils
Summary:	The utils for PostGIS
Group:		Applications/Databases
Requires:	%{name} = %{version}-%{release}, perl-DBD-Pg
Provides:	%{sname}-utils = %{version}-%{release}
Obsoletes:	%{sname}2_%{pgmajorversion}-utils <= %{postgismajorversion}.2-1
Provides:	%{sname}2_%{pgmajorversion}-utils => %{postgismajorversion}.0
%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

%description utils
The %{name}-utils package provides the utilities for PostGIS.
%endif

%global __perl_requires %{SOURCE4}

%prep
%setup -q -n %{sname}-%{version}
# Copy .pdf file to top directory before installing.
%{__cp} -p %{SOURCE2} .
%patch0 -p0

%build
LDFLAGS="-Wl,-rpath,%{geosinstdir}/lib64 ${LDFLAGS}" ; export LDFLAGS
SHLIB_LINK="$SHLIB_LINK -Wl,-rpath,%{geosinstdir}/lib64" ; export SHLIB_LINK

%ifarch ppc64 ppc64le
	sed -i 's:^GEOS_LDFLAGS=:GEOS_LDFLAGS=-L%{atpath}/%{_lib} :g' configure
	CFLAGS="-O3 -mcpu=power8 -mtune=power8 -I%{atpath}/include" LDFLAGS="-L%{atpath}/%{_lib}"
	sed -i 's:^LDFLAGS = :LDFLAGS = -L%{atpath}/%{_lib} :g' raster/loader/Makefile.in
	CC=%{atpath}/bin/gcc; export CC
%endif

LDFLAGS="$LDFLAGS -L/%{geosinstdir}/lib64 -L%{projinstdir}/lib"; export LDFLAGS

%configure --with-pgconfig=%{pginstdir}/bin/pg_config \
%if !%raster
	--without-raster \
%endif
%if %{sfcgal}
	--with-sfcgal=%{gbddir}/sfcgal/bin/sfcgal-config \
%endif
%if %{shp2pgsqlgui}
	--with-gui \
%endif
	--enable-rpath --libdir=%{pginstdir}/lib \
	--with-geosconfig=/%{geosinstdir}/bin/geos-config \
	--with-projdir=%{projinstdir}

SHLIB_LINK="$SHLIB_LINK" %{__make} LPATH=`%{pginstdir}/bin/pg_config --pkglibdir` shlib="%{name}.so"

%{__make} -C extensions

%if %utils
 SHLIB_LINK="$SHLIB_LINK" %{__make} -C utils
%endif

%install
%{__rm} -rf %{buildroot}
SHLIB_LINK="$SHLIB_LINK" %{__make} install DESTDIR=%{buildroot}

%if %utils
%{__install} -d %{buildroot}%{_datadir}/%{name}
%{__install} -m 644 utils/*.pl %{buildroot}%{_datadir}/%{name}
%endif

# Create symlink of .so file. PostGIS hackers said that this is safe:
%{__ln_s} %{pginstdir}/lib/%{sname}-%{postgismajorversion}.so %{buildroot}%{pginstdir}/lib/%{sname}-%{postgisprevmajorversion}.so
%{__ln_s} %{pginstdir}/lib/%{sname}_topology-%{postgismajorversion}.so %{buildroot}%{pginstdir}/lib/%{sname}_topology-%{postgisprevmajorversion}.so
%if %{raster}
%{__ln_s} %{pginstdir}/lib/rtpostgis-%{postgismajorversion}.so %{buildroot}%{pginstdir}/lib/rtpostgis-%{postgisprevmajorversion}.so
%endif

# Create alternatives entries for common binaries
%post
%{_sbindir}/update-alternatives --install /usr/bin/pgsql2shp postgis-pgsql2shp %{pginstdir}/bin/pgsql2shp %{pgmajorversion}00
%{_sbindir}/update-alternatives --install /usr/bin/shp2pgsql postgis-shp2pgsql %{pginstdir}/bin/shp2pgsql %{pgmajorversion}00

# Drop alternatives entries for common binaries and man files
%postun
if [ "$1" -eq 0 ]
  then
	# Only remove these links if the package is completely removed from the system (vs.just being upgraded)
	%{_sbindir}/update-alternatives --remove postgis-pgsql2shp	%{pginstdir}/bin/pgsql2shp
	%{_sbindir}/update-alternatives --remove postgis-shp2pgsql	%{pginstdir}/bin/shp2pgsql
fi

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root)
%doc COPYING CREDITS NEWS TODO README.%{sname} doc/html loader/README.* doc/%{sname}.xml doc/ZMSgeoms.txt
%if 0%{?rhel} && 0%{?rhel} <= 6
%doc LICENSE.TXT
%else
%license LICENSE.TXT
%endif
%{pginstdir}/doc/extension/README.address_standardizer
%{pginstdir}/share/contrib/%{sname}-%{postgismajorversion}/postgis.sql
%{pginstdir}/share/contrib/%{sname}-%{postgismajorversion}/postgis_comments.sql
%{pginstdir}/share/contrib/%{sname}-%{postgismajorversion}/postgis_for_extension.sql
%{pginstdir}/share/contrib/%{sname}-%{postgismajorversion}/postgis_upgrade*.sql
%{pginstdir}/share/contrib/%{sname}-%{postgismajorversion}/postgis_restore.pl
%{pginstdir}/share/contrib/%{sname}-%{postgismajorversion}/uninstall_postgis.sql
%{pginstdir}/share/contrib/%{sname}-%{postgismajorversion}/legacy*.sql
%{pginstdir}/share/contrib/%{sname}-%{postgismajorversion}/*topology*.sql
%{pginstdir}/share/contrib/%{sname}-%{postgismajorversion}/postgis_proc_set_search_path.sql
%if %{sfcgal}
%{pginstdir}/share/contrib/%{sname}-%{postgismajorversion}/*sfcgal*.sql
%endif
%{pginstdir}/lib/%{sname}-%{postgisprevmajorversion}.so
%attr(755,root,root) %{pginstdir}/lib/%{sname}-%{postgismajorversion}.so
%{pginstdir}/share/extension/%{sname}-*.sql
%if %{sfcgal}
%{pginstdir}/share/extension/%{sname}_sfcgal*.sql
%{pginstdir}/share/extension/%{sname}_sfcgal.control
%endif
%{pginstdir}/share/extension/%{sname}.control
%{pginstdir}/lib/liblwgeom*.so.*
%{pginstdir}/lib/%{sname}_topology-%{postgismajorversion}.so
%{pginstdir}/lib/%{sname}_topology-%{postgisprevmajorversion}.so
%{pginstdir}/lib/address_standardizer.so
%{pginstdir}/lib/liblwgeom.so
%{pginstdir}/share/extension/address_standardizer*.sql
%{pginstdir}/share/extension/address_standardizer*.control
%{pginstdir}/share/contrib/%{sname}-%{postgismajorversion}/sfcgal_comments.sql
%if %{raster}
%{pginstdir}/share/contrib/%{sname}-%{postgismajorversion}/raster_comments.sql
%{pginstdir}/share/contrib/%{sname}-%{postgismajorversion}/*rtpostgis*.sql
%{pginstdir}/share/contrib/%{sname}-%{postgismajorversion}/uninstall_legacy.sql
%{pginstdir}/share/contrib/%{sname}-%{postgismajorversion}/spatial*.sql
%{pginstdir}/lib/rtpostgis-%{postgismajorversion}.so
%{pginstdir}/lib/rtpostgis-%{postgisprevmajorversion}.so
%{pginstdir}/share/extension/%{sname}_topology-*.sql
%{pginstdir}/share/extension/%{sname}_topology.control
%{pginstdir}/share/extension/%{sname}_tiger_geocoder*.sql
%{pginstdir}/share/extension/%{sname}_tiger_geocoder.control
%endif
%if %shp2pgsqlgui
%{pginstdir}/bin/shp2pgsql-gui
%{pginstdir}/share/applications/shp2pgsql-gui.desktop
%{pginstdir}/share/icons/hicolor/*/apps/shp2pgsql-gui.png
%endif
%ifarch ppc64 ppc64le
 %else
 %if %{pgmajorversion} >= 11 && %{pgmajorversion} < 90
  %if 0%{?rhel} && 0%{?rhel} <= 6
  %else
   %{pginstdir}/lib/bitcode/address_standardizer*.bc
   %{pginstdir}/lib/bitcode/address_standardizer/*.bc
   %{pginstdir}/lib/bitcode/postgis-%{postgismajorversion}*.bc
   %{pginstdir}/lib/bitcode/postgis_topology-%{postgismajorversion}/*.bc
   %{pginstdir}/lib/bitcode/postgis_topology-%{postgismajorversion}*.bc
   %{pginstdir}/lib/bitcode/postgis-%{postgismajorversion}/*.bc
   %if %raster
   %{pginstdir}/lib/bitcode/rtpostgis-%{postgismajorversion}*.bc
   %{pginstdir}/lib/bitcode/rtpostgis-%{postgismajorversion}/*.bc
   %endif
  %endif
 %endif
%endif

%files client
%defattr(644,root,root)
%attr(755,root,root) %{pginstdir}/bin/pgsql2shp
%attr(755,root,root) %{pginstdir}/bin/raster2pgsql
%attr(755,root,root) %{pginstdir}/bin/shp2pgsql

%files devel
%defattr(644,root,root)
%{_includedir}/liblwgeom.h
%{_includedir}/liblwgeom_topo.h
%{pginstdir}/lib/liblwgeom*.a
%{pginstdir}/lib/liblwgeom*.la

%if %utils
%files utils
%defattr(-,root,root)
%doc utils/README
%attr(755,root,root) %{_datadir}/%{name}/*.pl
%endif

%files docs
%defattr(-,root,root)
%doc %{sname}-%{version}.pdf

%changelog
* Wed Jan 2 2019 Devrim Gündüz <devrim@gunduzdanismanlik.com> - 2.5.1-4GBD
- GBDSQL için ilk paket
