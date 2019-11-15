%global debug_package %{nil}

%ifarch ppc64 ppc64le
# Define the AT version and path.
%global atstring	at10.0
%global atpath		/opt/%{atstring}
%endif

Name:		gbdsql%{pgmajorversion}-odbc
Summary:	GBDSQL ODBC driver
Version:	12.00.0000
Release:	1GBD%{?dist}
License:	LGPLv2
Group:		Applications/Databases
URL:		https://odbc.postgresql.org/

Source0:	http://download.postgresql.org/pub/odbc/versions/src/psqlodbc-%{version}.tar.gz
Source1:	acinclude.m4

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:	unixODBC-devel
BuildRequires:	libtool automake autoconf gbdsql%{pgmajorversion}-devel
BuildRequires:	openssl-devel krb5-devel pam-devel zlib-devel readline-devel

%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

%ifarch ppc64 ppc64le
BuildRequires:	advance-toolchain-%{atstring}-devel
%endif

Requires:	gbdsql%{pgmajorversion}-libs
Provides:	gbdsql-odbc%{?_isa} >= 08.00.0100

# This spec file and ancillary files are licensed in accordance with
# the psqlodbc license.

%description
This package includes the driver needed for applications to access a
GBDSQL system via ODBC (Open Database Connectivity).

%prep
%setup -q -n psqlodbc-%{version}
%ifarch ppc64le
sed -i "s:elf64ppc:elf64lppc:g" configure
%endif

# Some missing macros.  Courtesy Owen Taylor <otaylor@redhat.com>.
%{__cp} -p %{SOURCE1} .
# Use build system's libtool.m4, not the one in the package.
%{__rm} -f libtool.m4

libtoolize --force  --copy
aclocal -I .
automake --add-missing --copy
autoconf
autoheader

%build

chmod +x configure
%ifarch ppc64 ppc64le
	CFLAGS="${CFLAGS} $(echo %{__global_cflags} | sed 's/-O2/-O3/g') -DENABLE_NLS -O3 -m64 -mcpu=power8 -mtune=power8 -I%{atpath}/include"
	CXXFLAGS="${CXXFLAGS} $(echo %{__global_cflags} | sed 's/-O2/-O3/g') -m64 -mcpu=power8 -mtune=power8 -I%{atpath}/include"
	LDFLAGS="-L%{atpath}/%{_lib}"
	CC=%{atpath}/bin/gcc; export CC
%endif
	./configure --with-unixodbc --with-libpq=%{pginstdir} -disable-dependency-tracking --libdir=%{_libdir}
%{__make}

%install
%{__rm} -rf %{buildroot}
%makeinstall

# Provide the old library name "psqlodbc.so" as a symlink,
# and remove the rather useless .la file

install -d -m 755 %{buildroot}%{pginstdir}/lib
pushd %{buildroot}%{pginstdir}/lib
	ln -s psqlodbcw.so psqlodbc.so
	mv %{buildroot}%{_libdir}/psqlodbc*.so %{buildroot}%{pginstdir}/lib
	rm %{buildroot}%{_libdir}/psqlodbcw.la
	rm %{buildroot}%{_libdir}/psqlodbca.la
popd
strip %{buildroot}%{pginstdir}/lib/*.so

%clean
%{__rm} -rf %{buildroot}

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%attr(755,root,root) %{pginstdir}/lib/psqlodbcw.so
%{pginstdir}/lib/psqlodbc.so
%{pginstdir}/lib/psqlodbca.so
%if 0%{?rhel} && 0%{?rhel} <= 6
%doc license.txt readme.txt
%else
%doc readme.txt
%license license.txt
%endif

%changelog
* Fri Nov 15 2019 Devrim Gündüz <devrim@gunduzdanismanlik.com> - 12.00.0000-1GBD
- 12.00.0000 güncellemesi

* Sun Jan 27 2019 Devrim Gündüz <devrim@gunduzdanismanlik.com> - 11.00.0000-1GBD
- GBDSQL için ilk paket
