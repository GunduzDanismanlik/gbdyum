%global		gbddir /usr/gbd/
%global		gbdsname gbd-%{sname}
%global		sname	ogdi
%global		gittag	4_1_0
%global		ogdimajorver 41
%global		ogdi41instdir %{gbddir}/ogdi%{ogdimajorver}

Name:		%{gbdsname}%{ogdimajorver}
Version:	4.1.0
Release:	2%{?dist}
Summary:	Open Geographic Datastore Interface
License:	BSD
URL:		http://ogdi.sourceforge.net/
# new project location is https://github.com/libogdi/ogdi
Source0:	https://github.com/libogdi/ogdi/archive/%{sname}_%{gittag}.tar.gz
Source1:	http://ogdi.sourceforge.net/ogdi.pdf
Source2:	%{name}-libs.conf
# https://bugzilla.redhat.com/show_bug.cgi?id=1470896
Patch0:		%{name}-4.1.0-sailer.patch
Patch1:		%{name}-4.1.0-mkinstalldirs.patch

BuildRequires:	gcc
BuildRequires:	unixODBC-devel
BuildRequires:	zlib-devel
BuildRequires:	expat-devel
BuildRequires:	tcl-devel
BuildRequires:	libtirpc-devel

%description
OGDI is the Open Geographic Datastore Interface. OGDI is an
application programming interface (API) that uses a standardized
access methods to work in conjunction with GIS software packages (the
application) and various geospatial data products. OGDI uses a
client/server architecture to facilitate the dissemination of
geospatial data products over any TCP/IP network, and a
driver-oriented approach to facilitate access to several geospatial
data products/formats.


%package devel
Summary:	OGDI header files and documentation
Requires:	%{name} = %{version}-%{release}
Requires:	pkgconfig
Requires:	zlib-devel expat-devel

%description devel
OGDI header files and developer's documentation.


%package odbc
Summary:	ODBC driver for OGDI
Requires:	%{name} = %{version}-%{release}

%description odbc
ODBC driver for OGDI.


%package tcl
Summary:	TCL wrapper for OGDI
Requires:	%{name} = %{version}-%{release}

%description tcl
TCL wrapper for OGDI.


%prep
%setup -q -n %{sname}-%{sname}_%{gittag}
%patch0 -p1
%patch1 -p0

# include documentation
%{__cp} -p %{SOURCE1} .


%build
TOPDIR=`pwd`; TARGET=Linux; export TOPDIR TARGET
INST_LIB=%{ogdi41instdir}/lib/;export INST_LIB
export CFG=debug # for -g

# removal of -D_FORTIFY_SOURCE from preprocessor flags seems not needed any more
# ogdits-3.1 test suite produces same result with and without the flag
export CFLAGS="$RPM_OPT_FLAGS -DDONT_TD_VOID -DUSE_TERMIO"
./configure \
	--prefix=%{ogdi41instdir} \
	--with-binconfigs \
	--with-expat \
	--with-zlib

# WARNING !!!
# using %{?_smp_mflags} may break build
%{__make}

# build tcl interface
%{__make} -C ogdi/tcl_interface \
	TCL_LINKLIB="-ltcl"

# build contributions
%{__make} -C contrib/gdal

# build odbc drivers
%{__make} -C ogdi/attr_driver/odbc \
	ODBC_LINKLIB="-lodbc"

%install
# export env
TOPDIR=`pwd`; TARGET=Linux; export TOPDIR TARGET
export DESTDIR=%{buildroot}
%{__make} install \
	INST_INCLUDE=%{buildroot}%{ogdi41instdir}/include/ \
	INST_LIB=%{buildroot}%{ogdi41instdir}/lib \
	INST_BIN=%{buildroot}%{ogdi41instdir}/bin

# install plugins olso
%{__make} install -C ogdi/tcl_interface \
	INST_LIB=%{buildroot}%{ogdi41instdir}/lib
%{__make} install -C contrib/gdal \
	INST_LIB=%{buildroot}%{ogdi41instdir}/lib
%{__make} install -C ogdi/attr_driver/odbc \
	INST_LIB=%{buildroot}%{ogdi41instdir}/lib

# remove example binary
%{__rm} %{buildroot}%{ogdi41instdir}/bin/example?

# we have multilib ogdi-config
%if "%{_lib}" == "lib"
%global cpuarch 32
%else
%global cpuarch 64
%endif

# fix file(s) for multilib issue
touch -r ogdi-config.in ogdi-config

# install pkgconfig file and ogdi-config
%{__mkdir} -p %{buildroot}%{ogdi41instdir}/lib/pkgconfig
%{__install} -p -m 644 ogdi.pc %{buildroot}%{ogdi41instdir}/lib/pkgconfig/
%{__install} -p -m 755 ogdi-config %{buildroot}%{ogdi41instdir}/bin/ogdi-config-%{cpuarch}
# ogdi-config wrapper for multiarch
cat > %{buildroot}%{ogdi41instdir}/bin/%{sname}-config <<EOF
#!/bin/bash

ARCH=\$(uname -m)
case \$ARCH in
x86_64 | ppc64 | ppc64le | ia64 | s390x | sparc64 | alpha | alphaev6 | aarch64 )
ogdi-config-64 \${*}
;;
*)
ogdi-config-32 \${*}
;;
esac
EOF
chmod 755 %{buildroot}%{ogdi41instdir}/bin/%{sname}-config
touch -r ogdi-config.in %{buildroot}%{ogdi41instdir}/bin/%{sname}-config

# Install linker config file:
%{__mkdir} -p %{buildroot}%{_sysconfdir}/ld.so.conf.d/
%{__install} %{SOURCE2} %{buildroot}%{_sysconfdir}/ld.so.conf.d/

%files
%doc LICENSE NEWS ChangeLog README
%{ogdi41instdir}/bin/gltpd
%{ogdi41instdir}/bin/ogdi_*
%{ogdi41instdir}/lib/libogdi.so*
%dir %{ogdi41instdir}/lib/ogdi
%exclude %{ogdi41instdir}/lib/%{sname}/liblodbc.so
%exclude %{ogdi41instdir}/lib/%{sname}/libecs_tcl.so
%{ogdi41instdir}/lib/%{sname}/lib*.so
%config(noreplace) %attr (644,root,root) %{_sysconfdir}/ld.so.conf.d/%{name}-libs.conf

%files devel
%doc ogdi.pdf
%doc ogdi/examples/example1/example1.c
%doc ogdi/examples/example2/example2.c
%{ogdi41instdir}/bin/%{sname}-config
%{ogdi41instdir}/bin/%{sname}-config-%{cpuarch}
%{ogdi41instdir}/lib/pkgconfig/%{sname}.pc
%dir %{ogdi41instdir}/include/
%{ogdi41instdir}/include/*.h

%files odbc
%{ogdi41instdir}/lib/%{sname}/liblodbc.so

%files tcl
%{ogdi41instdir}/lib/%{sname}/libecs_tcl.so


%changelog
* Fri Nov 15 2019 Devrim Gündüz <devrim@gunduz.org> - 4.1.0-2
* Initial ogdi41 packaging for GBDSQL
