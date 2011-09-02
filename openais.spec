# define alphatag 0

Name: openais
Summary: The openais Standards-Based Cluster Framework executive and APIs
Version: 1.1.1
Release: 6%{?alphatag:.%{alphatag}}%{?dist}
License: BSD
Group: System Environment/Base
URL: http://openais.org
Source0: http://devresources.linuxfoundation.org/dev/openais/downloads/%{name}-%{version}/%{name}-%{version}.tar.gz
Patch0: revision-2104.patch
Patch1: revision-2105.patch
Patch2: revision-2106.patch
Patch3: revision-2107.patch
Patch4: revision-2108.patch
Patch5: revision-2109.patch
Patch6: revision-2111.patch
Patch7: revision-2137.patch
Patch8: revision-2155.patch

ExclusiveArch: i686 x86_64

# Runtime bits
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
Requires: corosync >= 1.0.0-1
Requires: openaislib = %{version}-%{release}
Conflicts: openais-devel <= 0.89

# Setup/build bits
BuildRequires: corosynclib-devel >= 1.0.0-1

%define buildtrunk 0
%{?_with_buildtrunk: %define buildtrunk 1}

%if %{buildtrunk}
BuildRequires: autoconf automake
%endif

BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

%prep
%setup -q -n %{name}-%{version}
%patch0
%patch1
%patch2
%patch3
%patch4
%patch5
%patch6
%patch7
%patch8

%if %{buildtrunk}
./autogen.sh
%endif

%{configure}

%build
make %{_smp_mflags}

%install
rm -rf %{buildroot}

make install DESTDIR=%{buildroot}
mkdir -p %{buildroot}%{_initrddir}
install -m 755 init/redhat %{buildroot}%{_initrddir}/openais

## tree fixup
# drop static libs
rm -f %{buildroot}%{_libdir}/*.a
# drop docs and html docs for now
rm -rf %{buildroot}%{_docdir}/*

%clean
rm -rf %{buildroot}

%description
This package contains the openais service handlers, default configuration
files and init script.

%post
/sbin/chkconfig --add openais || :

%preun
if [ $1 -eq 0 ]; then
    %{_initrddir}/openais stop &>/dev/null || :
    /sbin/chkconfig --del openais || :
fi

%postun
[ "$1" -ge "1" ] && %{_initrddir}/openais condrestart &>/dev/null || :

%files
%defattr(-,root,root,-)
%doc LICENSE README.amf
%dir %{_sysconfdir}/corosync
%config(noreplace) %{_sysconfdir}/corosync/amf.conf.example
%{_initrddir}/openais
%dir %{_libexecdir}/lcrso
%{_libexecdir}/lcrso/openaisserviceenable.lcrso
%{_libexecdir}/lcrso/service_amf.lcrso
%{_libexecdir}/lcrso/service_ckpt.lcrso
%{_libexecdir}/lcrso/service_clm.lcrso
%{_libexecdir}/lcrso/service_evt.lcrso
%{_libexecdir}/lcrso/service_lck.lcrso
%{_libexecdir}/lcrso/service_msg.lcrso
%{_libexecdir}/lcrso/service_tmr.lcrso
%{_mandir}/man8/openais_overview.8*
%{_mandir}/man5/openais.conf.5*
%{_mandir}/man5/amf.conf.5*
%{_sbindir}/aisexec
%{_sbindir}/openais-instantiate

%package -n openaislib
Summary: The openais Standards-Based Cluster Framework libraries
Group: System Environment/Libraries
Requires: %{name} = %{version}-%{release}

%description -n openaislib
This package contains openais libraries.

%files -n openaislib
%defattr(-,root,root,-)
%doc LICENSE
%{_libdir}/libSaAmf.so.*
%{_libdir}/libSaCkpt.so.*
%{_libdir}/libSaClm.so.*
%{_libdir}/libSaEvt.so.*
%{_libdir}/libSaLck.so.*
%{_libdir}/libSaMsg.so.*
%{_libdir}/libSaTmr.so.*

%post -n openaislib -p /sbin/ldconfig

%postun -n openaislib -p /sbin/ldconfig

%package -n openaislib-devel
Summary: The openais Standards-Based Cluster Framework libraries
Group: Development/Libraries
Requires: openaislib = %{version}-%{release}
Requires: pkgconfig
Provides: openais-devel = %{version}
Obsoletes: openais-devel < 0.91-6

%description -n openaislib-devel
This package contains the include files used to develop using openais APIs.

%files -n openaislib-devel
%defattr(-,root,root,-)
%doc LICENSE
%dir %{_includedir}/openais/
%{_includedir}/openais/saAis.h
%{_includedir}/openais/saAmf.h
%{_includedir}/openais/saCkpt.h
%{_includedir}/openais/saClm.h
%{_includedir}/openais/saEvt.h
%{_includedir}/openais/saLck.h
%{_includedir}/openais/saMsg.h
%{_includedir}/openais/saTmr.h
%{_libdir}/libSaAmf.so
%{_libdir}/libSaCkpt.so
%{_libdir}/libSaClm.so
%{_libdir}/libSaEvt.so
%{_libdir}/libSaLck.so
%{_libdir}/libSaMsg.so
%{_libdir}/libSaTmr.so
%{_libdir}/pkgconfig/*.pc

%changelog
* Mon Aug 23 2010 Ryan O'Hara <rohara@redhat.com> - 1.1.1-6
- OpenAIS checkpoint service should handle unterminated strings.
  Resolves: rhbz#625601

* Thu May 20 2010 Ryan O'Hara <rohara@redhat.com> - 1.1.1-5
- Print checkpoint section information only if debug is enabled.
  Resolves: rhbz#578935

* Wed May 12 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.1.1-4
- Do not build on ppc and ppc64.
  Resolves: rhbz#590990

* Thu Feb 25 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.1.1-3
- Resolves: rhbz#567998
- Do not build openais on s390 and s390x.

* Thu Jan 21 2010 Ryan O'Hara <rohara@redhat.com> - 1.1.1-2
- Resolves: rhbz#555164
- Resolves: rhbz#557275
- Resolves: rhbz#557622
- Add upstream revision 2104 - Fix saCkptDispatch such that it will break out of switch if callback is received and is undefined.
- Add upstream revision 2105 - Fix saTmrDispatch such that it will break out of switch if callback is received and is undefined.
- Add upstream revision 2106 - Fix saLckDispatch such that it will break out of switch if callback is received and is undefined.
- Add upstream revision 2107 - Fix saClmDispatch such that it will break out of switch if callback is received and is undefined.
- Add upstream revision 2108 - Fix saMsgDispatch such that it will break out of switch if callback is received and is undefined.
- Add upstream revision 2109 - Prevents iteration of a checkpoint section during synchronization.
- Add upstream revision 2111 - Update to openais.spec.in to fix URL and File location.

* Fri Dec  4 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.1.1-1
- New upstream release.
- spec file updates:
  * Cleanup macro usage
  * Drop Conflict: in favour of correct Requires:
  * Whitespace cleanup

* Fri Sep 25 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.1.0-1
- New upstream release.

* Tue Sep 22 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.0.2-1
- New upstream release.
- spec file updates:
  * use proper configure macro

* Thu Aug 27 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.0.1-1
- New upstream release. Fixes 2 minor issues in SA CheckPoint service.

* Tue Jul 28 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.0.0-3
- spec file updates:
  * consistent use of macros across the board

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jul  8 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.0.0-1
- New upstream release

* Thu Jul  2 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.100-1
- New upstream release

* Sat Jun 20 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.97-1
- New upstream release
- spec file updates:
  * Drop openais-trunk patch and alpha tag.
  * Fix alphatag vs buildtrunk handling.
  * New config file locations from upstream: /etc/corosync/.
  * Fix configure invokation.
  * Requires and BuildRequires corosync 0.98

* Wed Jun 10 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.96-1.svn1951
- New upstream release
- spec file updates:
  * Update to svn version 1951.
  * Define buildtrunk if we are using svn snapshots
  * Bump Requires and BuildRequires to corosync 0.97-1.svn2226
  * Force autogen invokation if buildtrunk is defined
  * Whitespace cleanup
  * Respect _smp_mflags and update configure invokation
  * Update tree cleanup section
  * Stop shipping openais.conf and amf.conf in favour of generic examples
  * libraries have moved to libdir. Drop ld.so.conf.d openais file

* Tue Mar 24 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.94-1
- New upstream release
- spec file updates:
  * Drop alpha tag
  * Drop local patches (no longer required)
  * Remove install section for docs and use proper doc macro instead
  * Add LICENSE file to all subpackages
  * Bump Requires and BuildRequires to corosync 0.95-1
  * openaislib-devel now Requires pkgconfig
  * Update BuildRoot usage to preferred versions/names

* Mon Mar  9 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.93-2.svn1741
- Import fixes from upstream:
  * Updates for new totem interface (1737, 1738, 1739, 1741).
  * Fix ipc connection (1740).

* Tue Mar  3 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.93-1
- New upstream release.
- Bump Requires and BuildRequires to corosync 0.94-1.

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.92-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 23 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.92-2
- Rename SaTmr patch to match svn commit (r1717).

* Thu Feb 19 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.92-1
- New upstream release.
- Drop alphatag from spec file.
- Drop trunk patch.
- Update Provides for corosynclib-devel.
- Update BuildRequires and Requires for new corosync.
- Add libSaTmr to packaging.
- Backport pkgconfig support for libSaTmr from trunk.

* Mon Feb  2 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.91-6.svn1688
- Update to svn trunk at revision 1688 from upstream.
- Add support pkgconfig to devel package.
- Update BuildRequires: on corosynclib-devel.
- Tidy up spec files by re-organazing sections according to packages.
- Split libraries from openais to openaislib.
- Rename openais-devel to openaislib-devel.
- Comply with multiarch requirements (libraries).

* Tue Jan 27 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.91-5.svn1682
- Update to svn trunk at revision 1682 from upstream.

* Mon Dec 15 2008 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.91-4.svn1667
- No change rebuild against newer corosync.

* Wed Dec 10 2008 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.91-3.svn1667
- Update to svn trunk at revision 1667 from upstream.
- Update spec file to support alpha tag versioning.
- Tight dependencies (both build and runtime) with corosync to avoid
  internal ABI issues.

* Mon Oct 13 2008 Dennis Gilmore <dennis@ausil.us> 0.91-2
- remove ExclusiveArch line

* Fri Aug 15 2008 Steven dake <sdake@redhat.com> 0.91-1
- Upgrade to work with upstream corosync cluster engine.

* Mon May 19 2008 Steven Dake <sdake@redhat.com> 0.80.3-17
- Resolves: rhbz#400941
- Wrong bugzilla id caused rejection during commit.

* Mon May 19 2008 Steven Dake <sdake@redhat.com> 0.80.3-16
- Resolves: rhbz#400491
- Add upstream revision 1521 - Compile on latest glibc.
- Add upstream revision 1524 - Fix syscall usage in keygen application.
- Add upstream revision 1546 - Fix build for authentication on bsd platforms.
- Add upstream revision 1548 - Fix synchronization of checkpoint global id.

* Tue Apr 1 2008 Steven Dake <sdake@redhat.com> - 0.80.3-15
- Resolves: rhbz#432531
- Add upstream revision 1514 - Remove extra log_printf.
- Add upstream revision 1513 - Remove comparison with zero and replace with comparison with NULL in handle database code.
- Add upstream revision 1512 - Remove early commit of synchronization data when a synchronization in progress is followed by a node leaving or joining the cluster.
- Add upstream revision 1511 - Remove double pthread_mutex_destroy from evt service.
- Add upstream revision 1510 - Remove double pthread_mutex_destroy from evs service.
- Add upstream revision 1509 - Remove double pthread_mutex_destroy from cpg service.
- Add upstream revision 1508 - Remove double pthread_mutex_destroy from clm service.
- Add upstream revision 1507 - Remove double pthread_mutex_destroy from checkpoint service.
* Sat Mar 15 2008 Steven Dake <sdake@redhat.com> - 0.80.3-14
- Resolves: rhbz#432531
- Add upstream revision 1506 - Resolves incomplete checkpoing synchronization when totem queue is full.

* Thu Mar 6 2008 Steven Dake <sdake@redhat.com> - 0.80.3-13
- Resolves: rhbz#432531
- Add upstream revision 1504 - Fixes checkpoint synchronization issue when a new node is started.
- Add upstream revision 1503 - backport -f foreground option.
- Add upstream revision 1502 - Revert revision 1477 which exhibits problems with cman.
- Add revision 1477 - This was reverted in a previous version but cherrypicked.  Now the patch has been applied and reverted in the rpm build process to match upstream.


* Tue Feb 26 2008 Steven Dake <sdake@redhat.com> - 0.80.3-12
- Resolves: rhbz#433839
- Fix problem with cvs not allowing new checkin requires new revision.

* Fri Feb 22 2008 Steven Dake <sdake@redhat.com> - 0.80.3-11
- Resolves: rhbz#429920
- Add upstream revision 1500 - IPC locks up if a POLLERR is returned in certain circumstances.
- Resolves: rhbz#433839
- Add upstream revision 1501 - A mcast is delivered before a join in some circumstances.
* Fri Jan 18 2008 Steven Dake <sdake@redhat.com> - 0.80.3-10
- Resolves: rhbz#249287
- Remove upstream revision 1477 - Exhibits problem with revolver tester

* Tue Jan 15 2008 Steven Dake <sdake@redhat.com> - 0.80.3-9
- Resolves: rhbz#249287
- Add upstream revision 1499 - ipc changes merged into tree

* Tue Jan 15 2008 Steven Dake <sdake@redhat.com> - 0.80.3-8
- Resolves: rhbz#249287
- Add non-merged IPC changes for fixing operation with cluster mirror
- Resolves: rhbz#403901
- Add upstream revision 1498 - enhance openais_exit_error to report string instead of error code
- Resolves: rhbz#309621
- Add upstream revision 1497 - Follow LSB guidelines for initscript
- Add upstream revision 1496 - Revert patch 1480 since it causes problems with cman
- Add upstream revision 1493 - Backport of patch 1379 to remove this_ip and replace with accessor functoins for use by ipc system
- Add upstream revision 1486 - Unlock mutex on error condition of no memory when creating handle
- Add upstream revision 1480 - Endian fixes for the totempg code
- Add upstream revision 1479 - Remove & when regular reference works properly.
- Add upstream revision 1478 - Patch to set system_from properly in retransmitted messages
- Add upstream revision 1473 - Fix pthread_equal for timer_delete operation
- Add upstream revision 1471 - Endian convert cpg downlist messages properly
- Add upstream revision 1469 - change initialDataSize paramter from saUint32gt to SaSizeT to match specifications

* Tue Oct 2 2007 Steven Dake <sdake@redhat.com> - 0.80.3-7
- Resolves: rhbz#216954
- Add upstream revision 1465 - remove fsync call that blocks protocol

* Mon Sep 24 2007 Steven Dake <sdake@redhat.com> - 0.80.3-5
- Resolves: rhbz#302341
- Add upstream revision 1455 - Fix loss of node joins in commit state resulting in looping of membership protocol.
- Add upstream revision 1453 - Fix assertion if component registration occurs during certain phases of instantation.
- Add upstream revision 1450 - Fix reference counting in lcr code so that lcr_ifact_release works properly.
- Add upstream revision 1449 - Allow missing services in synchronization to not cause a segfault.k
- Add upstream revision 1446 - Remove inadvertant commit of changes to totemsrp which happened when security changes were patched in revision 1426.
- Add upstream revision 1426 - Patch to log security warnings when invalid identifier is used in message header for a totem header.

* Tue Aug 28 2007 Steven Dake <sdake@redhat.com> - 0.80.3-4
- Resolves: rhbz#251082
- Add upstream revision 1423 - Fix synchronization defect resulting in segfault.
- This is the fc6 build.
 
* Tue Aug 1 2007 Steven Dake <sdake@redhat.com> - 0.80.3-3
- Resolves: rhbz#209862
- Resolves: rhbz#249506
- Resolves: rhbz#249509
- Resolves: rhbz#247733

* Tue Aug 1 2007 Steven Dake <sdake@redhat.com> - 0.80.3-2
- Resolves: rhbz#209862
- Add upstream revision 1406 - Filter commit token when it is retransmitted.
- Resolves: rhbz#249506
- Add upstream revision 1407 - Reset consensus array on entering operational mode.
- Resolves: rhbz#249509
- Add upstream revision 1408 - Store the ring id information properly when it changes.
- Resolves: rhbz#247733
- Add upstream revision 1409 - Add subtractor to availability of message entries for the totem message queue
- This is the rhel5 version of 0.80.3-0 with some upstream patches.

* Tue Jun 26 2007 Steven Dake <sdake@redhat.com> - 0.80.3-1
- Resolves: rhbz#243119
- Resolves: rhbz#221190
- Resolves: rhbz#224190
- Resolves: rhbz#233892
- Resolves: rhbz#236549
- New upstream version including all previous revisions.
- This is the fc6 version of 0.80.3-1.

* Tue Jun 26 2007 Steven Dake <sdake@redhat.com> - 0.80.3-0
- Resolves: rhbz#243119
- Resolves: rhbz#221190
- Resolves: rhbz#224190
- Resolves: rhbz#233892
- Resolves: rhbz#236549
- New upstream version including all previous revisions.
- This is the rhel5 version of 0.80.3-0.

* Mon Dec 18 2006 Steven Dake <sdake@redhat.com> - 0.80.2-1
- Resolves: rhbz#211357
- This is the rhel5 version of 0.80.2-0.

* Mon Dec 18 2006 Steven Dake <sdake@redhat.com> - 0.80.2-0
- Resolves: rhbz#211357
- New upstream version including all prevision revisions.
- Fixes cpg ordering problem.
- Fixes ia64 unaligned problem.
- This is the fc6 version.

* Tue Dec 5 2006 Steven Dake <sdake@redhat.com> - 0.80.1-22
- Resolves: rhbz#216492
- This is the rhel5 version of 0.80.1-21.

* Tue Dec 5 2006 Steven Dake <sdake@redhat.com> - 0.80.1-21
- Resolves: rhbz#216492
- Add upstream revision 1319 - Increase outbound buffer size to 5000 messages.
- Add upstream revision 1316 - Improvements on segfault logging.
- This is the fc6 version.

* Wed Nov 29 2006 Steven Dake <sdake@redhat.com> - 0.80.1-20
- Resolves: rhbz#216492
- Need new res line to commit.  This is the same as 0.80.1-18.

* Wed Nov 29 2006 Steven Dake <sdake@redhat.com> - 0.80.1-19
- This is the rhel5 version of 0.80.1-18.

* Wed Nov 29 2006 Steven Dake <sdake@redhat.com> - 0.80.1-18
- Add upstream revision 1315 - Fix compile error in libcpg.
- Add upstream revision 1314 - Change rundir to /var/openais.
- Add upstream revision 1313 - Flow control fixes for the CPG service.
- Add upstream revision 1312 - Correct usage of ERR_LIBRARY to SA_AIS_ERR_LIBRARY.
- Add upstream revision 1311 - handle case where POLLHUP and POLLERR are not uspported by OS.
- Add upstream revision 1309 - set default downcheck value to 1000ms.
- Add upstream revision 1308 - Remove invalid code and warnings detected by Intel compiler.
- This is the fc6 version.

* Tue Nov 14 2006 Steven Dake <sdake@redhat.com> - 0.80.1-17
- This is the rhel5 version of 0.80.1-16.

* Tue Nov 14 2006 Steven Dake <sdake@redhat.com> - 0.80.1-16
- Add upstream revision 1307 - Remove flow control compile warning.
- Add upstream revision 1306 - Make clean now really makes clean.
- Add upstream revision 1305 - Set scheduler SCHED_RR to max priority available
  in system.
- Add upstream revision 1300 - Improve behavior of flow control of CPG service
  during configuration changes.
- This is the fc6 version.

* Thu Nov 9 2006 Steven Dake <sdake@redhat.com> - 0.80.1-15
- This is the rhel5 version of 0.80.1-14

* Thu Nov 9 2006 Steven Dake <sdake@redhat.com> - 0.80.1-14
- Add upstream revision 1296 - Remove compile warnings.
- Add upstream revision 1295 - The totem membership protocol was changed to
- Add upstream revision 1294 - modify location of ringid file to
- Add upstream revision 1293 - flush output of debug messages on exit or segv.
  /var/run/openais and chdir here so cores are saved there.
  match specifications.
- This is the fc6 version.

* Fri Nov 3 2006 Steven Dake <sdake@redhat.com> - 0.80.1-13
- Add upstream revision 1286 - Fix checkpoint unlink operation under certain
  conditions.  This is the rhel5 version.

* Fri Nov 3 2006 Steven Dake <sdake@redhat.com> - 0.80.1-12
- Add upstream revision 1286 - Fix checkpoint unlink operation under certain
  conditions.  This is the fc6 version.

* Tue Oct 24 2006 Steven Dake <sdake@redhat.com> - 0.80.1-11
- Add upstream revision 1284 - Initialize variables for checkpoint sync.

* Tue Oct 24 2006 Steven Dake <sdake@redhat.com> - 0.80.1-10
- Add %{?dist} to release field.

* Tue Oct 24 2006 Steven Dake <sdake@redhat.com> - 0.80.1-9
- Add upstream revision 1270 - Resolve IPC segfault.
- Add upstream revision 1271 - Fix errors in ia64 alignment.
- Add upstream revision 1275 - pthread_mutex_destroy cleanup patch.
- Add upstream revision 1276 - Remove debug from makefile committed in revision 1275.
- Add upstream revision 1277 - Formatting changes.
- Add upstream revision 1278 - Patch testckpt to use proper seciton id size.
- Add upstream revision 1279 - Call abort in sync service when processing is interrupted.
- Add upstream revision 1282 - New generation checkpoint state machine.
- Add upstream revision 1283 - Fix memory leaks.

* Wed Oct 18 2006 Steven Dake <sdake@redhat.com> - 0.80.1-8
- Add upstream revision 1268 - Align data in totem delivery on 4 byte
  boundaries for ia64.
- Add upstream revision 1269 - Increase default stack size for IPC connections
  on ia64.

* Mon Oct 16 2006 Steven Dake <sdake@redhat.com> - 0.80.1-7
- Add upstream revision 1267 - rework of checkpoint synchronization.

* Thu Oct 12 2006 Steven Dake <sdake@redhat.com> - 0.80.1-6
- Add upstream revision 1260 - Allocate the retransmission token in
  instance initialize instead of totemsrp_initialize.
- Add upstream revision 1261 - cleanup the way the memb_index variable is
  handled in the commit token.
- Add upstream revision 1262 - Set the ring sequence number according to the
  totem specifications.
- Add upstream revision 1263 - Use the fullset variable instead of he local
  variable j to make easier code reading.
- Add upstream revision 1264 - If the failed_list has zero entries, don't
  add it as an iovector in the join messages.
- Add upstream revision 1265 - Only originate one regular token.

* Mon Oct 9 2006 Steven Dake <sdake@redhat.com> - 0.80.1-5
- Add upstream revision 1256 - remove extra totem debug logging output.
- Add upstream revision 1257 - fix subset operation to repair membership behavior.
- Add upstream revision 1258 - accept commit token in proper circumstances.

* Wed Oct 4 2006 Steven Dake <sdake@redhat.com> - 0.80.1-4
- Add upstream revision 1252 - display members that have left in system log properly.

* Thu Sep 28 2006 Steven Dake <sdake@redhat.com> - 0.80.1-3
- Add upstream revision 1248 - fix more intermittent failures with flow control
  system.

* Wed Sep 27 2006 Steven Dake <sdake@redhat.com> - 0.80.1-2
- Add upstream revision 1246 - fix intermittent failures with flow control
  system.

* Mon Sep 25 2006 Steven Dake <sdake@redhat.com> - 0.80.1-1.1
- Add upstream revision 1223 - Fix checkpoint write size of zero to
  return INVALID_PARAM error code.
- Add upstream revision 1230 - Add missing include for assert.h.
- Add upstream revision 1245 - Add cpgbench tool and better flow control system.
- Move /sbin/ldconfig into regular package from devel package.

* Tue Aug 15 2006 Steven Dake <sdake@redhat.com> - 0.80.1-1.0
- New stable upstream release

* Thu Aug 10 2006 Steven Dake <sdake@redhat.com> - 0.80-1.2
- Move libraries to openais package.
- Add cpg hash collision patch.
- Add makefile install clm patch.

* Tue Aug 8 2006 Steven Dake <sdake@redhat.com> - 0.80-1.1
- New process of tracking any revisions in the upstream stable branch.

* Sun Jul 23 2006 Steven Dake <sdake@redhat.com> - 0.80-1.0
- New upstream release.
- Added openais-cfgtool tool to install.
- Added openais/cfg.h header file.

* Mon Jul 17 2006 Steven Dake <sdake@redhat.com> - 0.79-1.0
- New upstream release.

* Mon Jul 10 2006 Steven Dake <sdake@redhat.com> - 0.78-1.2
- Allow build on s390 and s390x.

* Fri Jul 07 2006 Steven Dake <sdake@redhat.com> - 0.78-1.1
- Allow build on ia64.

* Thu Jul 06 2006 Steven Dake <sdake@redhat.com> - 0.78-1.0
- New upstream release.

* Wed Jun 21 2006 Steven Dake <sdake@redhat.com> - 0.77-1.0
- New upstream release.

* Tue Jun 13 2006 Steven Dake <sdake@redhat.com> - 0.76-1.8
- Readded ExlcusiveArch since build system builds s390 and ia64 which are
  untested.
- Add makefile override patch which fixes build with optflags on x86_64 arch.
- Remove -DOPENAIS_LINUX from passed CFLAGS since it now works properly with
  makefile override patch.

* Tue Jun 13 2006 Steven Dake <sdake@redhat.com> - 0.76-1.7
- Remove ExclusiveArch since all Fedora Core 6 arches have been tested.

* Fri Jun 9 2006 Steven Dake <sdake@redhat.com> - 0.76-1.6
- Move condrestart to %%postun instead of %%post.
- Call initscript directly as suggested by Jesse.

* Thu Jun 8 2006 Steven Dake <sdake@redhat.com> - 0.76-1.5
- Changed BuildRoot tag to match convention specified in Fedora Wiki.
- Removed /sbin/service dependency since it is pulled in from init packages.

* Mon Jun 5 2006 Steven Dake <sdake@redhat.com> - 0.76-1.4
- Moved uid 102 to 39 since uids over 99 are not suitable for core at Bill's
  suggestion.

* Mon Jun 5 2006 Steven Dake <sdake@redhat.com> - 0.76-1.3
- Allocated uid 102 from setup package for user add operation.
- Added || : to initscript stuff so initscript bugs dont cause RPM transaction
  failures as per Paul's suggestion.
- Added /sbin/services to post requires as per Paul's suggestion.
- Removed ldconfig from the requires post for the main package as per Paul's
  suggestion.
- Changed post devel scriptlet action as per Paul's suggestion.

* Thu May 31 2006 Steven Dake <sdake@redhat.com> - 0.76-1.2
- Add user account for AIS applications and authentication.
- Move /etc/ld.so.conf/openais-*.conf to devel package since it is
  only needed there.
- Move ldconfig to devel package.
- Execute condrestart on upgrade

* Fri May 25 2006 Steven Dake <sdake@redhat.com> - 0.76-1.1
- Fix unowned dirs problem.
- Correct make with optflags work properly.
- Move plugins from /usr/lib/openais/lcrso to /usr/libexec/lcrso.
- Remove static archives from RPM.
- Name shared objects in devel package as 1.0.0 instead of 1.0.

* Thu May 24 2006 Steven Dake <sdake@redhat.com> - 0.76-1.0
- New release of openais 0.76.

* Wed May 23 2006 Paul Howarth <paul@city-fan.org> - 0.75-1.1
- Address rpmlint issues during package review (#192889)
- Move docs to associated packages, don't bother with -docs subpackage
- Make -devel package require main package
- Fix Source: and URL: tags
- Fix up Makefile to handle DESTDIR properly
- Honoring %%{optflags} breaks build!

* Wed May 20 2006 Steven Dake <sdake@redhat.com> - 0.75-1.0
- Initial import.
