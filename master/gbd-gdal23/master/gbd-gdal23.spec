%global pgmajorversion 11
%global sname gdal
%global gbddir /usr/gbd
%global gdalinstdir %{gbddir}/%{sname}
%global geos37instdir /usr/gbd/geos37
%global proj52instdir /usr/gbd/proj52

#TODO: g2clib and grib (said to be modified)
#TODO: Create script to make clean tarball
#TODO: msg needs to have PublicDecompWT.zip from EUMETSAT, which is not free;
#      Building without msg therefore
#TODO: e00compr bundled?
#TODO: There are tests for bindings -- at least for Perl
#TODO: Java has a directory with test data and a build target called test
#      It uses %%{JAVA_RUN}; make test seems to work in the build directory
#TODO: e00compr source is the same in the package and bundled in GDAL
#TODO: Consider doxy patch from Suse, setting EXTRACT_LOCAL_CLASSES  = NO

# Soname should be bumped on API/ABI break
# http://trac.osgeo.org/gdal/ticket/4543

# Conditionals and structures for EL 5 are there
# to make life easier for downstream ELGIS.
# Sadly noarch doesn't work in EL 5, see
# http://fedoraproject.org/wiki/EPEL/GuidelinesAndPolicies

# He also suggest to use --with-static-proj4 to actually link to proj, instead of dlopen()ing it.

# Major digit of the proj so version
%global proj_somaj 13

# Tests can be of a different version
%global testversion 2.3.2

%global bashcompletiondir %(pkg-config --variable=compatdir bash-completion)

%if 0%{?bootstrap}
%global build_refman 0
%global mysql --without-mysql
%global with_poppler 0
%global poppler --without-poppler
%global with_spatialite 0
%global spatialite --without-spatialite
%else
# Enable/disable generating refmans
# texlive currently broken deps and FTBFS in rawhide
%global build_refman 1
# https://bugzilla.redhat.com/show_bug.cgi?id=1490492
%global with_mysql 1
%global mysql --with-mysql
# https://bugzilla.redhat.com/show_bug.cgi?id=1490492
%global with_poppler 1
%global poppler --with-poppler
%global with_spatialite 1
%global spatialite "--with-spatialite"
%endif

# No ppc64 build for spatialite in EL6
# https://bugzilla.redhat.com/show_bug.cgi?id=663938
%if 0%{?rhel} == 6
%ifnarch ppc64
%global with_spatialite 0
%global spatialite --without-spatialite
%endif
%endif

Name:		gbd-%{sname}23
Version:	2.3.2
Release:	8%{?dist}%{?bootstrap:.%{bootstrap}.bootstrap}
Summary:	GIS file format library
License:	MIT
URL:		http://www.gdal.org
# Source0:   http://download.osgeo.org/gdal/%%{version}/gdal-%%{version}.tar.xz
# See PROVENANCE.TXT-fedora and the cleaner script for details!

Source0:	%{sname}-%{version}-fedora.tar.xz
Source1:	%{sname}autotest-%{testversion}.tar.gz

# Cleaner script for the tarball
Source3:	%{sname}-cleaner.sh

Source4:	PROVENANCE.TXT-fedora
Source5:	%{name}-libs.conf

# Fix bash-completion install dir
Patch3:		%{name}-completion.patch

# Fedora uses Alternatives for Java
Patch8:		%{name}-1.9.0-java.patch

Patch9:		%{name}-2.3.0-zlib.patch

# https://github.com/OSGeo/gdal/pull/876
Patch10:	%{name}-2.3.1-perl-build.patch

Patch11:	%{name}-2.3.2-poppler-0.73.0.patch

# GBD patches
Patch12:	%{name}-gdalconfig-path.patch

BuildRequires:	gcc gcc-c++
BuildRequires:	ant
# No armadillo in EL5
BuildRequires:	armadillo-devel
BuildRequires:	bash-completion
BuildRequires:	cfitsio-devel
# No CharLS in EL5
#BuildRequires: CharLS-devel
BuildRequires:	chrpath
BuildRequires:	curl-devel
BuildRequires:	doxygen
BuildRequires:	expat-devel
BuildRequires:	fontconfig-devel
# No freexl in EL5
BuildRequires:	freexl-devel
BuildRequires:	g2clib-static
BuildRequires:	gbd-geos37-devel >= 3.7.1
BuildRequires:	ghostscript
BuildRequires:	hdf-devel
BuildRequires:	hdf-static
BuildRequires:	hdf5-devel
BuildRequires:	java-devel >= 1:1.6.0
BuildRequires:	jasper-devel
BuildRequires:	jpackage-utils
# For 'mvn_artifact' and 'mvn_install'
BuildRequires:	json-c-devel
BuildRequires:	libgeotiff-devel
# No libgta in EL5
BuildRequires:	libgta-devel

BuildRequires:	libjpeg-devel
BuildRequires:	libpng-devel
# No libkml in EL
%if 0%{?fedora}
BuildRequires:	libkml-devel
%endif
%if %{with_spatialite}
BuildRequires:	libspatialite-devel
%endif

BuildRequires:	libtiff-devel
# No libwebp in EL 5 and 6
BuildRequires:	libwebp-devel
BuildRequires:	libtool
BuildRequires:	giflib-devel
BuildRequires:	netcdf-devel
BuildRequires:	libdap-devel
BuildRequires:	librx-devel
%if 0%{?rhel}
BuildRequires:	mariadb-devel
%endif
%if 0%{?fedora}
BuildRequires:	mariadb-connector-c-devel
%endif
BuildRequires:	gbdsql%{pgmajorversion}-devel
BuildRequires:	pcre-devel
BuildRequires:	ogdi-devel
BuildRequires:	perl-devel
BuildRequires:	perl-generators
BuildRequires:	openjpeg2-devel
BuildRequires:	perl(ExtUtils::MakeMaker)
BuildRequires:	%{_bindir}/pkg-config
%if 0%{?with_poppler}
BuildRequires:	poppler-devel
%endif
BuildRequires:	gbd-proj52-devel >= 5.2.0
BuildRequires:	sqlite-devel
BuildRequires:	swig
%if %{build_refman}
BuildRequires:	texlive-latex
BuildRequires:	texlive-collection-fontsrecommended
%if 0%{?fedora}
BuildRequires:	texlive-collection-langcyrillic
BuildRequires:	texlive-collection-langportuguese
BuildRequires:	texlive-newunicodechar
%endif
BuildRequires:	texlive-collection-latex
BuildRequires:	texlive-epstopdf
BuildRequires:	tex(multirow.sty)
BuildRequires:	tex(sectsty.sty)
BuildRequires:	tex(tocloft.sty)
BuildRequires:	tex(xtab.sty)
%endif
BuildRequires:	unixODBC-devel
BuildRequires:	xerces-c-devel
BuildRequires:	xz-devel
BuildRequires:	zlib-devel
BuildRequires:	libtirpc-devel

# Run time dependency for gpsbabel driver
Requires:	gpsbabel

# proj DL-opened in ogrct.cpp, see also fix in %%prep
%if 0%{?__isa_bits} == 64
Requires:	libproj.so.%{proj_somaj}()(64bit)
%else
Requires:	libproj.so.%{proj_somaj}
%endif

Requires:	%{name}-libs%{?_isa} = %{version}-%{release}

# We have multilib triage
%if "%{_lib}" == "lib"
  %global cpuarch 32
%else
  %global cpuarch 64
%endif

#TODO: Description on the lib?
%description
Geospatial Data Abstraction Library (GDAL/OGR) is a cross platform
C++ translator library for raster and vector geospatial data formats.
As a library, it presents a single abstract data model to the calling
application for all supported formats. It also comes with a variety of
useful commandline utilities for data translation and processing.

It provides the primary data access engine for many applications.
GDAL/OGR is the most widely used geospatial data access library.


%package devel
Summary:	Development files for the GDAL file format library

# Old rpm didn't figure out
%if 0%{?rhel} < 6
Requires: pkgconfig
%endif

Requires:	%{name}-libs%{?_isa} = %{version}-%{release}
Obsoletes:	%{name}-static < 1.9.0-1

%description devel
This package contains development files for GDAL.


%package libs
Summary:	GDAL file format library
# https://trac.osgeo.org/gdal/ticket/3978#comment:5
Obsoletes:	%{name}-ruby < 1.11.0-1

%description libs
This package contains the GDAL file format library.

%package doc
Summary:	Documentation for GDAL
BuildArch:	noarch

%description doc
This package contains HTML and PDF documentation for GDAL.

%prep
%setup -q -n %{sname}-%{version}-fedora -a 1

# Delete bundled libraries
rm -rf frmts/zlib
rm -rf frmts/png/libpng
rm -rf frmts/gif/giflib
rm -rf frmts/jpeg/libjpeg \
    frmts/jpeg/libjpeg12
rm -rf frmts/gtiff/libgeotiff \
    frmts/gtiff/libtiff
#rm -r frmts/grib/degrib/g2clib

%patch3 -p1 -b .completion~
%patch8 -p1 -b .java~
%patch9 -p1 -b .zlib~
%patch10 -p1 -b .perl-build~
%if 0%{?fedora} >= 30
%patch11 -p1 -b .poppler-0.73.0
%endif
%patch12 -p0

# Copy in PROVENANCE.TXT-fedora
cp -p %SOURCE4 .

# Sanitize linebreaks and encoding
#TODO: Don't touch data directory!
# /frmts/grib/degrib18/degrib/metaname.cpp
# and geoconcept.c are potentially dangerous to change
set +x
for f in `find . -type f` ; do
  if file $f | grep -q ISO-8859 ; then
    set -x
    iconv -f ISO-8859-1 -t UTF-8 $f > ${f}.tmp && \
      mv -f ${f}.tmp $f
    set +x
  fi
  if file $f | grep -q CRLF ; then
    set -x
    sed -i -e 's|\r||g' $f
    set +x
  fi
done
set -x

for f in apps; do
pushd $f
  chmod 644 *.cpp
popd
done

# Replace hard-coded library- and include paths
sed -i 's|-L\$with_cfitsio -L\$with_cfitsio/lib -lcfitsio|-lcfitsio|g' configure
sed -i 's|-I\$with_cfitsio -I\$with_cfitsio/include|-I\$with_cfitsio/include/cfitsio|g' configure
sed -i 's|-L\$with_netcdf -L\$with_netcdf/lib -lnetcdf|-lnetcdf|g' configure
sed -i 's|-L\$DODS_LIB -ldap++|-ldap++|g' configure
sed -i 's|-L\$with_ogdi -L\$with_ogdi/lib -logdi|-logdi|g' configure
sed -i 's|-L\$with_jpeg -L\$with_jpeg/lib -ljpeg|-ljpeg|g' configure
sed -i 's|-L\$with_libtiff\/lib -ltiff|-ltiff|g' configure
sed -i 's|-lgeotiff -L$with_geotiff $LIBS|-lgeotiff $LIBS|g' configure
sed -i 's|-L\$with_geotiff\/lib -lgeotiff $LIBS|-lgeotiff $LIBS|g' configure

# libproj is dlopened; upstream sources point to .so, which is usually not present
# http://trac.osgeo.org/gdal/ticket/3602
sed -i 's|libproj.so|libproj.so.%{proj_somaj}|g' ogr/ogrct.cpp

# Adjust check for LibDAP version
# http://trac.osgeo.org/gdal/ticket/4545
%if %cpuarch == 64
  sed -i 's|with_dods_root/lib|with_dods_root/lib64|' configure
%endif

# Fix mandir
sed -i "s|^mandir=.*|mandir='\${prefix}/share/man'|" configure

# Add our custom cflags when trying to find geos
# https://bugzilla.redhat.com/show_bug.cgi?id=1284714
sed -i 's|CFLAGS=\"${GEOS_CFLAGS}\"|CFLAGS=\"${CFLAGS} ${GEOS_CFLAGS}\"|g' configure

%build
#TODO: Couldn't I have modified that in the prep section?
%ifarch sparcv9 sparc64 s390 s390x
export CFLAGS="$RPM_OPT_FLAGS -fPIC"
%else
export CFLAGS="$RPM_OPT_FLAGS -fpic"
%endif
export CXXFLAGS="$CFLAGS -I%{_includedir}/libgeotiff -I%{_includedir}/tirpc"
export CPPFLAGS="$CPPFLAGS -I%{_includedir}/libgeotiff -I%{_includedir}/tirpc"

# For future reference:
# epsilon: Stalled review -- https://bugzilla.redhat.com/show_bug.cgi?id=660024
# Building without pgeo driver, because it drags in Java

%if 0%{?fedora} >= 27 || 0%{?rhel} > 7
%global g2clib g2c_v1.6.0
%else
%global g2clib grib2c
%endif

%configure \
	LIBS="-l%{g2clib} -ltirpc" \
	--prefix=%{gdalinstdir}	\
	--bindir=%{gdalinstdir}/bin	\
	--sbindir=%{gdalinstdir}/sbin	\
	--libdir=%{gdalinstdir}/lib	\
	--datadir=%{gdalinstdir}/share	\
	--datarootdir=%{gdalinstdir}/share	\
	--with-autoload=%{_libdir}/%{name}plugins \
	--with-armadillo	\
	--with-curl		\
	--with-cfitsio=%{_prefix}	\
	--with-dods-root=%{_prefix}	\
	--with-expat		\
	--with-freexl		\
	--with-geos=%{geos37instdir}/bin/geos-config	\
	--with-geotiff=external	\
	--with-gif		\
	--with-gta		\
	--with-hdf4		\
	--with-hdf5		\
	--with-jasper		\
	--with-java		\
	--with-jpeg		\
	--with-libjson-c	\
	--without-jpeg12	\
	--with-liblzma		\
	--with-libtiff=external	\
	--with-libz		\
	--without-mdb		\
	%{mysql}		\
	--with-netcdf		\
	--with-odbc		\
	--with-ogdi		\
	--without-msg		\
	--with-openjpeg		\
	--with-pcraster		\
	--with-pg=%{pginstdir}/bin/pg_config	\
	--with-png		\
	%{poppler}		\
	--with-proj=%{proj52instdir}	\
	%{spatialite}		\
	--with-sqlite3		\
	--with-threads		\
%if 0%{?fedora}
	--with-libkml		\
%endif
	--with-webp		\
	--with-xerces		\
	--enable-shared

sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

# {?_smp_mflags} doesn't work; Or it does -- who knows!
# NOTE: running autoconf seems to break build:
# fitsdataset.cpp:37:10: fatal error: fitsio.h: No such file or directory
#  #include <fitsio.h>

POPPLER_OPTS="POPPLER_0_20_OR_LATER=yes POPPLER_0_23_OR_LATER=yes POPPLER_BASE_STREAM_HAS_TWO_ARGS=yes"
%if 0%{?fedora} > 26 || 0%{?rhel} > 7
POPPLER_OPTS="$POPPLER_OPTS POPPLER_0_58_OR_LATER=yes"
%endif

make %{?_smp_mflags} $POPPLER_OPTS

make man
make docs

# Build some utilities, as requested in BZ #1271906
pushd ogr/ogrsf_frmts/s57/
  make all
popd

pushd frmts/iso8211/
  make all
popd

# --------- Documentation ----------

# No useful documentation in swig
%global docdirs apps doc doc/br doc/ru ogr ogr/ogrsf_frmts frmts/gxf frmts/iso8211 frmts/pcidsk frmts/sdts frmts/vrt ogr/ogrsf_frmts/dgn/
for docdir in %{docdirs}; do
  # CreateHTML and PDF documentation, if specified
  pushd $docdir
    if [ ! -f Doxyfile ]; then
      doxygen -g
    else
      doxygen -u
    fi
    sed -i -e 's|^GENERATE_LATEX|GENERATE_LATEX = YES\n#GENERATE_LATEX |' Doxyfile
    sed -i -e 's|^GENERATE_HTML|GENERATE_HTML = YES\n#GENERATE_HTML |' Doxyfile
    sed -i -e 's|^USE_PDFLATEX|USE_PDFLATEX = YES\n#USE_PDFLATEX |' Doxyfile

    if [ $docdir == "doc/ru" ]; then
      sed -i -e 's|^OUTPUT_LANGUAGE|OUTPUT_LANGUAGE = Russian\n#OUTPUT_LANGUAGE |' Doxyfile
    fi
    rm -rf latex html
    doxygen

    %if %{build_refman}
      pushd latex
	sed -i -e '/rfoot\[/d' -e '/lfoot\[/d' doxygen.sty
	sed -i -e '/small/d' -e '/large/d' refman.tex
	sed -i -e 's|pdflatex|pdflatex -interaction nonstopmode |g' Makefile
	make refman.pdf || true
      popd
    %endif
  popd
done


%install
rm -rf %{buildroot}

make	DESTDIR=%{buildroot}	\
	install	\
	install-man

%{__install} -pm 755 ogr/ogrsf_frmts/s57/s57dump %{buildroot}%{gdalinstdir}/bin
%{__install} -pm 755 frmts/iso8211/8211createfromxml %{buildroot}%{gdalinstdir}/bin
%{__install} -pm 755 frmts/iso8211/8211dump %{buildroot}%{gdalinstdir}/bin
%{__install} -pm 755 frmts/iso8211/8211view %{buildroot}%{gdalinstdir}/bin

# Directory for auto-loading plugins
mkdir -p %{buildroot}%{_libdir}/%{name}plugins

# Install formats documentation
for dir in gdal_frmts ogrsf_frmts; do
  mkdir -p $dir
  find frmts -name "*.html" -exec install -p -m 644 '{}' $dir \;
done

#TODO: Header date lost during installation
# Install multilib cpl_config.h bz#430894
%{__install} -p -D -m 644 port/cpl_config.h %{buildroot}%{gdalinstdir}/include/cpl_config-%{cpuarch}.h
# Create universal multilib cpl_config.h bz#341231
# The problem is still there in 1.9.
#TODO: Ticket?

#>>>>>>>>>>>>>
cat > %{buildroot}%{gdalinstdir}/include/cpl_config.h <<EOF
#include <bits/wordsize.h>

#if __WORDSIZE == 32
#include "gdal/cpl_config-32.h"
#else
#if __WORDSIZE == 64
#include "gdal/cpl_config-64.h"
#else
#error "Unknown word size"
#endif
#endif
EOF
#<<<<<<<<<<<<<
touch -r NEWS port/cpl_config.h

# Create and install pkgconfig file
#TODO: Why does that exist? Does Grass really use it? I don't think so.
# http://trac.osgeo.org/gdal/ticket/3470
#>>>>>>>>>>>>>
cat > %{name}.pc <<EOF
prefix=%{_prefix}
exec_prefix=%{_prefix}
libdir=%{_libdir}
includedir=%{_includedir}

Name: GDAL
Description: GIS file format library
Version: %{version}
Libs: -L\${libdir} -lgdal
Cflags: -I\${includedir}/%{name}
EOF
#<<<<<<<<<<<<<
mkdir -p %{buildroot}%{_libdir}/pkgconfig/
install -m 644 %{name}.pc %{buildroot}%{_libdir}/pkgconfig/
touch -r NEWS %{buildroot}%{_libdir}/pkgconfig/%{name}.pc

# Multilib gdal-config
# Rename the original script to gdal-config-$arch (stores arch-specific information)
# and create a script to call one or the other -- depending on detected architecture
# TODO: The extra script will direct you to 64 bit libs on
# 64 bit systems -- whether you like that or not
mv %{buildroot}%{gdalinstdir}/bin/%{sname}-config %{buildroot}%{gdalinstdir}/bin/%{sname}-config-%{cpuarch}
#>>>>>>>>>>>>>
cat > %{buildroot}%{gdalinstdir}/bin/%{sname}-config <<EOF
#!/bin/bash

ARCH=\$(uname -m)
case \$ARCH in
x86_64 | ppc64 | ppc64le | ia64 | s390x | sparc64 | alpha | alphaev6 | aarch64 )
%{gdalinstdir}/bin/%{sname}-config-64 \${*}
;;
*)
%{gdalinstdir}/bin/%{sname}-config-32 \${*}
;;
esac
EOF
#<<<<<<<<<<<<<
touch -r NEWS %{buildroot}%{gdalinstdir}/bin/%{sname}-config
chmod 755 %{buildroot}%{gdalinstdir}/bin/%{sname}-config

# Clean up junk
%{__rm} -f %{buildroot}%{gdalinstdir}/bin/*.dox

#jni-libs and libgdal are also built static (*.a)
#.exists and .packlist stem from Perl
for junk in {*.a,*.la,*.bs,.exists,.packlist} ; do
  find %{buildroot} -name "$junk" -exec rm -rf '{}' \;
done

# Don't duplicate license files
%{__rm} -f %{buildroot}%{_datadir}/%{name}/LICENSE.TXT

# Throw away random API man mages plus artefact seemingly caused by Doxygen 1.8.1 or 1.8.1.1
for f in 'GDAL*' BandProperty ColorAssociation CutlineTransformer DatasetProperty EnhanceCBInfo ListFieldDesc NamedColor OGRSplitListFieldLayer VRTBuilder; do
  rm -rf %{buildroot}%{gdalinstdir}/share/man/man1/$f.1*
done

#TODO: What's that?
%{__rm} -f %{buildroot}%{gdalinstdir}/share/man/man1/*_%{name}-%{version}-fedora_apps_*
%{__rm} -f %{buildroot}%{gdalinstdir}/share/man/man1/_home_rouault_dist_wrk_gdal_apps_.1*

# GBD: Move includes under gdalinst directory:
%{__mkdir} -p %{buildroot}%{gdalinstdir}/include
%{__mkdir} -p %{buildroot}%{gdalinstdir}/share/man
%{__mv} %{buildroot}%{_includedir}/* %{buildroot}%{gdalinstdir}/include

# Install linker config file:
%{__mkdir} -p %{buildroot}%{_sysconfdir}/ld.so.conf.d/
%{__install} %{SOURCE5} %{buildroot}%{_sysconfdir}/ld.so.conf.d/

%check

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%files
%{bashcompletiondir}/*
%{gdalinstdir}/bin/gdallocationinfo
%{gdalinstdir}/bin/gdal_contour
%{gdalinstdir}/bin/gdal_rasterize
%{gdalinstdir}/bin/gdal_translate
%{gdalinstdir}/bin/gdaladdo
%{gdalinstdir}/bin/gdalinfo
%{gdalinstdir}/bin/gdaldem
%{gdalinstdir}/bin/gdalbuildvrt
%{gdalinstdir}/bin/gdaltindex
%{gdalinstdir}/bin/gdalwarp
%{gdalinstdir}/bin/gdal_grid
%{gdalinstdir}/bin/gdalenhance
%{gdalinstdir}/bin/gdalmanage
%{gdalinstdir}/bin/gdalserver
%{gdalinstdir}/bin/gdalsrsinfo
%{gdalinstdir}/bin/gdaltransform
%{gdalinstdir}/bin/nearblack
%{gdalinstdir}/bin/ogr*
%{gdalinstdir}/bin/8211*
%{gdalinstdir}/bin/s57*
%{gdalinstdir}/bin/testepsg
%{gdalinstdir}/bin/gnmanalyse
%{gdalinstdir}/bin/gnmmanage
%{gdalinstdir}/share/man/man1/gdal*.1*
%exclude %{gdalinstdir}/share/man/man1/gdal-config.1*
%exclude %{gdalinstdir}/share/man/man1/gdal2tiles.1*
%exclude %{gdalinstdir}/share/man/man1/gdal_fillnodata.1*
%exclude %{gdalinstdir}/share/man/man1/gdal_merge.1*
%exclude %{gdalinstdir}/share/man/man1/gdal_retile.1*
%exclude %{gdalinstdir}/share/man/man1/gdal_sieve.1*
%{gdalinstdir}/share/man/man1/nearblack.1*
%{gdalinstdir}/share/man/man1/ogr*.1*
%{gdalinstdir}/share/man/man1/gnm*.1

%files libs
%doc LICENSE.TXT NEWS PROVENANCE.TXT COMMITTERS PROVENANCE.TXT-fedora
%{gdalinstdir}/lib/libgdal.so.20
%{gdalinstdir}/lib/libgdal.so.20.*
%{gdalinstdir}/share/
#TODO: Possibly remove files like .dxf, .dgn, ...
%dir %{gdalinstdir}/lib/%{sname}plugins
%config(noreplace) %attr (644,root,root) %{_sysconfdir}/ld.so.conf.d/%{name}-gbd-libs.conf

%files devel
%{gdalinstdir}/bin/%{sname}-config
%{gdalinstdir}/bin/%{sname}-config-%{cpuarch}
%{gdalinstdir}/share/man/man1/gdal-config.1*
%dir %{gdalinstdir}/include/
%{gdalinstdir}/include/*.h
%{gdalinstdir}/lib/*.so
%{gdalinstdir}/lib/pkgconfig/%{sname}.pc
%{_libdir}/pkgconfig/%{name}.pc

%files doc
%doc gdal_frmts ogrsf_frmts

#TODO: jvm
#Should be managed by the Alternatives system and not via ldconfig
#The MDB driver is said to require:
#Download jackcess-1.2.2.jar, commons-lang-2.4.jar and
#commons-logging-1.1.1.jar (other versions might work)
#If you didn't specify --with-jvm-lib-add-rpath at
#Or as before, using ldconfig

%changelog
* Mon Aug 12 2019 Devrim Gündüz <devrim@gunduz.org> - 2.3.2-8
- GBDSQL için ilk paket
