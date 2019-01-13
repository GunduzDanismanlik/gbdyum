%global gbddir /usr/gbd/
%global gbdsname gbd-%{sname}
%global sname proj
%global projinstdir %{gbddir}%{sname}49

%ifarch ppc64 ppc64le
# Define the AT version and path.
%global atstring	at10.0
%global atpath		/opt/%{atstring}
%endif

Name:		%{gbdsname}49
Version:	4.9.3
Release:	3GBD%{?dist}
Epoch:		0
Summary:	Cartographic projection software (PROJ.4) for GBDSQL

Group:		Applications/Engineering
License:	MIT
URL:		http://trac.osgeo.org/proj
Source0:	http://download.osgeo.org/%{sname}/%{sname}-%{version}.tar.gz
Source1:	http://download.osgeo.org//proj/proj-datumgrid-1.5.zip
Source2:	%{name}-libs.conf

Patch0:		%{gbdsname}-4.8.0-removeinclude.patch
BuildRoot:	%{_tmppath}/%{sname}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:	libtool

%ifarch ppc64 ppc64le
BuildRequires:	advance-toolchain-%{atstring}-devel
%endif

%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

%package devel
Summary:	Development files for PROJ.4
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

%package nad
Summary:	US, Canadian, French and New Zealand datum shift grids for PROJ.4
Group:		Applications/Engineering
Requires:	%{name} = %{version}-%{release}
%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

%package epsg
Summary:	EPSG dataset for PROJ.4
Group:		Applications/Engineering
Requires:	%{name} = %{version}-%{release}
%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

%package static
Summary:	Development files for PROJ.4
Group:		Development/Libraries
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

%description nad
This package contains additional US and Canadian datum shift grids.

%description epsg
This package contains additional EPSG dataset.

%description static
This package contains libproj static library.

%prep
%setup -q -n %{sname}-%{version}

# disable internal libtool to avoid hardcoded r-path
for makefile in `find . -type f -name 'Makefile.in'`; do
sed -i 's|@LIBTOOL@|%{_bindir}/libtool|g' $makefile
done

# Prepare nad
cd nad
unzip %{SOURCE1}
cd ..
# fix shebag header of scripts
for script in `find nad/ -type f -perm -a+x`; do
sed -i -e '1,1s|:|#!/bin/bash|' $script
done

%build
# fix version info to respect new ABI
sed -i -e 's|5\:4\:5|6\:4\:6|' src/Makefile*

%ifarch ppc64 ppc64le
	CFLAGS="${CFLAGS} $(echo %{__global_cflags} | sed 's/-O2/-O3/g') -m64 -mcpu=power8 -mtune=power8 -I%{atpath}/include"
	CXXFLAGS="${CXXFLAGS} $(echo %{__global_cflags} | sed 's/-O2/-O3/g') -m64 -mcpu=power8 -mtune=power8 -I%{atpath}/include"
	LDFLAGS="-L%{atpath}/%{_lib}"
	CC=%{atpath}/bin/gcc; export CC
%endif
LDFLAGS="-Wl,-rpath,/usr/proj49/lib64 ${LDFLAGS}" ; export LDFLAGS
SHLIB_LINK="$SHLIB_LINK -Wl,-rpath,/usr/proj49/lib" ; export SHLIB_LINK

./configure --prefix=%{projinstdir} --without-jni
#make OPTIMIZE="$RPM_OPT_FLAGS" %{?_smp_mflags}
%{__make} %{?_smp_mflags}

%install
%{__rm} -rf %{buildroot}
%make_install
%{__install} -d %{buildroot}%{projinstdir}/share/%{sname}
%{__install} -d %{buildroot}%{projinstdir}/share/doc/
%{__install} -p -m 0644 nad/pj_out27.dist nad/pj_out83.dist nad/td_out.dist %{buildroot}%{projinstdir}/share/%{sname}
%{__install} -p -m 0755 nad/test27 nad/test83 nad/testvarious %{buildroot}%{projinstdir}/share/%{sname}
%{__install} -p -m 0644 nad/epsg %{buildroot}%{projinstdir}/share/%{sname}
%{__install} -p -m 0644 NEWS AUTHORS COPYING README ChangeLog %{buildroot}%{projinstdir}/share/doc/

# Install linker config file:
%{__mkdir} -p %{buildroot}%{_sysconfdir}/ld.so.conf.d/
%{__install} %{SOURCE2} %{buildroot}%{_sysconfdir}/ld.so.conf.d/

%check
pushd nad
# set test enviroment for porj
export PROJ_LIB=%{buildroot}%{projinstdir}/share/%{sname}
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH%{buildroot}%{projinstdir}/lib
# run tests for proj
./test27      %{buildroot}%{projinstdir}/bin/%{sname} || exit 0
./test83      %{buildroot}%{projinstdir}/bin/%{sname} || exit 0
./testntv2    %{buildroot}%{projinstdir}/bin/%{sname} || exit 0
./testvarious %{buildroot}%{projinstdir}/bin/%{sname} || exit 0
popd

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
%{projinstdir}/lib/libproj.so.12*
%config(noreplace) %attr (644,root,root) %{_sysconfdir}/ld.so.conf.d/%{name}-libs.conf

%files devel
%defattr(-,root,root,-)
%{projinstdir}/share/man/man3/*.3
%{projinstdir}/include/*.h
%{projinstdir}/lib/*.so
%{projinstdir}/lib/*.a
#%attr(0755,root,root) %{projinstdir}/pkgconfig/%{sname}.pc
%exclude %{projinstdir}/lib/libproj.a
%exclude %{projinstdir}/lib/libproj.la

%files static
%defattr(-,root,root,-)
%{projinstdir}/lib/libproj.a
%{projinstdir}/lib/libproj.la

%files nad
%defattr(-,root,root,-)
%doc nad/README
%attr(0755,root,root) %{projinstdir}/share/%{sname}/test27
%attr(0755,root,root) %{projinstdir}/share/%{sname}/test83
%attr(0755,root,root) %{projinstdir}/share/%{sname}/testvarious
%attr(0755,root,root) %{projinstdir}/lib/pkgconfig/%{sname}.pc
%exclude %{projinstdir}/share/%{sname}/epsg
%{projinstdir}/share/%{sname}

%files epsg
%defattr(-,root,root,-)
%doc nad/README
%attr(0644,root,root) %{projinstdir}/share/%{sname}/epsg

%changelog
* Mon Oct 15 2018 Devrim Gündüz <devrim@gunduz.org> - 0:4.9.3-3.1
- Rebuild against PostgreSQL 11.0

* Tue Nov 28 2017 Devrim Gündüz <devrim@gunduz.org> - 4.9.3-3
- Fix linker config file contents. Per report from Daniel Farina.

* Thu Nov 23 2017 Devrim Gündüz <devrim@gunduz.org> - 4.9.3-2
- Add a linker config file to satisfy GDAL and other packages
  which we use while building PostGIS.

* Tue Nov 21 2017 Devrim Gündüz <devrim@gunduz.org> 4.9.3-1
- Update to 4.9.3

* Mon Apr 24 2017 Devrim Gündüz <devrim@gunduz.org> 4.9.2-1
- Update to 4.9.2

* Wed Mar 11 2015 Devrim Gündüz <devrim@gunduz.org> 4.9.1-1
- Update to 4.9.1
- track soname so bumps are not a suprise.
- -devel: include .pc file here (left copy in -nad too)

* Thu Jul 26 2012 Devrim Gündüz <devrim@gunduz.org> - 0:4.8.0-2
- Add --without-jni to configure, for clean build..

* Wed Apr 04 2012 - Devrim Gündüz <devrim@gunduz.org> - 0:4.8.0-1
- Update to 4.8.0

* Thu Dec 10 2009 - Devrim Gündüz <devrim@gunduz.org> - 0:4.7.0-1
- Update to 4.7.0
- Update proj-datumgrid to 1.5
- Fix attr issue for epsg package.

* Tue Dec 2 2008 - Devrim Gündüz <devrim@gunduz.org> - 0:4.6.1-1
- Update to 4.6.1
- Update URLs

* Thu Apr 3 2008 - Devrim Gündüz <devrim@gunduz.org> - 0:4.6.0-1
- Initial build for yum.postgresql.org, based on Fedora/EPEL spec.

