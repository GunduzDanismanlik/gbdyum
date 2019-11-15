%global sname	pgbadger
%global gbddir	/usr/gbd

Summary:	A fast GBDSQL log analyzer
Name:		gbd-%{sname}
Version:	11.1
Release:	1GBD%{?dist}
Group:		Applications/Databases
License:	PostgreSQL
Source0:	https://github.com/darold/%{sname}/archive/v%{version}.tar.gz
URL:		https://github.com/darold
BuildArch:	noarch
Requires:	perl-Text-CSV_XS

%description
pgBadger is a GBDSQL log analyzer build for speed with fully
detailed reports from your GBDSQL log file. It's a single and small
Perl script that aims to replace and outperform the old php script
pgFouine.

pgBadger is written in pure Perl language. It uses a javascript library
to draw graphs so that you don't need additional Perl modules or any
other package to install. Furthermore, this library gives us more
features such as zooming.

pgBadger is able to autodetect your log file format (syslog, stderr or
csvlog). It is designed to parse huge log files as well as gzip
compressed file.

%prep
%setup -q -n %{sname}-%{version}

%build
%{__perl} Makefile.PL INSTALLDIRS=vendor

%install
%{__rm} -rf %{buildroot}
%{__make} pure_install PERL_INSTALL_ROOT=%{buildroot}
# Remove .packlist file (per rpmlint)
%{__rm} -f %{buildroot}/%perl_vendorarch/auto/pgBadger/.packlist
# GBD dizinleri:
%{__mkdir} -p %{buildroot}%{gbddir}/%{sname}/bin
%{__mkdir} -p %{buildroot}%{gbddir}/%{sname}/man/man1/
%{__mv} %{buildroot}/%{_bindir}/%{sname}  %{buildroot}%{gbddir}/%{sname}/bin/%{name}
%{__mv} %{buildroot}/%{_mandir}/man1/%{sname}* %{buildroot}%{gbddir}/%{sname}/man/man1/%{name}

%files
%if 0%{?rhel} && 0%{?rhel} <= 6
%doc README LICENSE
%else
%doc README
%license LICENSE
%endif
%dir %{gbddir}/%{sname}/bin
%dir %{gbddir}/%{sname}/man/man1/
%attr(755,root,root) %{gbddir}/%{sname}/bin/%{name}
%{gbddir}/%{sname}/man/man1/%{name}

%changelog
* Fri Nov 15 2019 - Devrim Gündüz <devrim@gunduzdanismanlik.com> - 11.1GBD
- 11.1 güncellemesi

* Sun Apr 14 2019 - Devrim Gündüz <devrim@gunduzdanismanlik.com> - 10.3GBD
- 10.3 güncellemesi

* Wed Jan 2 2019 - Devrim Gündüz <devrim@gunduzdanismanlik.com> - 10.2GBD
- GBDSSQL için ilk paket
