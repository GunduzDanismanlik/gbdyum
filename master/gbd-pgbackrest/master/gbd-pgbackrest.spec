%global debug_package %{nil}
%global sname	pgbackrest
%global gbddir	/usr/gbd
Summary:	Reliable PostgreSQL Backup & Restore
Name:		gbd-%{sname}
Version:	2.14
Release:	1GBD%{?dist}
License:	MIT
Group:		Applications/Databases
Url:		http://www.pgbackrest.org/
Source0:	https://github.com/pgbackrest/pgbackrest/archive/release/%{version}.tar.gz
Source1:	gbd-pgbackrest-conf.patch
Patch0:		gbd-pgbackrest-instdir.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires:	perl-XML-LibXML perl-IO-Socket-SSL
%if 0%{?rhel} && 0%{?rhel} <= 6
Requires:	perl-parent perl-JSON perl-Time-HiRes
%else
Requires:	perl-JSON-PP
%endif
Requires:	perl-Digest-SHA perl-DBD-Pg perl-Time-HiRes zlib
Requires:	perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
BuildRequires:	openssl-devel zlib-devel perl-ExtUtils-Embed

%description
pgBackRest aims to be a simple, reliable backup and restore system that can
seamlessly scale up to the largest databases and workloads.

Instead of relying on traditional backup tools like tar and rsync, pgBackRest
implements all backup features internally and uses a custom protocol for
communicating with remote systems. Removing reliance on tar and rsync allows
for better solutions to database-specific backup challenges. The custom remote
protocol allows for more flexibility and limits the types of connections that
are required to perform a backup which increases security.

%prep
%setup -q -n %{sname}-release-%{version}
%patch0 -p0

%build
pushd src
./configure
%{__make}
popd

%install
pushd src
%{__install} -D -d -m 0755 %{buildroot}%{gbddir}/%{sname}
%make_install DESTDIR=%{buildroot}
popd
%{__install} -D -d -m 0755 %{buildroot}/%{gbddir}/%{sname}/etc
%{__install} %{SOURCE1} %{buildroot}/%{gbddir}/%{sname}/etc/pgbackrest.conf
%{__install} -D -d -m 0700 %{buildroot}/%{_sharedstatedir}/%{name}
%{__install} -D -d -m 0700 %{buildroot}/var/log/%{name}
%{__install} -D -d -m 0700 %{buildroot}/var/spool/%{name}
%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root)
%if 0%{?rhel} && 0%{?rhel} <= 6
%doc LICENSE
%else
%license LICENSE
%endif
%{gbddir}/%{sname}/bin/%{sname}
%config(noreplace) %attr (644,root,root) %{gbddir}/%{sname}/etc/%{sname}.conf
%attr(-,gbdsql,gbdsql) /var/log/%{name}
%attr(-,gbdsql,gbdsql) %{_sharedstatedir}/%{name}
%attr(-,gbdsql,gbdsql) /var/spool/%{name}

%changelog
* Thu May 23 2019 Devrim Gündüz <devrim@gunduzdanismanlik.com> - 2.14-1GBD
- 2.14 güncellemesi

* Sun Apr 14 2019 Devrim Gündüz <devrim@gunduzdanismanlik.com> - 2.12-1GBD
- 2.12 güncellemesi

* Fri Jan 4 2019 Devrim Gündüz <devrim@gunduzdanismanlik.com> - 2.08-1GBD
- GBDSQL için ilk paket
