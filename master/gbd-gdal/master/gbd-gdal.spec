%global	gbddir /usr/gbd
%global	gbdsname gbd-%{sname}
%global	sname gdal
%global	gdalinstdir /usr/%{gbdsname}

%ifarch ppc64 ppc64le
# Define the AT version and path.
%global atstring	at10.0
%global atpath		/opt/%{atstring}
%endif
# Tests can be of a different version
%global testversion 1.11.4
%global run_tests 1

%global with_spatialite 1
%global spatialite "--with-spatialite"

# No ppc64 build for spatialite in EL7
# https://bugzilla.redhat.com/show_bug.cgi?id=663938
%if 0%{?rhel} == 7
%ifnarch ppc64
%global with_spatialite 0
%global spatialite "--without-spatialite"
%endif
%endif


Name:		%{gbdsname}
Version:	1.11.4
Release:	12%{?dist}
Summary:	GIS file format library
Group:		System Environment/Libraries
License:	MIT
URL:		http://www.gdal.org
# Source0:   http://download.osgeo.org/gdal/%%{version}/gdal-%%{version}.tar.xz
# See PROVENANCE.TXT-fedora and the cleaner script for details!

Source0:	%{sname}-%{version}-fedora.tar.xz
Source1:	http://download.osgeo.org/%{sname}/%{testversion}/%{sname}autotest-%{testversion}.tar.gz
Source2:	%{sname}.pom

# Cleaner script for the tarball
Source3:	%{sname}-cleaner.sh

Source4:	PROVENANCE.TXT-fedora

# Patch to use system g2clib
Patch1:		%{sname}-g2clib.patch
# Patch for Fedora JNI library location
Patch2:		%{sname}-jni.patch

# https://trac.osgeo.org/gdal/ticket/6159#ticket
Patch3:		%{sname}-2.0.1-iso8211-include.patch

# Fedora uses Alternatives for Java
Patch8:		%{sname}-1.9.0-java.patch

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:	ant
BuildRequires:	armadillo-devel
BuildRequires:	cfitsio-devel
BuildRequires:	CharLS-devel
BuildRequires:	chrpath
BuildRequires:	curl-devel
BuildRequires:	doxygen
BuildRequires:	expat-devel
BuildRequires:	fontconfig-devel
BuildRequires:	freexl-devel
BuildRequires:	g2clib-static
BuildRequires:	gbd-geos37-devel
BuildRequires:	ghostscript
BuildRequires:	hdf-devel
BuildRequires:	hdf-static
BuildRequires:	hdf5-devel
BuildRequires:	java-devel >= 1:1.6.0
BuildRequires:	jasper-devel
BuildRequires:	jpackage-utils
BuildRequires:	libgeotiff-devel
BuildRequires:	libgta-devel
BuildRequires:	libjpeg-devel
BuildRequires:	libpng-devel

%if %{with_spatialite}
BuildRequires: libspatialite-devel
%endif

BuildRequires:	libtiff-devel
BuildRequires:	libwebp-devel
BuildRequires:	libtool
BuildRequires:	giflib-devel
BuildRequires:	netcdf-devel
BuildRequires:	libdap-devel
BuildRequires:	librx-devel
BuildRequires:	mysql-devel
BuildRequires:	numpy
BuildRequires:	pcre-devel
BuildRequires:	ogdi-devel
BuildRequires:	openjpeg2-devel
BuildRequires:	perl(ExtUtils::MakeMaker)
BuildRequires:	pkgconfig
BuildRequires:	poppler-devel
BuildRequires:	gbdsql%{pgmajorversion}-devel
BuildRequires:	gbd-proj49-devel
BuildRequires:	python2-devel
BuildRequires:	sqlite-devel
BuildRequires:	swig
BuildRequires:	texlive-latex
%if 0%{?fedora} >= 20
BuildRequires:	texlive-collection-fontsrecommended
BuildRequires:	texlive-collection-langcyrillic
BuildRequires:	texlive-collection-langportuguese
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

# Run time dependency for gpsbabel driver
Requires:	gpsbabel

Requires:	%{sname}-libs%{?_isa} = %{version}-%{release}

%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

%ifarch ppc64 ppc64le
BuildRequires:	advance-toolchain-%{atstring}-devel
%endif

# Enable/disable generating refmans
%global build_refman 1

# We have multilib triage
%if "%{_lib}" == "lib"
  %global cpuarch 32
%else
  %global cpuarch 64
%endif

%if ! (0%{?fedora} || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
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
Summary: Development files for the GDAL file format library
Group: Development/Libraries
%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

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
Group:		System Environment/Libraries
Obsoletes:	%{name}-ruby < 1.11.0-1
%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

%description libs
This package contains the GDAL file format library.

%package java
Summary:	Java modules for the GDAL file format library
Group:		Development/Libraries
Requires:	jpackage-utils
Requires:	%{name}-libs%{?_isa} = %{version}-%{release}
%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

%description java
The GDAL Java modules provide support to handle multiple GIS file formats.


%package	javadoc
Summary:	Javadocs for %{name}
Group:		Documentation
Requires:	jpackage-utils
BuildArch:	noarch
%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

%description javadoc
This package contains the API documentation for %{name}.

%package perl
Summary:	Perl modules for the GDAL file format library
Group:		Development/Libraries
Requires:	%{name}-libs%{?_isa} = %{version}-%{release}
Requires:	perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

%description perl
The GDAL Perl modules provide support to handle multiple GIS file formats.


%package python
Summary:	Python modules for the GDAL file format library
Group:		Development/Libraries
Requires:	numpy
Requires:	%{name}-libs%{?_isa} = %{version}-%{release}
%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

%description python
The GDAL Python modules provide support to handle multiple GIS file formats.
The package also includes a couple of useful utilities in Python.


%package doc
Summary:	Documentation for GDAL
Group:		Documentation
BuildArch:	noarch
%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

%description doc
This package contains HTML and PDF documentation for GDAL.

# We don't want to provide private Python extension libs
%global __provides_exclude_from ^%{python_sitearch}/.*\.so$

%prep
%setup -q -n %{name}-%{version}-fedora

# Unpack tests to the same directory
%setup -q -D -a 1 -n %{name}-%{version}-fedora

# Delete bundled libraries
rm -rf frmts/zlib
rm -rf frmts/png/libpng
rm -rf frmts/gif/giflib
rm -rf frmts/jpeg/libjpeg \
    frmts/jpeg/libjpeg12
rm -rf frmts/gtiff/libgeotiff \
    frmts/gtiff/libtiff
rm -r frmts/grib/degrib18/g2clib-1.0.4

%patch1 -p1 -b .g2clib~
%patch2 -p1 -b .jni~
%patch3 -p1 -b .iso8211~
%patch8 -p1 -b .java~

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

# Solved for 2.0
for f in ogr/ogrsf_frmts/gpsbabel ogr/ogrsf_frmts/pgdump port apps; do
pushd $f
  chmod 644 *.cpp *.h
popd
done

# Fix build order with parallel make
# http://trac.osgeo.org/gdal/ticket/5346
sed -i '/^swig-modules:/s/lib-target/apps-target/' GNUmakefile

# Workaround about wrong result in configure
# armadillo returns a warning about gcc versions 4.7.0 or 4.7.1
# due to http://gcc.gnu.org/bugzilla/show_bug.cgi?id=53549
# configure interprets the result as an error so ignore it
# this patch can/should be removed after gcc 4.7.2 is released
sed -i 's|if test -z "`${CXX} testarmadillo.cpp -o testarmadillo -larmadillo 2>&1`"|if true|' configure

# Replace hard-coded library- and include paths
%ifnarch aarch64 ppc64le
# workaround libtool bug in RHEL 7.2 (rhbz#1287191)
sed -i 's|@LIBTOOL@|%{_bindir}/libtool|g' GDALmake.opt.in
%endif
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
sed -i 's|libproj.so|libproj.so.12|g' ogr/ogrct.cpp

# Fix Python installation path
sed -i 's|setup.py install|setup.py install --root=%{buildroot}|' swig/python/GNUmakefile

# Must be corrected for 64 bit architectures other than Intel
# http://trac.osgeo.org/gdal/ticket/4544
# Should be gone in 2.0
sed -i 's|test \"$ARCH\" = \"x86_64\"|test \"$libdir\" = \"/usr/lib64\"|g' configure

# Adjust check for LibDAP version
# http://trac.osgeo.org/gdal/ticket/4545
%if %cpuarch == 64
  sed -i 's|with_dods_root/lib|with_dods_root/lib64|' configure
%endif

# Fix mandir
sed -i "s|^mandir=.*|mandir='\${prefix}/share/man'|" configure

# Activate support for JPEGLS
sed -i 's|^#HAVE_CHARLS|HAVE_CHARLS|' GDALmake.opt.in
sed -i 's|#CHARLS_INC = -I/path/to/charls_include|CHARLS_INC = -I%{_includedir}/CharLS|' GDALmake.opt.in
sed -i 's|#CHARLS_LIB = -L/path/to/charls_lib -lCharLS|CHARLS_LIB = -lCharLS|' GDALmake.opt.in

# Replace default plug-in dir
# Solved in 2.0
# http://trac.osgeo.org/gdal/ticket/4444
%if %cpuarch == 64
  sed -i 's|GDAL_PREFIX "/lib/gdalplugins"|GDAL_PREFIX "/lib64/gdalplugins"|' \
    gcore/gdaldrivermanager.cpp \
    ogr/ogrsf_frmts/generic/ogrsfdriverregistrar.cpp
%endif

# Remove man dir, as it blocks a build target.
# It obviously slipped into the tarball and is not in Trunk (April 17th, 2011)
#rm -rf man


%build
#TODO: Couldn't I have modified that in the prep section?
%ifarch sparcv9 sparc64 s390 s390x
export CFLAGS="$RPM_OPT_FLAGS -fPIC"
%else
export CFLAGS="$RPM_OPT_FLAGS -fpic"
%endif
export CXXFLAGS="$CFLAGS -I%{_includedir}/libgeotiff"
export CPPFLAGS="$CPPFLAGS -I%{_includedir}/libgeotiff"
%ifarch ppc64 ppc64le
	CFLAGS="${CFLAGS} $(echo %{__global_cflags} | sed 's/-O2/-O3/g') -m64 -mcpu=power8 -mtune=power8 -I%{atpath}/include"
	CXXFLAGS="${CXXFLAGS} $(echo %{__global_cflags} | sed 's/-O2/-O3/g') -m64 -mcpu=power8 -mtune=power8 -I%{atpath}/include"
	LDFLAGS="-L%{atpath}/%{_lib}"
	CC=%{atpath}/bin/gcc; export CC
%endif

# For future reference:
# epsilon: Stalled review -- https://bugzilla.redhat.com/show_bug.cgi?id=660024
# Building without pgeo driver, because it drags in Java

%configure \
	LIBS=-lgrib2c \
	--with-autoload=%{_libdir}/%{name}plugins \
	--datadir=%{_datadir}/%{name}/ \
	--includedir=%{_includedir}/%{name}/ \
	--prefix=%{gdalinstdir} \
	--without-bsb \
	--with-armadillo          \
	--with-curl               \
	--with-cfitsio=%{_prefix} \
	--with-dods-root=%{_prefix} \
	--with-expat              \
	--with-freexl             \
	--with-geos=/%{gbddir}/geos37/bin/geos-config               \
	--with-static-proj4=%{gbddir}/proj49/	\
	--with-geotiff=external   \
	--with-gif                \
	--with-gta                \
	--with-hdf4               \
	--with-hdf5               \
	--with-jasper             \
	--with-java               \
	--with-jpeg               \
	--without-jpeg12          \
	--with-liblzma            \
	--with-libtiff=external   \
	--with-libz               \
	--without-mdb             \
	--with-mysql              \
	--with-netcdf             \
	--with-odbc               \
	--with-ogdi               \
	--without-msg             \
	--with-openjpeg           \
	--with-pcraster           \
	--with-pg=%{pginstdir}/bin/pg_config		\
	--with-png                \
	--with-poppler            \
	%{spatialite}             \
	--with-sqlite3            \
	--with-threads            \
	--with-webp               \
	--with-xerces             \
	--enable-shared           \
	--with-perl               \
	--with-python

# {?_smp_mflags} doesn't work; Or it does -- who knows!
make %{?_smp_mflags}
make man
make docs

# Make Perl modules
pushd swig/perl
  perl Makefile.PL;  make;
  echo > Makefile.PL;
popd

# Build some utilities, as requested in BZ #1271906
pushd ogr/ogrsf_frmts/s57/
  make all
popd

pushd frmts/iso8211/
  make all
popd

# Install the Perl modules in the right place
sed -i 's|INSTALLDIRS = site|INSTALLDIRS = vendor|' swig/perl/Makefile_*

# Don't append installation info to pod
#TODO: What about the pod?
sed -i 's|>> $(DESTINSTALLARCHLIB)\/perllocal.pod|> \/dev\/null|g' swig/perl/Makefile_*

# Make Java module and documentation
pushd swig/java
  make
  ./make_doc.sh
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

make    DESTDIR=%{buildroot} \
        install \
        install-man

install -pm 755 ogr/ogrsf_frmts/s57/s57dump %{buildroot}%{_bindir}
install -pm 755 frmts/iso8211/8211createfromxml %{buildroot}%{_bindir}
install -pm 755 frmts/iso8211/8211dump %{buildroot}%{_bindir}
install -pm 755 frmts/iso8211/8211view %{buildroot}%{_bindir}

# Directory for auto-loading plugins
mkdir -p %{buildroot}%{_libdir}/%{name}plugins

#TODO: Don't do that?
find %{buildroot}%{perl_vendorarch} -name "*.dox" -exec rm -rf '{}' \;
rm -f %{buildroot}%{perl_archlib}/perllocal.pod

# Correct permissions
#TODO and potential ticket: Why are the permissions not correct?
find %{buildroot}%{perl_vendorarch} -name "*.so" -exec chmod 755 '{}' \;
find %{buildroot}%{perl_vendorarch} -name "*.pm" -exec chmod 644 '{}' \;

touch -r NEWS swig/java/gdal.jar
mkdir -p %{buildroot}%{_javadir}
cp -p swig/java/gdal.jar  \
    %{buildroot}%{_javadir}/%{name}.jar

# Install Maven pom and update version number
install -dm 755 %{buildroot}%{_mavenpomdir}
install -pm 644 %{SOURCE2} %{buildroot}%{_mavenpomdir}/JPP-%{name}.pom
sed -i 's|<version></version>|<version>%{version}</version>|' %{buildroot}%{_mavenpomdir}/JPP-%{name}.pom

# Create depmap fragment
%add_maven_depmap JPP-%{name}.pom %{name}.jar

# 775 on the .so?
# copy JNI libraries and links, non versioned link needed by JNI
# What is linked here?
mkdir -p %{buildroot}%{_jnidir}/%{name}
cp -pl swig/java/.libs/*.so*  \
    %{buildroot}%{_jnidir}/%{name}/
chrpath --delete %{buildroot}%{_jnidir}/%{name}/*jni.so*

# Install Java API documentation in the designated place
mkdir -p %{buildroot}%{_javadocdir}/%{name}
cp -pr swig/java/java/org %{buildroot}%{_javadocdir}/%{name}

# Install refmans
for docdir in %{docdirs}; do
  pushd $docdir
    path=%{_builddir}/%{name}-%{version}-fedora/refman
    mkdir -p $path/html/$docdir
    cp -r html $path/html/$docdir

    # Install all Refmans
    %if %{build_refman}
        if [ -f latex/refman.pdf ]; then
          mkdir -p $path/pdf/$docdir
          cp latex/refman.pdf $path/pdf/$docdir
        fi
    %endif
  popd
done

# Install formats documentation
for dir in gdal_frmts ogrsf_frmts; do
  mkdir -p $dir
  find frmts -name "*.html" -exec install -p -m 644 '{}' $dir \;
done

#TODO: Header date lost during installation
# Install multilib cpl_config.h bz#430894
install -p -D -m 644 port/cpl_config.h %{buildroot}%{_includedir}/%{name}/cpl_config-%{cpuarch}.h
# Create universal multilib cpl_config.h bz#341231
# The problem is still there in 1.9.
#TODO: Ticket?

#>>>>>>>>>>>>>
cat > %{buildroot}%{_includedir}/%{name}/cpl_config.h <<EOF
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
mv %{buildroot}%{_bindir}/%{name}-config %{buildroot}%{_bindir}/%{name}-config-%{cpuarch}
#>>>>>>>>>>>>>
cat > %{buildroot}%{_bindir}/%{name}-config <<EOF
#!/bin/bash

ARCH=\$(uname -m)
case \$ARCH in
x86_64 | ppc64 | ppc64le | ia64 | s390x | sparc64 | alpha | alphaev6 | aarch64 )
%{name}-config-64 \${*}
;;
*)
%{name}-config-32 \${*}
;;
esac
EOF
#<<<<<<<<<<<<<
touch -r NEWS %{buildroot}%{_bindir}/%{name}-config
chmod 755 %{buildroot}%{_bindir}/%{name}-config

# Clean up junk
rm -f %{buildroot}%{_bindir}/*.dox

#jni-libs and libgdal are also built static (*.a)
#.exists and .packlist stem from Perl
for junk in {*.a,*.la,*.bs,.exists,.packlist} ; do
  find %{buildroot} -name "$junk" -exec rm -rf '{}' \;
done

# Don't duplicate license files
rm -f %{buildroot}%{_datadir}/%{name}/LICENSE.TXT

# Throw away random API man mages plus artefact seemingly caused by Doxygen 1.8.1 or 1.8.1.1
for f in 'GDAL*' BandProperty ColorAssociation CutlineTransformer DatasetProperty EnhanceCBInfo ListFieldDesc NamedColor OGRSplitListFieldLayer VRTBuilder; do
  rm -rf %{buildroot}%{_mandir}/man1/$f.1*
done
#TODO: What's that?
rm -f %{buildroot}%{_mandir}/man1/*_%{name}-%{version}-fedora_apps_*
rm -f %{buildroot}%{_mandir}/man1/_home_rouault_dist_wrk_gdal_apps_.1*

%check
%if %{run_tests}
for i in -I/usr/lib/jvm/java/include{,/linux}; do
    java_inc="$java_inc $i"
done


pushd %{name}autotest-%{testversion}
  # Export test enviroment
  export PYTHONPATH=$PYTHONPATH:%{buildroot}%{python_sitearch}
  export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:%{buildroot}%{_libdir}

  export GDAL_DATA=%{buildroot}%{_datadir}/%{name}/

  # Enable these tests on demand
  #export GDAL_RUN_SLOW_TESTS=1
  #export GDAL_DOWNLOAD_TEST_DATA=1

  # Remove some test cases that would require special preparation
  rm -rf ogr/ogr_pg.py        # No database available
  rm -rf ogr/ogr_mysql.py     # No database available
  rm -rf osr/osr_esri.py      # ESRI datum absent
  rm -rf osr/osr_erm.py       # File from ECW absent

  # Run tests but force normal exit in the end
  ./run_all.py || true
popd
%endif


%post libs
%ifarch ppc64 ppc64le
%{atpath}/sbin/ldconfig
%else
/sbin/ldconfig
%endif

%postun libs
%ifarch ppc64 ppc64le
%{atpath}/sbin/ldconfig
%else
/sbin/ldconfig
%endif

%files
%{_bindir}/gdallocationinfo
%{_bindir}/gdal_contour
%{_bindir}/gdal_rasterize
%{_bindir}/gdal_translate
%{_bindir}/gdaladdo
%{_bindir}/gdalinfo
%{_bindir}/gdaldem
%{_bindir}/gdalbuildvrt
%{_bindir}/gdaltindex
%{_bindir}/gdalwarp
%{_bindir}/gdal_grid
%{_bindir}/gdalenhance
%{_bindir}/gdalmanage
%{_bindir}/gdalserver
%{_bindir}/gdalsrsinfo
%{_bindir}/gdaltransform
%{_bindir}/nearblack
%{_bindir}/ogr*
%{_bindir}/8211*
%{_bindir}/s57*
%{_bindir}/testepsg
%{_mandir}/man1/gdal*.1*
%exclude %{_mandir}/man1/gdal-config.1*
%exclude %{_mandir}/man1/gdal2tiles.1*
%exclude %{_mandir}/man1/gdal_fillnodata.1*
%exclude %{_mandir}/man1/gdal_merge.1*
%exclude %{_mandir}/man1/gdal_retile.1*
%exclude %{_mandir}/man1/gdal_sieve.1*
%{_mandir}/man1/nearblack.1*
%{_mandir}/man1/ogr*.1*

%files libs
%doc LICENSE.TXT NEWS PROVENANCE.TXT COMMITERS PROVENANCE.TXT-fedora
%{_libdir}/libgdal.so.*
%{_datadir}/%{name}
#TODO: Possibly remove files like .dxf, .dgn, ...
%dir %{_libdir}/%{name}plugins

%files devel
%{_bindir}/%{name}-config
%{_bindir}/%{name}-config-%{cpuarch}
%{_mandir}/man1/gdal-config.1*
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*.h
%{_libdir}/*.so
%{_libdir}/pkgconfig/%{name}.pc

# Can I even have a separate Java package anymore?
%files java -f .mfiles
%doc swig/java/apps
%{_jnidir}/%{name}/

%files javadoc
%{_javadocdir}/%{name}

%files perl
%doc swig/perl/README
%{perl_vendorarch}/*

%files python
%doc swig/python/README.txt
%doc swig/python/samples
#TODO: Bug with .py files in EPEL 5 bindir, see http://fedoraproject.org/wiki/EPEL/GuidelinesAndPolicies
%{_bindir}/*.py
%{_mandir}/man1/pct2rgb.1*
%{_mandir}/man1/rgb2pct.1*
%{_mandir}/man1/gdal2tiles.1*
%{_mandir}/man1/gdal_fillnodata.1*
%{_mandir}/man1/gdal_merge.1*
%{_mandir}/man1/gdal_retile.1*
%{_mandir}/man1/gdal_sieve.1*
%{python_sitearch}/osgeo
%{python_sitearch}/GDAL-%{version}-py*.egg-info
%{python_sitearch}/osr.py*
%{python_sitearch}/ogr.py*
%{python_sitearch}/gdal*.py*

%files doc
%doc gdal_frmts ogrsf_frmts refman

#TODO: jvm
#Should be managed by the Alternatives system and not via ldconfig
#The MDB driver is said to require:
#Download jackcess-1.2.2.jar, commons-lang-2.4.jar and
#commons-logging-1.1.1.jar (other versions might work)
#If you didn't specify --with-jvm-lib-add-rpath at
#Or as before, using ldconfig

%changelog

* Sun Jan 28 2018 Devrim Gündüz <devrim@gunduz.org> - 1.11.4-12
- Initial version of gbd-gdal
