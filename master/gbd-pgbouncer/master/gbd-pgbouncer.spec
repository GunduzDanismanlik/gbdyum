%global gbddir /usr/gbd/
%global sname pgbouncer
%if 0%{?rhel} && 0%{?rhel} <= 6
%global systemd_enabled 0
%else
%global systemd_enabled 1
%endif

%if 0%{?suse_version}
%if 0%{?suse_version} >= 1315
%global systemd_enabled 1
%endif
%endif

%ifarch ppc64 ppc64le
# Define the AT version and path.
%global atstring	at10.0
%global atpath		/opt/%{atstring}
%endif

%global _varrundir %{_localstatedir}/run/%{name}

Name:		gbd-%{sname}
Version:	1.9.0
Release:	1%{?dist}.1
Summary:	Lightweight connection pooler for PostgreSQL
License:	MIT and BSD
URL:		https://%{sname}.github.io/
Source0:	https://%{sname}.github.io/downloads/files/%{version}/%{sname}-%{version}.tar.gz
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.logrotate
Source4:	%{name}.service
Patch0:		%{name}-ini.patch
%if 0%{?suse_version}
%if 0%{?suse_version} >= 1315
BuildRequires:	libcares-devel libevent-devel
Requires:	libevent-devel
%else
BuildRequires:	c-ares-devel
%endif
%endif
%if 0%{?rhel} && 0%{?rhel} <= 6
BuildRequires:	libevent2-devel >= 2.0
Requires:	libevent2 >= 2.0
%else
BuildRequires:	libevent-devel >= 2.0
Requires:	libevent >= 2.0
%endif
BuildRequires:	openssl-devel pam-devel
Requires:	c-ares pam python-psycopg2
Requires:	initscripts

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
# This is for older releases:
Group:		Applications/Databases
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%endif
Requires:	/usr/sbin/useradd

%ifarch ppc64 ppc64le
AutoReq:	0
Requires:	advance-toolchain-%{atstring}-runtime
%endif

%ifarch ppc64 ppc64le
BuildRequires:	advance-toolchain-%{atstring}-devel
%endif

%description
gbd-pgbouncer is a lightweight connection pooler for GBDSQL.
gbd-pgbouncer uses libevent for low-level socket handling.

%prep
%setup -q -n %{sname}-%{version}
%patch0 -p0

%build
sed -i.fedora \
 -e 's|-fomit-frame-pointer||' \
 -e '/BININSTALL/s|-s||' \
 configure

%ifarch ppc64 ppc64le
	CFLAGS="${CFLAGS} $(echo %{__global_cflags} | sed 's/-O2/-O3/g') -m64 -mcpu=power8 -mtune=power8 -I%{atpath}/include"
	CXXFLAGS="${CXXFLAGS} $(echo %{__global_cflags} | sed 's/-O2/-O3/g') -m64 -mcpu=power8 -mtune=power8 -I%{atpath}/include"
	LDFLAGS="-L%{atpath}/%{_lib}"
	CC=%{atpath}/bin/gcc; export CC
%endif

./configure -prefix=%{gbddir}%{sname}/ --disable-evdns --with-pam

%{__make} %{?_smp_mflags} V=1

%install
%{__rm} -rf %{buildroot}
%{__make} install DESTDIR=%{buildroot}
# Install sysconfig file
%{__install} -p -d %{buildroot}%{gbddir}%{sname}
%{__install} -p -d %{buildroot}%{gbddir}%{sname}/etc
%{__install} -p -d %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -p -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/%{name}
%{__install} -p -m 644 etc/%{sname}.ini %{buildroot}%{gbddir}%{sname}/etc
%{__install} -p -m 700 etc/mkauth.py %{buildroot}%{gbddir}%{sname}/etc

%if %{systemd_enabled}
%{__install} -d %{buildroot}%{_unitdir}
%{__install} -m 644 %{SOURCE4} %{buildroot}%{_unitdir}/%{name}.service

# ... and make a tmpfiles script to recreate it at reboot.
%{__mkdir} -p %{buildroot}%{_tmpfilesdir}
cat > %{buildroot}%{_tmpfilesdir}/%{name}.conf <<EOF
d %{_varrundir} 0700 gbdpgbouncer gbdpgbouncer -
EOF

%else
%{__install} -p -d %{buildroot}%{_initrddir}
%{__install} -p -m 755 %{SOURCE1} %{buildroot}%{_initrddir}/%{name}
%endif

# Install logrotate file:
%{__install} -p -d %{buildroot}%{_sysconfdir}/logrotate.d
%{__install} -p -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# It seems we need to do this manually on SuSE:
%if 0%{?suse_version}
%{__mkdir} -p %{buildroot}%{_defaultdocdir}
%{__mv} %{buildroot}/usr/share/doc/%{name} %{buildroot}%{_defaultdocdir}/
%endif

%post
%if %{systemd_enabled}
%systemd_post %{name}.service
%tmpfiles_create
%else
# This adds the proper /etc/rc*.d links for the script
/sbin/chkconfig --add %{name}
%endif
if [ ! -d %{_localstatedir}/log/gbd-pgbouncer ] ; then
%{__mkdir} -m 700 %{_localstatedir}/log/gbd-pgbouncer
fi
%{__chown} -R gbdpgbouncer:gbdpgbouncer %{_localstatedir}/log/gbd-pgbouncer
%{__chown} -R gbdpgbouncer:gbdpgbouncer %{_varrundir} >/dev/null 2>&1 || :

%pre
groupadd -r gbdpgbouncer >/dev/null 2>&1 || :
useradd -m -g gbdpgbouncer -r -s /bin/bash \
	-c "GBDSQL PgBouncer Server" gbdpgbouncer >/dev/null 2>&1 || :

%preun
%if %{systemd_enabled}
%systemd_preun %{name}.service
%else
if [ $1 -eq 0 ] ; then
	/sbin/service gbd-pgbouncer condstop >/dev/null 2>&1
	chkconfig --del gbd-pgbouncer
fi
%endif

%postun
if [ $1 -eq 0 ]; then
%{__rm} -rf %{_varrundir}
fi
%if %{systemd_enabled}
%systemd_postun_with_restart %{name}.service
%else
if [ $1 -ge 1 ] ; then
	/sbin/service gbd-pgbouncer condrestart >/dev/null 2>&1 || :
fi
%endif

%clean
%{__rm} -rf %{buildroot}

%files
%doc %{gbddir}/%{sname}/share/doc/pgbouncer/NEWS.rst
%doc %{gbddir}/%{sname}/share/doc/pgbouncer/README.rst
%doc %{gbddir}/%{sname}/share/doc/pgbouncer/pgbouncer.ini
%doc %{gbddir}/%{sname}/share/doc/pgbouncer/userlist.txt

%if %{systemd_enabled}
%license COPYRIGHT
%endif
%dir %{gbddir}/%{sname}
%{gbddir}/%{sname}/bin/pgbouncer
#%{_bindir}/%{name}
#%config(noreplace) %{_sysconfdir}/%{name}/%{name}.ini
%if %{systemd_enabled}
%ghost %{_varrundir}
%{_tmpfilesdir}/%{name}.conf
%attr(644,root,root) %{_unitdir}/%{name}.service
%else
%{_initrddir}/%{name}
%endif
%config(noreplace) %{_sysconfdir}/logrotate.d/gbd-pgbouncer
%config(noreplace)%{_sysconfdir}/sysconfig/gbd-pgbouncer
%{gbddir}/%{sname}/etc/mkauth.py*
%{gbddir}/%{sname}/etc/pgbouncer.ini
%{gbddir}/%{sname}/share/man/man*/pgbouncer.*

%changelog
* Mon Oct 15 2018 Devrim Gündüz <devrim@gunduz.org> - 1.9.0-1.1
- GBDSQL için ilk paketleme
