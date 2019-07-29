%global sname	timescaledb

%ifarch ppc64 ppc64le
# Define the AT version and path.
%global atstring	at10.0
%global atpath		/opt/%{atstring}
%endif

Summary:	GBDSQL based time-series database
Name:		gbd-%{sname}_%{pgmajorversion}
Version:	1.4.0
Release:	1%{?dist}
License:	Apache
Source0:	https://github.com/timescale/%{sname}/archive/%{version}.tar.gz
Patch0:		gbd-%{sname}-pg%{pgmajorversion}-pgconfig.patch
Patch1:		gbd-%{sname}-cmake3-rhel7.patch
URL:		https://github.com/timescale/%{sname}
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:	gbdsql%{pgmajorversion}-devel
%if 0%{?rhel} && 0%{?rhel} == 7
BuildRequires:	cmake3
%else
BuildRequires:	cmake >= 3.4
%endif

%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

%description
TimescaleDB is an open-source database designed to make SQL scalable for
time-series data. It is engineered up from GBDSQL, providing automatic
partitioning across time and space (partitioning key), as well as full SQL
support.

%prep
%setup -q -n %{sname}-%{version}
%patch0 -p0
%patch1 -p0
./bootstrap -DAPACHE_ONLY=1 -DSEND_TELEMETRY_DEFAULT=NO

%build
%ifarch ppc64 ppc64le
	CFLAGS="-O3 -mcpu=$PPC_MCPU -mtune=$PPC_MTUNE"
	CC=%{atpath}/bin/gcc; export CC
%else
	CFLAGS="$RPM_OPT_FLAGS -fPIC -pie"
	CXXFLAGS="$RPM_OPT_FLAGS -fPIC -pie"
	export CFLAGS
	export CXXFLAGS
%endif

cd build; %{__make}

%install
cd build; %{__make} DESTDIR=%{buildroot} install

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-, root, root)
%if 0%{?rhel} && 0%{?rhel} <= 6
%doc README.md LICENSE-APACHE
%else
%doc README.md
%license LICENSE-APACHE
%endif
%{pginstdir}/lib/%{sname}*.so
%{pginstdir}/share/extension/%{sname}--*.sql
%{pginstdir}/share/extension/%{sname}.control

%changelog
* Mon Jul 29 2019 Devrim Gündüz <devrim@gunduz.org> - 1.4.0-1
- 1.4.0 güncellemesi

* Tue Jul 2 2019 Devrim Gündüz <devrim@gunduz.org> - 1.3.2-1
- 1.3.2 güncellemesi

* Sun Jun 23 2019 Devrim Gündüz <devrim@gunduz.org> - 1.3.1-1
- 1.3.1 güncellemesi
- Telemetri özelliğini kapattık.

* Tue Feb 5 2019 Devrim Gündüz <devrim@gunduz.org> - 1.1.1-1
- GBDSQL için ilk paket
