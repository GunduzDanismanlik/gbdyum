%global gbddir /usr/gbd/
%global gbdsname gbd-%{sname}
%global sname sqlite
%global sqlite33instdir %{gbddir}/%{sname}33

# bcond default logic is nicely backwards...
%bcond_without tcl
%bcond_with static

%define	realver	3300100
%define	docver	3300100
%define	rpmver	3.30.1

Summary:	Library that implements an embeddable SQL database engine
Name:		%{sname}33
Version:	%{rpmver}
Release:	1%{?dist}
License:	Public Domain
URL:		http://www.sqlite.org/

Source0:	http://www.sqlite.org/2019/sqlite-src-%{realver}.zip
Source1:	http://www.sqlite.org/2019/sqlite-doc-%{docver}.zip
Source2:	http://www.sqlite.org/2019/sqlite-autoconf-%{realver}.tar.gz
# Support a system-wide lemon template
Patch1:		sqlite-3.6.23-lemon-system-template.patch
# sqlite >= 3.7.10 is buggy if malloc_usable_size() is detected, disable it:
# https://bugzilla.redhat.com/show_bug.cgi?id=801981
# http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=665363
Patch2:		sqlite-3.12.2-no-malloc-usable-size.patch
# Temporary workaround for failed percentile test, see patch for details
Patch3:		sqlite-3.8.0-percentile-test.patch
# Disable test date-2.2c on i686
Patch4:		sqlite-3.16-datetest-2.2c.patch
# Modify sync2.test to pass with DIRSYNC turned off
Patch5:		sqlite-3.18.0-sync2-dirsync.patch

BuildRequires:	gcc
BuildRequires:	ncurses-devel readline-devel glibc-devel
BuildRequires:	autoconf
%if %{with tcl}
BuildRequires:	/usr/bin/tclsh
BuildRequires:	tcl-devel
%{!?tcl_version:	%global tcl_version 8.6}
%{!?tcl_sitearch:	%global tcl_sitearch %{sqlite33instdir}/lib/tcl%{tcl_version}}
%endif

Requires:		%{name}-libs = %{version}-%{release}

# Ensure updates from pre-split work on multi-lib systems
Obsoletes:		%{name} < 3.11.0-1
Conflicts:		%{name} < 3.11.0-1

%description
SQLite is a C library that implements an SQL database engine. A large
subset of SQL92 is supported. A complete database is stored in a
single disk file. The API is designed for convenience and ease of use.
Applications that link against SQLite can enjoy the power and
flexibility of an SQL database without the administrative hassles of
supporting a separate database server.  Version 2 and version 3 binaries
are named to permit each to be installed on a single host

%package devel
Summary:	Development tools for the sqlite3 embeddable SQL database engine
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	pkgconfig

%description devel
This package contains the header files and development documentation
for %{name}. If you like to develop programs using %{name}, you will need
to install %{name}-devel.

%package libs
Summary:	Shared library for the sqlite3 embeddable SQL database engine.

# Ensure updates from pre-split work on multi-lib systems
Obsoletes:	%{name} < 3.11.0-1
Conflicts:	%{name} < 3.11.0-1

%description libs
This package contains the shared library for %{name}.

%package doc
Summary:	Documentation for sqlite
BuildArch: noarch

%description doc
This package contains most of the static HTML files that comprise the
www.sqlite.org website, including all of the SQL Syntax and the
C/C++ interface specs and other miscellaneous documentation.

%package -n %{name}-lemon
Summary:	A parser generator

%description -n %{name}-lemon
Lemon is an LALR(1) parser generator for C or C++. It does the same
job as bison and yacc. But lemon is not another bison or yacc
clone. It uses a different grammar syntax which is designed to reduce
the number of coding errors. Lemon also uses a more sophisticated
parsing engine that is faster than yacc and bison and which is both
reentrant and thread-safe. Furthermore, Lemon implements features
that can be used to eliminate resource leaks, making is suitable for
use in long-running programs such as graphical user interfaces or
embedded controllers.

%if %{with tcl}
%package tcl
Summary:	Tcl module for the sqlite3 embeddable SQL database engine
Requires:	%{name} = %{version}-%{release}
Requires:	tcl(abi) = %{tcl_version}

%description tcl
This package contains the tcl modules for %{name}.

%package analyzer
Summary:	An analysis program for sqlite3 database files
Requires:	%{name} = %{version}-%{release}
Requires:	tcl(abi) = %{tcl_version}

%description analyzer
This package contains the analysis program for %{name}.
%endif

%prep
%setup -q -a1 -n sqlite-src-%{realver}
%patch1 -p1
%patch2 -p1
%patch3 -p1
%ifarch %{ix86}
%patch4 -p1
%endif
%patch5 -p1

# Remove backup-file
%{__rm} -f %{sname}-doc-%{docver}/sqlite.css~ || :

autoconf # Rerun with new autoconf to add support for aarm64

%build
export CFLAGS="$RPM_OPT_FLAGS $RPM_LD_FLAGS -DSQLITE_ENABLE_COLUMN_METADATA=1 \
		-DSQLITE_DISABLE_DIRSYNC=1 -DSQLITE_ENABLE_FTS3=3 \
		-DSQLITE_ENABLE_RTREE=1 -DSQLITE_SECURE_DELETE=1 \
		-DSQLITE_ENABLE_UNLOCK_NOTIFY=1 -DSQLITE_ENABLE_DBSTAT_VTAB=1 \
		-DSQLITE_ENABLE_FTS3_PARENTHESIS=1 -DSQLITE_ENABLE_JSON1=1 \
		-Wall -fno-strict-aliasing"
./configure %{!?with_tcl:--disable-tcl} \
	--prefix=%{sqlite33instdir} \
	--libdir=%{sqlite33instdir}/lib \
	--enable-fts5 \
	--enable-threadsafe \
	--enable-threads-override-locks \
	--enable-load-extension \
	%{?with_tcl:TCLLIBDIR=%{tcl_sitearch}/sqlite3}

# rpath removal
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

%{__make} %{?_smp_mflags}

# Build sqlite3_analyzer
# depends on tcl
%if %{with tcl}
%{__make} %{?_smp_mflags} sqlite3_analyzer
%endif

%install
%{__make} DESTDIR=${RPM_BUILD_ROOT} install

%{__install} -D -m0644 sqlite3.1 $RPM_BUILD_ROOT/%{sqlite33instdir}/man/man1/sqlite3.1
%{__install} -D -m0755 lemon $RPM_BUILD_ROOT/%{sqlite33instdir}/bin/lemon
%{__install} -D -m0644 tool/lempar.c $RPM_BUILD_ROOT/%{sqlite33instdir}/data/lemon/lempar.c

%if %{with tcl}
# fix up permissions to enable dep extraction
chmod 0755 ${RPM_BUILD_ROOT}/%{tcl_sitearch}/sqlite3/*.so
# Install sqlite3_analyzer
%{__install} -D -m0755 sqlite3_analyzer $RPM_BUILD_ROOT/%{sqlite33instdir}/bin/sqlite3_analyzer
%endif

%if ! %{with static}
%{__rm} -f $RPM_BUILD_ROOT/%{sqlite33instdir}/lib/*.{la,a}
%endif

%post libs
/usr/sbin/ldconfig

%files
%{sqlite33instdir}/bin/sqlite3
%{sqlite33instdir}/man/man?/*

%files libs
%doc README.md
%{sqlite33instdir}/lib/*.so.*

%files devel
%{sqlite33instdir}/include/*.h
%{sqlite33instdir}/lib/*.so
%{sqlite33instdir}/lib/pkgconfig/*.pc
%if %{with static}
%{sqlite33instdir}/lib/*.a
%exclude %{sqlite33instdir}/lib/*.la
%endif

%files doc
%doc %{sname}-doc-%{docver}/*

%files -n %{name}-lemon
%{sqlite33instdir}/bin/lemon
%{sqlite33instdir}/data/lemon

%if %{with tcl}
%files tcl
%{tcl_sitearch}/sqlite3

%files analyzer
%{sqlite33instdir}/bin/sqlite3_analyzer
%endif

%changelog
* Fri Nov 15 2019 Devrim Gündüz <devrim@gunduzdanismanlik.com> - 3.30-1.1
- Initial packaging for GBDSQL to fix performance issues on RHEL
  7 with new Proj and co.
