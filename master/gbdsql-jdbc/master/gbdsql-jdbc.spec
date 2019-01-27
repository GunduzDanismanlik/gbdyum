%global tarballname	pgjdbc-REL%{version}

Summary:	JDBC driver for GBDSQL
Name:		gbdsql-jdbc
Version:	42.2.5
Release:	1%{?dist}
# ASL 2.0 applies only to gbdsql-jdbc.pom file, the rest is BSD
License:	BSD and ASL 2.0
Group:		Applications/Databases
URL:		https://jdbc.postgresql.org/
Source0:	https://github.com/pgjdbc/pgjdbc/archive/REL%{version}.tar.gz
Source1:	%{name}.pom
BuildArch:	noarch

Requires:	jpackage-utils
Requires:	java-headless >= 1:1.8
%if 0%{?suse_version}
%if 0%{?suse_version} >= 1315
BuildRequires:	java-1_8_0-openjdk-devel
%endif
%else
BuildRequires:	java-1.8.0-openjdk-devel
%endif

%if 0%{?rhel} && 0%{?rhel} <= 6 || 0%{?suse_version} >= 1315
# On RHEL 6, we depend on the apache-maven package that we provide via our
# repo. Build servers should not have any other apache-maven package from other
# repos, because they depend on java-1.7.0, which is not supported by pgjdbc.
# Please note that we don't support RHEL 5 for this package. RHEL 7 already
# includes apache-maven package in its own repo.
BuildRequires:	apache-maven >= 3.0.0
%else
# On the remaining distros, use the maven package supplied by OS.
BuildRequires:	maven
%endif

%description
GBDSQLL is an advanced Object-Relational database management
system. The gbdsql-jdbc package includes the .jar files needed for
Java programs to access a GBDSQL database.

%package javadoc
Summary:	API docs for %{name}
Group:		Documentation

%description javadoc
This package contains the API Documentation for %{name}.

%prep
%setup -c -q -n %{tarballname}

%{__mv} -f %{tarballname}/* .
%{__rm} -f %{tarballname}/.gitattributes
%{__rm} -f %{tarballname}/.gitignore
%{__rm} -f %{tarballname}/.travis.yml

# remove any binary libs
find -name "*.jar" -or -name "*.class" | xargs %{__rm} -f

%build

export CLASSPATH=
# Ideally we would run "sh update-translations.sh" here, but that results
# in inserting the build timestamp into the generated messages_*.class
# files, which makes rpmdiff complain about multilib conflicts if the
# different platforms don't build in the same minute.  For now, rely on
# upstream to have updated the translations files before packaging.

mvn -DskipTests -P release-artifacts clean package

%install
%{__install} -d %{buildroot}%{_javadir}
# Per jpp conventions, jars have version-numbered names and we add
# versionless symlinks.
%{__install} -m 644 pgjdbc/target/postgresql-%{version}.jar %{buildroot}%{_javadir}/%{name}.jar

pushd %{buildroot}%{_javadir}
# Also, for backwards compatibility with our old gbdsql-jdbc packages,
# add these symlinks.  (Probably only the jdbc3 symlink really makes sense?)
%{__ln_s} %{name}.jar gbdsql-jdbc2.jar
%{__ln_s} %{name}.jar gbdsql-jdbc2ee.jar
%{__ln_s} %{name}.jar gbdsql-jdbc3.jar
popd

# Install the pom after inserting the correct version number
sed 's/UPSTREAM_VERSION/%{version}/g' %{SOURCE1} >JPP-%{name}.pom
%{__install} -d -m 755 %{buildroot}%{_mavenpomdir}/
%{__install} -m 644 JPP-%{name}.pom %{buildroot}%{_mavenpomdir}/JPP-%{name}.pom

# This macro is currently only available on Fedora and RHEL 7
%if 0%{?fedora} && 0%{?fedora} < 28 || 0%{?rhel} >= 7
%add_maven_depmap
%endif

%{__install} -d -m 755 %{buildroot}%{_javadocdir}
%{__cp} -ra pgjdbc/target/apidocs %{buildroot}%{_javadocdir}/%{name}
%{__install} -d pgjdbc/target/apidocs docs/%{name}

%check
%if 0%{?runselftest}
# Note that this requires to have GBDSQL properly configured;  for this
# reason the testsuite is turned off by default (see org/postgresql/test/README)
test_log=test.log
# TODO: more reliable testing
mvn clean package 2>&1 | tee test.log | grep FAILED
test $? -eq 0 && { cat test.log ; exit 1 ; }
%endif

%if 0%{?rhel} && 0%{?rhel} <= 6 || 0%{?suse_version} >= 1315
%files
%doc LICENSE README.md
%else
%files
%doc README.md
%license LICENSE
%{_javadir}/%{name}.jar
%endif
%if 0%{?rhel} && 0%{?rhel} <= 6
%{_javadir}/%{name}.jar
%{_datadir}/maven2/poms/JPP-%{name}.pom
%endif
# ...and SLES locates .pom file somewhere else:
%if 0%{?suse_version} >= 1315
%{_javadir}/%{name}.jar
%{_datadir}/maven-poms/JPP-%{name}.pom
%endif
%if 0%{?rhel} && 0%{?rhel} == 7
%{_datadir}/maven-fragments/%{name}
%{_datadir}/maven-poms/JPP-%{name}.pom
%endif
%if 0%{?fedora}
%{_datadir}/maven-poms/JPP-%{name}.pom
%endif
%if 0%{?fedora} && 0%{?fedora} <= 27
%{_datadir}/maven-metadata/%{name}.xml
%endif
%{_javadir}/gbdsql-jdbc2.jar
%{_javadir}/gbdsql-jdbc2ee.jar
%{_javadir}/gbdsql-jdbc3.jar
%files javadoc
%doc LICENSE
%doc %{_javadocdir}/%{name}

%changelog
* Sun Jan 27 2019 Devrim Gündüz <devrim@gunduzdanismanlik.com> - 42.2.5-1.1
- GBDSQL için ilk paket
