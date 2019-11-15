%global gbddir /usr/gbd/
%global gbdsname gbd-%{sname}
%global sname proj
%global projinstdir %{gbddir}%{sname}62

%if 0%{?rhel} && 0%{?rhel} == 7
%global sqlitepname	gbd-sqlite33
%global sqlite33dir	/usr/sqlite330
%else
%global sqlitepname	sqlite
%endif

%ifarch ppc64 ppc64le
# Define the AT version and path.
%global atstring	at10.0
%global atpath		/opt/%{atstring}
%endif

Name:		%{gbdsname}62
Version:	6.2.1
Release:	1GBD%{?dist}
Epoch:		0
Summary:	Cartographic projection software (PROJ) for GBDSQL

License:	MIT
URL:		https://proj.org
Source0:	http://download.osgeo.org/%{sname}/%{sname}-%{version}.tar.gz
Source1:	http://download.osgeo.org/%{sname}/%{sname}-datumgrid-1.8.zip
Source2:	%{name}-libs.conf


BuildRequires:	%{sqlitepname}-devel >= 3.7 gcc-c++
%if 0%{?fedora} > 28 || 0%{?rhel} == 8
Requires:	%{sqlitepname}-libs >= 3.7
%else
Requires:	%{sqlitepname}
%endif

%ifarch ppc64 ppc64le
BuildRequires:	advance-toolchain-%{atstring}-devel
%endif

%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

%package devel
Summary:	Development files for PROJ
Requires:	%{name} = %{version}-%{release}
%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

%package static
Summary:	Development files for PROJ
Requires:	%{name}-devel%{?_isa} = %{version}-%{release}
%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

%description
Proj and invproj perform respective forward and inverse transformation of
cartographic data to or from cartesian data with a wide range of selectable
projection functions. Proj docs: http://www.remotesensing.org/dl/new_docs/

%description devel
This package contains libproj and the appropriate header files and man pages.

%description static
This package contains libproj static library.

%prep
%setup -q -n %{sname}-%{version}

%build
%ifarch ppc64 ppc64le
	CFLAGS="${CFLAGS} $(echo %{__global_cflags} | sed 's/-O2/-O3/g') -m64 -mcpu=power8 -mtune=power8 -I%{atpath}/include"
	CXXFLAGS="${CXXFLAGS} $(echo %{__global_cflags} | sed 's/-O2/-O3/g') -m64 -mcpu=power8 -mtune=power8 -I%{atpath}/include"
	LDFLAGS="-L%{atpath}/%{_lib}"
	CC=%{atpath}/bin/gcc; export CC
%endif
LDFLAGS="-Wl,-rpath,%{projinstdir}/lib64 ${LDFLAGS}" ; export LDFLAGS
SHLIB_LINK="$SHLIB_LINK -Wl,-rpath,%{projinstdir}/lib" ; export SHLIB_LINK

%if 0%{?rhel} && 0%{?rhel} == 7
export SQLITE3_LIBS="-L%{sqlite33dir}/lib -lsqlite3"
export SQLITE3_INCLUDE_DIR='%{sqlite33dir}/include'
export PATH=%{sqlite33dir}/bin/:$PATH
LDFLAGS="-Wl,-rpath,%{sqlite33dir}/lib ${LDFLAGS}" ; export LDFLAGS
SHLIB_LINK="$SHLIB_LINK -Wl,-rpath,%{sqlite33dir}/lib" ; export SHLIB_LINK
%endif

./configure --prefix=%{projinstdir} --without-jni

%{__make} %{?_smp_mflags}

%install
%if 0%{?rhel} && 0%{?rhel} == 7
export SQLITE3_LIBS="-L%{sqlite33dir}/lib -lsqlite3"
export SQLITE3_INCLUDE_DIR='%{sqlite33dir}/include'
export PATH=%{sqlite33dir}/bin/:$PATH
LDFLAGS="-Wl,-rpath,%{sqlite33dir}/lib ${LDFLAGS}" ; export LDFLAGS
SHLIB_LINK="$SHLIB_LINK -Wl,-rpath,%{sqlite33dir}/lib" ; export SHLIB_LINK
%endif

%{__rm} -rf %{buildroot}
%make_install
%{__install} -d %{buildroot}%{projinstdir}/share/%{sname}
%{__install} -d %{buildroot}%{projinstdir}/share/doc/
%{__install} -p -m 0644 NEWS AUTHORS COPYING README ChangeLog %{buildroot}%{projinstdir}/share/doc/

# Install linker config file:
%{__mkdir} -p %{buildroot}%{_sysconfdir}/ld.so.conf.d/
%{__install} %{SOURCE2} %{buildroot}%{_sysconfdir}/ld.so.conf.d/

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
%doc %{projinstdir}/share/doc/*
%{projinstdir}/bin/*
%{projinstdir}/share/man/man1/*.1
%{projinstdir}/share/proj/*
%{projinstdir}/lib/libproj.so.15*
%config(noreplace) %attr (644,root,root) %{_sysconfdir}/ld.so.conf.d/%{name}-libs.conf

%files devel
%defattr(-,root,root,-)
%{projinstdir}/share/man/man3/*.3
%{projinstdir}/include/*.h
%{projinstdir}/include/proj/*
%{projinstdir}/include/proj_json_streaming_writer.hpp
%{projinstdir}/lib/*.so
%{projinstdir}/lib/*.a
%attr(0755,root,root) %{projinstdir}/lib/pkgconfig/%{sname}.pc
%exclude %{projinstdir}/lib/libproj.a
%exclude %{projinstdir}/lib/libproj.la
%{projinstdir}/include/proj/util.hpp

%files static
%defattr(-,root,root,-)
%{projinstdir}/lib/libproj.a
%{projinstdir}/lib/libproj.la

%changelog
* Fri Nov 15 2019 Devrim Gündüz <devrim@gunduz.org> - 0:6.2.1-2
- GBDSQL için ilk paket
