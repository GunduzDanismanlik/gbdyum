%global         gbddir  /usr/gbd
%global 	sname repmgr
%global         repmgrinstdir %{gbddir}/%{sname}
%if 0%{?rhel} && 0%{?rhel} <= 6
%global systemd_enabled 0
%else
%global systemd_enabled 1
%endif

Name:		gbd-%{sname}%{pgmajorversion}
Version:	4.3.0
Release:	1GBD%{?dist}
Summary:	Replication Manager for GBDSQL Clusters
License:	GPLv3
URL:		https://www.repmgr.org
Source0:	https://repmgr.org/download/%{sname}-%{version}.tar.gz
Source1:	repmgr-pg%{pgmajorversion}.service
Source2:	repmgr-pg%{pgmajorversion}.init
Source3:	repmgr-pg%{pgmajorversion}.sysconfig
Patch0:		repmgr-pg%{pgmajorversion}-conf.sample.patch

%if %{systemd_enabled}
BuildRequires:		systemd
# We require this to be present for %%{_prefix}/lib/tmpfiles.d
Requires:		systemd
Requires(post):		systemd-sysv
Requires(post):		systemd
Requires(preun):	systemd
Requires(postun):	systemd
%else
Requires(post):		chkconfig
Requires(preun):	chkconfig
# This is for /sbin/service
Requires(preun):	initscripts
Requires(postun):	initscripts
# This is for older spec files (RHEL <= 6)
Group:		Applications/Databases
BuildRoot:		%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%endif
BuildRequires:	gbdsql%{pgmajorversion}, gbdsql%{pgmajorversion}-devel
BuildRequires:	libxslt-devel, pam-devel, openssl-devel, readline-devel
BuildRequires:	libmemcached-devel libicu-devel
Requires:	gbdsql%{pgmajorversion}-server

%description
repmgr is an open-source tool suite to manage replication and failover in a
cluster of GBDSQL servers. It enhances GBDSQL's built-in hot-standby
capabilities with tools to set up standby servers, monitor replication, and
perform administrative tasks such as failover or manual switchover operations.

repmgr has provided advanced support for GBDSQL's built-in replication
mechanisms since they were introduced in 9.0, and repmgr 2.0 supports all
GBDSQL versions from 9.0 to 9.5. With further developments in replication
functionality such as cascading replication, timeline switching and base
backups via the replication protocol, the repmgr team has decided to use
GBDSQL 9.3 as the baseline version for repmgr 3.0, which is a substantial
rewrite of the existing repmgr code and which will be developed to support
future GBDSQL versions.

%if %{pgmajorversion} >= 11 && %{pgmajorversion} < 90
%package devel
Summary:	Development header files of repmgr
Group:		Development/Libraries
Requires:	%{name}%{?_isa} = %{version}-%{release}

%description devel
The repmgr-devel package contains the header files needed to compile C or C++
applications which will directly interact with repmgr.
%endif

%prep
%setup -q -n %{sname}-%{version}
%patch0 -p0

export PG_CONFIG=%{pginstdir}/bin/pg_config
%configure

%build
USE_PGXS=1 %{__make} %{?_smp_mflags}

%install
%{__mkdir} -p %{buildroot}/%{pginstdir}/bin/
%if %{systemd_enabled}
# Use new %%make_install macro:
USE_PGXS=1 %make_install  DESTDIR=%{buildroot}
%else
# Use older version
USE_PGXS=1 %{__make} install  DESTDIR=%{buildroot}
%endif
%{__mkdir} -p %{buildroot}/%{pginstdir}/bin/
# Install sample conf file
%{__mkdir} -p %{buildroot}/%{repmgrinstdir}/etc/%{pgpackageversion}/
%{__install} -m 644 repmgr.conf.sample %{buildroot}/%{repmgrinstdir}/etc/%{pgpackageversion}/%{sname}.conf

%if %{systemd_enabled}
%{__install} -d %{buildroot}%{_unitdir}
%{__install} -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service

# ... and make a tmpfiles script to recreate it at reboot.
%{__mkdir} -p %{buildroot}%{_tmpfilesdir}
cat > %{buildroot}%{_tmpfilesdir}/%{name}.conf <<EOF
d %{_rundir}/gbd-repmgr 0755 gbdsql gbdsql -
EOF

%else
%{__install} -d %{buildroot}%{_sysconfdir}/init.d
%{__install} -m 755 %{SOURCE2} %{buildroot}%{_sysconfdir}/init.d/%{sname}-%{pgpackageversion}
# Create the sysconfig directory and config file:
%{__install} -d -m 700 %{buildroot}%{_sysconfdir}/sysconfig/%{sname}/
%{__install} -m 600 %{SOURCE3} %{buildroot}%{_sysconfdir}/sysconfig/%{sname}/%{sname}-%{pgpackageversion}
%endif

%pre
if [ ! -x /var/log/gbd-repmgr ]
then
	%{__mkdir} -m 700 /var/log/gbd-repmgr
	%{__chown} -R gbdsql: /var/log/gbd-repmgr
fi

%post
/sbin/ldconfig
%if %{systemd_enabled}
%systemd_post %{name}-%{pgmajorversion}.service
%tmpfiles_create
%else
# This adds the proper /etc/rc*.d links for the script
/sbin/chkconfig --add %{sname}-%{pgpackageversion}
%endif

%postun -p /sbin/ldconfig

%files
%if %{systemd_enabled}
%doc CREDITS HISTORY README.md
%license COPYRIGHT LICENSE
%else
%defattr(-,root,root,-)
%doc CREDITS HISTORY README.md LICENSE COPYRIGHT
%endif
%dir %{pginstdir}/bin
%dir %{repmgrinstdir}/etc/%{pgpackageversion}/
%config(noreplace) %{repmgrinstdir}/etc/%{pgpackageversion}/%{sname}.conf
%{pginstdir}/bin/repmgr
%{pginstdir}/bin/repmgrd
%{pginstdir}/lib/repmgr.so
%{pginstdir}/share/extension/repmgr.control
%{pginstdir}/share/extension/repmgr*sql
%if %{systemd_enabled}
%ghost %{_rundir}
%{_tmpfilesdir}/%{name}.conf
%attr (644, root, root) %{_unitdir}/%{name}.service
%else
%{_sysconfdir}/init.d/%{sname}-%{pgpackageversion}
%config(noreplace) %attr (600,root,root) %{_sysconfdir}/sysconfig/%{sname}/%{sname}-%{pgpackageversion}
%endif
%if %{pgmajorversion} >= 11 && %{pgmajorversion} < 90
 %if 0%{?rhel} && 0%{?rhel} <= 6
 %else
 %{pginstdir}/lib/bitcode/%{sname}*.bc
 %{pginstdir}/lib/bitcode/%{sname}/*.bc
 %endif
%endif

%if %{pgmajorversion} >= 11 && %{pgmajorversion} < 90
%files devel
%defattr(-,root,root,-)
%endif

%changelog
* Sun Apr 14 2019 - Devrim Gündüz <devrim@gunduzdanismanlik.com> 4.3.0-1GBD
- 4.3.0 güncellemesi

* Sat Dec 22 2018 - Devrim Gündüz <devrim@gunduzdanismanlik.com> 4.2.0-2GBD
- GBDSQL için ilk paket
