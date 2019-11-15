%global debug_package		%{nil}
%global sname libspatialite
%global	gbddir  /usr/gbd
%global libspatialiteinstdir	%{gbddir}/%{name}

%global	libspatialiteversion	43

%global geosmajorversion	38
%global projmajorversion	62

%global geosinstdir		%{gbddir}/geos%{geosmajorversion}
%global projinstdir		%{gbddir}/proj%{projmajorversion}

# Warning to ELGIS:
# 1 of the 41 tests is known to fail on EL6 (32 bit and 64 bit Intel)
# Tests pass though on PPC and PPC64
# The author is informed about that.
# The problem seems to stem from Geos.

#EPSG data in libspatialite should be in sync with our current GDAL version

# A new feature available in PostGIS 2.0
#%%global _lwgeom "--enable-lwgeom=yes"
# Disabled due to a circular dependency issue with PostGIS
# https://bugzilla.redhat.com/show_bug.cgi?id=979179
%global _lwgeom "--disable-lwgeom"

# Geocallbacks work with SQLite 3.7.3 and up, available in Fedora and EL 7
%if (0%{?fedora} || 0%{?rhel} > 6)
  %global _geocallback "--enable-geocallbacks"
%endif

%if 0%{?rhel} == 6
# Checks are known to fail if libspatialite is built without geosadvanced
#TODO: Fails to build, reported by mail. If geosadvanced is disabled, linker flags miss geos_c
#TODO: Check if that's still true anywhere
  %global _geosadvanced "--disable-geosadvanced"
  %global _no_checks 1
%endif

# check_bufovflw test fails on gcc 4.9
# https://groups.google.com/forum/#!msg/spatialite-users/zkGP-gPByXk/EAZ-schWn1MJ
%if (0%{?fedora} >= 21 || 0%{?rhel} > 7)
  %global _no_checks 1
%endif

Name:		%{sname}%{libspatialiteversion}
Version:	4.3.0a
Release:	4%{?dist}
Summary:	Enables SQLite to support spatial data
License:	MPLv1.1 or GPLv2+ or LGPLv2+
URL:		https://www.gaia-gis.it/fossil/libspatialite
Source0:	http://www.gaia-gis.it/gaia-sins/%{sname}-%{version}.tar.gz
Patch0:		%{name}-proj_api.h-configure.patch
Patch1:		%{name}-proj_api.h-c.patch
BuildRequires:	gcc autoconf
BuildRequires:	freexl-devel
BuildRequires:	gbd-geos%{geosmajorversion}-devel >= 3.7.2
BuildRequires:	gbd-proj%{projmajorversion}-devel >= 6.2.1
BuildRequires:	sqlite-devel
BuildRequires:	zlib-devel

%if (0%{?fedora} || 0%{?rhel} > 6)
BuildRequires: libxml2-devel
%endif


%description
SpatiaLite is a a library extending the basic SQLite core in order to
get a full fledged Spatial DBMS, really simple and lightweight, but
mostly OGC-SFS compliant.

%package devel
Summary:	Development libraries and headers for SpatiaLite
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	pkgconfig

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%prep
%setup -q -n %{sname}-%{version}
%patch0 -p0
%patch1 -p0
autoconf

%build
CFLAGS="$CFLAGS -I%{projinstdir}/include -I%{geosinstdir}/include"; export CFLAGS
SHLIB_LINK="$SHLIB_LINK -Wl,-rpath,%{geosinstdir}/lib64,%{projinstdir}/lib" ; export SHLIB_LINK
LDFLAGS="$LDFLAGS -L%{geosinstdir}/lib64 -L%{projinstdir}/lib"; export LDFLAGS
./configure \
	--prefix=%{libspatialiteinstdir} \
	--libdir=%{libspatialiteinstdir}/lib \
	--disable-static \
	--with-geosconfig=%{geosinstdir}/bin/geos-config \
	--with-lwgeom \
	--enable-libxml2 \
	%{?_geocallback}   \
	%{?_geosadvanced}

%{__make} %{?_smp_mflags}

%install
%{__rm} -rf %{buildroot}

%{__make} install DESTDIR=%{buildroot}

# Delete undesired libtool archives
find %{buildroot} -type f -name "*.la" -delete

%check
%if 0%{?_no_checks}
# Run check but don't fail build
#%%{__make} check V=1 ||:
#%%else
#%%{__make} check V=1
%endif

%post -p %{_sbindir}/ldconfig
%postun -p %{_sbindir}/ldconfig

%clean
%{__rm} -rf %{buildroot}

%files
%doc COPYING AUTHORS
%{libspatialiteinstdir}/lib/%{sname}.so.7*
%{libspatialiteinstdir}/lib/mod_spatialite.so.7*
# The symlink must be present to allow loading the extension
# https://groups.google.com/forum/#!topic/spatialite-users/zkGP-gPByXk
%{libspatialiteinstdir}/lib/mod_spatialite.so

%files devel
%doc examples/*.c
%{libspatialiteinstdir}/include/spatialite.h
%{libspatialiteinstdir}/include/spatialite
%{libspatialiteinstdir}/lib/%{sname}.so
%{libspatialiteinstdir}/lib/pkgconfig/spatialite.pc


%changelog
* Fri Nov 15 2019 Devrim Gunduz <devrim@gunduz.org> - 4.3.0a-4
- Initial packaging for GBDSQL for RHEL 7.
