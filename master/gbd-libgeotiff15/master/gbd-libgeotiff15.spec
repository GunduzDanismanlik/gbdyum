%global gbddir /usr/gbd/
%global gbdsname gbd-%{sname}
%global sname libgeotiff
%global	libgeotiffversion 15
%global	libgeotiffinstdir %{gbddir}/%{sname}%{libgeotiffversion}
%global	projinstdir %{gbddir}/proj62/

Name:		%{gbdsname}%{libgeotiffversion}
Version:	1.5.1
Release:	3%{?dist}
Summary:	GeoTIFF format library
License:	MIT
URL:		http://trac.osgeo.org/geotiff/
Source0:	http://download.osgeo.org/geotiff/libgeotiff/libgeotiff-%{version}.tar.gz
Source2:	%{name}-libs.conf
BuildRequires:	libtiff-devel libjpeg-devel gbd-proj62-devel zlib-devel

%description
GeoTIFF represents an effort by over 160 different remote sensing,
GIS, cartographic, and surveying related companies and organizations
to establish a TIFF based interchange format for georeferenced
raster imagery.

%package devel
Summary:	Development Libraries for the GeoTIFF file format library
Requires:	pkgconfig libtiff-devel
Requires:	%{name} = %{version}-%{release}

%description devel
The GeoTIFF library provides support for development of geotiff image format.

%prep
%setup -q -n %{sname}-%{version}

# fix wrongly encoded files from tarball
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

# remove junks
find . -name ".cvsignore" -exec rm -rf '{}' \;

%build

# disable -g flag removal
sed -i 's| \| sed \"s\/-g \/\/\"||g' configure

# use gcc -shared instead of ld -shared to build with -fstack-protector
sed -i 's|LD_SHARED=@LD_SHARED@|LD_SHARED=@CC@ -shared|' Makefile.in

./configure \
	--prefix=%{libgeotiffinstdir}	\
	--includedir=%{libgeotiffinstdir}/include/ \
	--mandir=%{libgeotiffinstdir}/man	\
	--libdir=%{libgeotiffinstdir}/lib	\
	--with-proj=%{projinstdir}	\
	--with-tiff		\
	--with-jpeg		\
	--with-zip
# WARNING
# disable %{?_smp_mflags}
# it breaks compile

%{__make}

%install
# install libgeotiff
%{__make} install DESTDIR=%{buildroot} INSTALL="%{__install} -p"

# install manualy some file
%{__mkdir} -p %{buildroot}%{libgeotiffinstdir}/bin
%{__install} -p -m 755 bin/makegeo %{buildroot}%{libgeotiffinstdir}/bin

# install pkgconfig file
cat > %{name}.pc <<EOF
prefix=%{libgeotiffinstdir}
exec_prefix=%{libgeotiffinstdir}
libdir=%{libgeotiffinstdir}/lib
includedir=%{libgeotiffinstdir}/include

Name: %{name}
Description: GeoTIFF file format library
Version: %{version}
Libs: -L\${libdir} -lgeotiff
Cflags: -I\${includedir}
EOF

%{__mkdir} -p %{buildroot}%{libgeotiffinstdir}/lib/pkgconfig/
%{__install} -p -m 644 %{name}.pc %{buildroot}%{libgeotiffinstdir}/lib/pkgconfig/

#clean up junks
%{__rm} -rf %{buildroot}%{libgeotiffinstdir}/lib/*.a
%{__rm} -f %{buildroot}%{libgeotiffinstdir}/lib/*.la

# Install linker config file:
%{__mkdir} -p %{buildroot}%{_sysconfdir}/ld.so.conf.d/
%{__install} %{SOURCE2} %{buildroot}%{_sysconfdir}/ld.so.conf.d/

%clean
%{__rm} -rf %{buildroot}

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%doc ChangeLog LICENSE README
%{libgeotiffinstdir}/bin/applygeo
%{libgeotiffinstdir}/bin/geotifcp
%{libgeotiffinstdir}/bin/listgeo
%{libgeotiffinstdir}/bin/makegeo
%{libgeotiffinstdir}/lib/libgeotiff.so.*
%{libgeotiffinstdir}/man/man1/listgeo.1
%{libgeotiffinstdir}/man/man1/geotifcp.1
%{libgeotiffinstdir}/man/man1/applygeo.1
%config(noreplace) %attr (644,root,root) %{_sysconfdir}/ld.so.conf.d/%{name}-libs.conf

%files devel
%dir %{libgeotiffinstdir}/include
%attr(0644,root,root) %{libgeotiffinstdir}/include/*.h
%attr(0644,root,root) %{libgeotiffinstdir}/include/*.inc
%{libgeotiffinstdir}/lib/libgeotiff.so
%{libgeotiffinstdir}/lib/pkgconfig/%{name}.pc


%changelog
* Fri Nov 15 2019 2019 Devrim Gündüz <devrim@gunduz.org> - 1.5.1-3
- Initial build for GBDSQL, to satisfy dependency for gdal (and so PostGIS),
  based on EPEL spec.
