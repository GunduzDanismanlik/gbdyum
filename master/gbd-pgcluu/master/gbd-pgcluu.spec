%global sname	pgcluu
%global gbddir	/usr/gbd

%if 0%{?rhel} && 0%{?rhel} <= 6
%global systemd_enabled 0
%else
%global systemd_enabled 1
%endif

Summary:	PostgreSQL performance monitoring and auditing tool
Name:		gbd-%{sname}
Version:	3.1
Release:	1GBD%{?dist}
License:	BSD
Group:		Applications/Databases
Source0:	https://github.com/darold/%{sname}/archive/v%{version}.tar.gz
Patch0:		%{name}-systemd-rpm-paths.patch
URL:		http://%{sname}.darold.net/
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:	noarch

%description
pgCluu is a PostgreSQL performances monitoring and auditing tool.
View reports of all statistics collected from your PostgreSQL
databases cluster. pgCluu will show you the entire information
of the PostgreSQL cluster and the system utilization

%prep
%setup -q -n %{sname}-%{version}
%patch0 -p0

%build
%{__perl} Makefile.PL INSTALLDIRS=vendor
%{__make} %{?_smp_mflags}

%install
%{__rm} -rf %{buildroot}
%{__make} pure_install PERL_INSTALL_ROOT=%{buildroot}
%{__mkdir} -p %{buildroot}%{gbddir}/%{sname}/bin/
%{__mkdir} -p %{buildroot}%{gbddir}/%{sname}/share/man/man1/
%{__mv} %{buildroot}%{_bindir}/pgcluu %{buildroot}%{gbddir}/%{sname}/bin/pgcluu
%{__mv} %{buildroot}%{_bindir}/pgcluu_collectd %{buildroot}%{gbddir}/%{sname}/bin/pgcluu_collectd
%{__mv} %{buildroot}%{_datadir}/man/man1/pgcluu* %{buildroot}%{gbddir}/%{sname}/share/man/man1/

%if %{systemd_enabled}
%{__install} -d %{buildroot}%{_unitdir}
%{__install} -m 644 %{sname}_collectd.service %{buildroot}%{_unitdir}/%{name}_collectd.service
%{__install} -m 644 %{sname}.timer %{buildroot}%{_unitdir}/%{name}.timer
%{__install} -m 644 %{sname}.service %{buildroot}%{_unitdir}/%{name}.service
%endif

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc ChangeLog
%attr(755,root,root) %{gbddir}/%{sname}/bin/pgcluu
%attr(755,root,root) %{gbddir}/%{sname}/bin/pgcluu_collectd
%perl_vendorarch/auto/pgCluu/.packlist
%{gbddir}/%{sname}/share/man/man1/%{sname}.1
%if %{systemd_enabled}
%{_unitdir}/%{name}_collectd.service
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}.timer
%endif

%changelog
* Fri Nov 15 2019 Devrim Gündüz <devrim@gunduzdanismanlik.com> - 3.1-1GBD
- 3.1 güncellemesi

* Wed Jan 2 2019 Devrim Gündüz <devrim@gunduzdanismanlik.com> - 2.9-1GBD
- GBDSQL için ilk paket
