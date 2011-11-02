%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name: cas
Summary: Tool to analyze and configure core file environment
Version: 1.0
Release: 0%{?dist}
Source0: https://fedorahosted.org/releases/c/a/cas/%{name}-%{version}.tar.gz
License: GPLv3+
Group: Applications/System
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch: noarch
Url: http://fedorahosted.org/cas
BuildRequires: python-devel
%if 0%{?rhel} <= 5
Requires: python-sqlite
%endif
Requires: python-paramiko
Requires: xz
Requires: crash
Requires: python-urlgrabber
Requires: python-sqlalchemy

%description
CAS provides a user the ability to configure an environment for core analysis
quickly. All the hassles of matching kernel versions and machine architecture
types to core dumps are automatically detected and processed.

%package admin
Summary: Administrative frontend to CAS
Group: Applications/System
Requires: cas = %{version}-%{release}

%description admin
Administrative frontend to CAS database. Provides the ability to update
the database instance with newly added kernel debug information and timestamps.

%package server
Summary: Web frontend to CAS
Group: Applications/System
Requires: cas = %{version}-%{release}
Requires: cas-admin = %{version}-%{release}
Requires: python-cherrypy
Requires: python-simplejson
Requires: python-mako

%description server
Provides web frontend to CAS to allow for a much simpler user experience when
dealing with vmcores.

%prep
%setup -q

%build
make

%install
rm -rf ${RPM_BUILD_ROOT}
make DESTDIR=${RPM_BUILD_ROOT} install
for i in `find ${RPM_BUILD_ROOT} -iname Makefile`; do rm $i; done

%clean
rm -rf ${RPM_BUILD_ROOT}

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/cas.conf
%{_bindir}/cas
%{python_sitelib}/*
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_datadir}/%{name}
%dir %{_var}/lib/cas/snippets/
%config(noreplace) %{_var}/lib/cas/snippets/*
%doc AUTHORS LICENSE README PKG-INFO doc/*

%files admin
%defattr(-,root,root,-)
%{_bindir}/cas-admin

%files server
%defattr(-,root,root,-)
%{_datadir}/%{name}/overseer
%{_bindir}/cas-server

%changelog
* Tue May 20 2010 Adam Stokes <ajs at redhat dot com> - 1.0
- Create 1.0 release

* Mon May 3 2010 Adam Stokes <ajs at redhat dot com> - 0.18
- Split packages into admin/user
- Rewrote database interface using sqlalchemy
- Reworked cas-admin to interface with new database format

* Mon Apr 26 2010 Adam Stokes <ajs at redhat dot com> - 0.17
- Add cas.conf man page
- Fix typo in 'smtphost' configuration parameter

* Fri Apr 16 2010 Adam Stokes <ajs at redhat dot com> - 0.16
- Release bump
- Fix inconsistencies with compression/core analysis
- Installer updates

* Wed Feb 17 2010 Adam Stokes <ajs at redhat dot com> - 0.15-5
- file structure rework

* Wed Dec 9 2009 Adam Stokes <ajs at redhat dot com> - 0.15-4
- Test for pbzip2 for utilizing multiple cores during decompression
- Increment python requirement to 2.4
- provide shutil, subprocess from 2.6 if on lower python version
- added helper function for compressing core files in proper format
- tagged stable 0.15

* Thu Oct 15 2009 Adam Stokes <ajs at redhat dot com> - 0.15-1
- Require paramiko for all remote executions
- Rip out func code
- Documentation update to include ssh setup

* Tue May 5 2009 Adam Stokes <ajs at redhat dot com> - 0.14-8
- support for purging old data
- documentation updated to reflect updated workflow and describe
  new features.

* Fri Apr 24 2009 Adam Stokes <ajs at redhat dot com> - 0.14-2
- Finalizing sqlite implementation
- added AUTHORS

* Thu Apr 2 2009 Scott Dodson <sdodson at sdodson dot com > - 0.14-1
- Spec file changes to handle the snippets directory
- Snippets support to replace hardcoding crash input cmds

* Wed Feb 11 2009 Adam Stokes <ajs at redhat dot com> - 0.13-120
- added proper documentation

* Wed Jan 7 2009 Adam Stokes <ajs at redhat dot com> - 0.13-116
- support for extracting kernel modules
- support for analyzing x86 cores on x86_64 system
- consistent macro usage in spec

* Mon Dec 29 2008 Adam Stokes <ajs at redhat dot com> - 0.13-114
- changed license to gplv3 or later
- removed source requirements as these are handled by python manifest
- removed python requirement
- updated description

* Fri Dec 19 2008 Adam Stokes <ajs at redhat dot com> - 0.13-113
- rpmlint verified
- manually set version/release in spec
- license tag fix
- added full path to upstream source release

* Mon Dec 15 2008 Adam Stokes <ajs at redhat dot com> - 0.13-94
- no replace on config file
- cas now processes locally and remotely via func

* Wed Aug 20 2008 Adam Stokes <ajs at redhat dot com> - 0.13
- Updated build and spec

* Mon Feb 10 2008 Scott Dodson <sdodson at redhat dot com> - 0.11
- Minor changes to permissions

* Mon Dec 10 2007 Adam Stokes <astokes at redhat dot com> - 0.9.1
- splitting off grabcore to be a download/extract only service
- core of the work to be done specifically by their intended
  modules

* Fri Dec 7 2007 Adam Stokes <astokes at redhat dot com> - 0.9
- release bump
- decompression module added

* Tue Nov 13 2007 Adam Stokes <astokes at redhat dot com> - 0.8
- threading added
- better exception handling
- bug fixes
- added initscripts, service capabilities

* Mon Oct 22 2007 Adam Stokes <astokes at redhat dot com> - 0.1
- initial build
