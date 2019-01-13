Name:		gbd-centos11
Version:	11
Release:	2
Summary:	GBDSQL 11.X CentOS Depo Yapılandırması
Group:		System Environment/Base
License:	PostgreSQL
URL:		https://yum.gbdsql.org
Source0:	https://yum.gbdsql.org/RPM-GPG-KEY-GBD-11
Source2:	gbd-11-centos.repo
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:	noarch
Requires:	centos-release

%description
This package contains yum configuration for CentOS, and also the GPG
key for GBD RPMs.

%prep
%setup -q  -c -T

%build

%install
%{__rm} -rf %{buildroot}

%{__install} -Dpm 644 %{SOURCE0} \
	%{buildroot}%{_sysconfdir}/pki/rpm-gpg/RPM-GPG-KEY-GBD-11

%{__install} -dm 755 %{buildroot}%{_sysconfdir}/yum.repos.d
%{__install} -pm 644 %{SOURCE2}  \
	%{buildroot}%{_sysconfdir}/yum.repos.d/

%clean
%{__rm} -rf %{buildroot}

%post
/bin/rpm --import %{_sysconfdir}/pki/rpm-gpg/RPM-GPG-KEY-GBD-11

%files
%defattr(-,root,root,-)
%config %{_sysconfdir}/yum.repos.d/*
%dir %{_sysconfdir}/pki/rpm-gpg
%{_sysconfdir}/pki/rpm-gpg/*

%changelog
* Sun Jan 13 2019 Devrim Gündüz <devrim@gunduzdanismanlik.com> - 11-2
- GBDSQL depo paketi
