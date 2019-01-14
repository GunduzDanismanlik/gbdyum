%global gbddir /usr/gbd
%global sname	pgagent

%if 0%{?rhel} && 0%{?rhel} <= 6
%global systemd_enabled 0
%else
%global systemd_enabled 1
%endif

%ifarch ppc64 ppc64le
# Define the AT version and path.
%global atstring	at10.0
%global atpath		/opt/%{atstring}
%endif

Summary:	Job scheduler for PostgreSQL
Name:		gbd-%{sname}_%{pgmajorversion}
Version:	4.0.0
Release:	2%{?dist}
License:	PostgreSQL
Source0:	https://download.postgresql.org/pub/pgadmin/%{sname}/pgAgent-%{version}-Source.tar.gz
Source2:	gbd-%{sname}-%{pgmajorversion}.service
Source4:	gbd-%{sname}-%{pgmajorversion}.logrotate
Source5:	gbd-%{sname}-%{pgmajorversion}.conf
URL:		http://www.pgadmin.org/
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:	gbdsql%{pgmajorversion}-devel
%if 0%{?rhel} && 0%{?rhel} == 7
BuildRequires:	cmake3
%else
BuildRequires:	cmake => 2.8.8
%endif

%if %{systemd_enabled}
BuildRequires:		systemd, systemd-devel
Requires:		systemd
%if 0%{?suse_version}
%if 0%{?suse_version} >= 1315
Requires(post):		systemd-sysvinit
%endif
%else
Requires(post):		systemd-sysv
Requires(post):		systemd
Requires(preun):	systemd
Requires(postun):	systemd
%endif
%else
Requires(post):		chkconfig
Requires(preun):	chkconfig
# This is for /sbin/service
Requires(preun):	initscripts
Requires(postun):	initscripts
%endif

%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

%description
pgAgent is a job scheduler for GBDQL which may be managed
using pgAdmin.

%pre
if [ $1 -eq 1 ] ; then
groupadd -r gbdpgagent >/dev/null 2>&1 || :
useradd -g gbdpgagent -r -s /bin/false \
	-c "pgAgent Job Scheduler for GBDSQL" gbdpgagent >/dev/null 2>&1 || :
touch /var/log/gbd-pgagent_%{pgmajorversion}.log
fi
%{__chown} gbdpgagent:gbdpgagent /var/log/gbd-pgagent_%{pgmajorversion}.log
%{__chmod} 0700 /var/log/gbd-pgagent_%{pgmajorversion}.log

%prep
%setup -q -n pgAgent-%{version}-Source

%build
%ifarch ppc64 ppc64le
	CFLAGS="-O3 -mcpu=$PPC_MCPU -mtune=$PPC_MTUNE"
	CC=%{atpath}/bin/gcc; export CC
%else
	CFLAGS="$RPM_OPT_FLAGS -fPIC -pie"
	CXXFLAGS="$RPM_OPT_FLAGS -fPIC -pie -pthread"
	export CFLAGS
	export CXXFLAGS
%endif
%if 0%{?rhel} && 0%{?rhel} == 7
cmake3 .. \
%else
%cmake .. \
%endif
	-D CMAKE_INSTALL_PREFIX:PATH=/usr \
	-D PG_CONFIG_PATH:FILEPATH=/%{pginstdir}/bin/pg_config \
	-D STATIC_BUILD:BOOL=OFF .

%install
%{__rm} -rf %{buildroot}
%{__make} DESTDIR=%{buildroot} install

# Rename gbd-pgagent binary, so that we can have parallel installations:
%{__mv} -f %{buildroot}%{_bindir}/%{sname} %{buildroot}%{_bindir}/%{name}
# Remove some cruft, and also install doc related files to appropriate directory:
%{__mkdir} -p %{buildroot}%{_datadir}/%{name}-%{version}
%{__rm} -f %{buildroot}/usr/LICENSE
%{__rm} -f %{buildroot}/usr/README
%{__mv} -f %{buildroot}%{_datadir}/pgagent*.sql %{buildroot}%{_datadir}/%{name}-%{version}/

%if %{systemd_enabled}
# Install unit file
%{__install} -d %{buildroot}%{_unitdir}
%{__install} -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.service
# Install conf file
%{__install} -p -d %{buildroot}%{gbddir}/%{sname}/etc/
%{__install} -p -m 644 %{SOURCE5} %{buildroot}%{gbddir}/%{sname}/etc/%{name}.conf
# ... and make a tmpfiles script to recreate it at reboot.
%{__mkdir} -p %{buildroot}%{_tmpfilesdir}
cat > %{buildroot}%{_tmpfilesdir}/%{name}.conf <<EOF
d %{_rundir} 0755 root root -
EOF
%else
# install init script
# Not supported by GBD (yet)
%{__install} -d %{buildroot}%{_initrddir}
%{__install} -m 755 %{SOURCE3} %{buildroot}/%{_initrddir}/%{name}
%endif

# Install logrotate file:
%{__install} -p -d %{buildroot}%{_sysconfdir}/logrotate.d
%{__install} -p -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

%post
if [ $1 -eq 1 ] ; then
%if %{systemd_enabled}
%systemd_post %{name}.service
%tmpfiles_create
    # Initial installation
%else
# Not supported by GBD (yet)
chkconfig --add %{name}
%endif
fi

%preun
%if %{systemd_enabled}
if [ $1 -eq 0 ] ; then
	# Package removal, not upgrade
	/bin/systemctl --no-reload disable %{name}.service >/dev/null 2>&1 || :
	/bin/systemctl stop %{name}.service >/dev/null 2>&1 || :
fi
%else
	# Not supported by GBD (yet)
	chkconfig --del %{name}
%endif

%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
	# Package upgrade, not uninstall
	/bin/systemctl try-restart %{name}.service >/dev/null 2>&1 || :
fi

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-, root, root)
%if %{systemd_enabled}
%doc README
%license LICENSE
%else
%doc README LICENSE
%endif
%{_bindir}/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_datadir}/%{name}-%{version}/%{sname}*.sql
%if %{systemd_enabled}
%ghost %{_rundir}
%{_tmpfilesdir}/%{name}.conf
%{_unitdir}/%{name}.service
%dir %{gbddir}/%{sname}/etc/
%config(noreplace) %{buildroot}%{gbddir}/%{sname}/etc/%{name}.conf
%else
%{_initrddir}/%{name}
%endif
%{pginstdir}/share/extension/%{sname}--*.sql
%{pginstdir}/share/extension/%{sname}--unpackaged--*.sql
%{pginstdir}/share/extension/%{sname}.control

%changelog
* Fri Jan 4 2019 Devrim Gündüz <devrim@gunduz.org> - 4.0.0-2
- GBDSQL için ilk paket
