# $Id$

Name: startup
Version: 0.9.2
Release: alt1

Summary: The system startup scripts
License: GPL
Group: System/Base
Packager: Dmitry V. Levin <ldv@altlinux.org>
BuildArch: noarch

Source: %name-%version.tar.bz2

Provides: /etc/firsttime.d
PreReq: service >= 0.0.2-alt1, chkconfig, gawk, grep, sed, coreutils, %__subst
# Who could remind me where these dependencies came from?
Requires: findutils >= 0:4.0.33, modutils >= 0:2.4.12-alt4, mount >= 0:2.10q-ipl1mdk
Requires: procps >= 0:2.0.7-ipl5mdk, psmisc >= 0:19-ipl2mdk, util-linux >= 0:2.10q-ipl1mdk
# due to /sys
Requires: filesystem >= 0:2.1.7-alt1
# due to %_sysconfdir/adjtime
Requires: hwclock >= 2.23-alt1

# due to update_wms
Conflicts: xinitrc < 0:2.4.13-alt1
# due to gen_kernel_headers
Conflicts: kernel-headers-common < 0:1.1

%description
This package contains scripts used to boot your system,
change runlevels, and shut the system down cleanly.

%prep
%setup -q

%install
%__mkdir_p $RPM_BUILD_ROOT%_sysconfdir/rc.d/rc{0,1,2,3,4,5,6}.d
%__install -p -m644 inittab modules sysctl.conf $RPM_BUILD_ROOT%_sysconfdir/
%__install -pD -m755 setsysfont $RPM_BUILD_ROOT/sbin/setsysfont
%__cp -a rc.d sysconfig $RPM_BUILD_ROOT%_sysconfdir/

# these services do not support chkconfig:
# killall, halt, single local - Can't store symlinks in a CVS archive
%__ln_s ../init.d/killall $RPM_BUILD_ROOT%_sysconfdir/rc.d/rc0.d/S00killall
%__ln_s ../init.d/killall $RPM_BUILD_ROOT%_sysconfdir/rc.d/rc6.d/S00killall

%__ln_s ../init.d/halt $RPM_BUILD_ROOT%_sysconfdir/rc.d/rc0.d/S01halt
%__ln_s ../init.d/halt $RPM_BUILD_ROOT%_sysconfdir/rc.d/rc6.d/S01reboot

%__ln_s ../init.d/single $RPM_BUILD_ROOT%_sysconfdir/rc.d/rc1.d/S00single

for i in `seq 2 5`; do
	%__ln_s ../init.d/local $RPM_BUILD_ROOT%_sysconfdir/rc.d/rc$i.d/S99local
done

%__mkdir_p $RPM_BUILD_ROOT/var/{log,run}
touch $RPM_BUILD_ROOT/var/{log/wtmp,run/utmp}
touch $RPM_BUILD_ROOT%_sysconfdir/sysconfig/{clock,i18n,keyboard,mouse,system}
chmod -R +x $RPM_BUILD_ROOT%_sysconfdir/rc.d
%__mkdir_p $RPM_BUILD_ROOT%_sysconfdir/sysconfig/{console,harddisk}
touch $RPM_BUILD_ROOT%_sysconfdir/sysconfig/console/setterm

%__mkdir_p $RPM_BUILD_ROOT%_sysconfdir/firsttime.d
%__mkdir_p $RPM_BUILD_ROOT%_localstatedir/rsbac

%post
if [ $1 -eq 1 ]; then
	/sbin/chkconfig --add fbsetfont
	/sbin/chkconfig --add random
	/sbin/chkconfig --add rawdevices
fi

for f in /var/{log/wtmp,run/utmp}; do
	if [ ! -f "$f" ]; then
		:>>"$f"
		%__chown root:utmp "$f"
		%__chmod 664 "$f"
	fi
done

# Dup of timeconfig %%post - here to avoid a dependency.
if [ -L %_sysconfdir/localtime ]; then
	_FNAME=`/bin/ls -ld %_sysconfdir/localtime |/bin/awk '{print $11}' |/bin/sed 's/lib/share/'`
	if [ -f "$_FNAME" ]; then
		%__rm %_sysconfdir/localtime
		%__cp -fp "$_FNAME" %_sysconfdir/localtime
		if ! %__grep -q "^ZONE=" %_sysconfdir/sysconfig/clock; then
			echo "ZONE=\"$_FNAME"\" |/bin/sed -e "s|[^\"]*/usr/share/zoneinfo/||" >>%_sysconfdir/sysconfig/clock
		fi
	fi
fi

if %__grep -qs '^fb:[0-9]*:once:/etc/rc.d/scripts/framebuffer_setfont' /etc/inittab; then
	/sbin/chkconfig --add fbsetfont
	%__subst 's,^\(fb:[0-9]*:once:/etc/rc.d/scripts/framebuffer_setfont\),#\1,' /etc/inittab
fi

%preun
if [ $1 -eq 0 ]; then
	/sbin/chkconfig --del fbsetfont
	/sbin/chkconfig --del random
	/sbin/chkconfig --del rawdevices
fi

%triggerpostun -- initscripts < 1:5.49.1-alt1
for f in %_sysconfdir/{inittab,modules,sysctl.conf,sysconfig/{clock,console/setterm,framebuffer,i18n,init,keyboard,mouse,rawdevices,system}}; do
	if [ ! -f "$f" ]; then
	        if [ -f "$f".rpmsave ]; then
	                %__cp -pf "$f".rpmsave "$f"
	        elif [ -f "$f".rpmnew ]; then
	                %__cp -pf "$f".rpmnew "$f"
	        fi
	fi
done
/sbin/chkconfig --add fbsetfont
/sbin/chkconfig --add random
/sbin/chkconfig --add rawdevices

%triggerpostun -- startup < 0:0.2-alt1
/sbin/chkconfig --add fbsetfont

%files
%config(noreplace) %verify(not md5 mtime size) %_sysconfdir/sysconfig/*
%config(noreplace) %_sysconfdir/inittab
%config(noreplace) %_sysconfdir/modules
%config(noreplace) %_sysconfdir/sysctl.conf
%config(missingok) %_sysconfdir/rc.d/rc?.d/*
%dir    %_sysconfdir/rc.d/scripts
%config %_sysconfdir/rc.d/scripts/*
%config %_sysconfdir/rc.d/init.d/*
%config %_sysconfdir/rc.d/rc
%config %_sysconfdir/rc.d/rc.sysinit
%config %_sysconfdir/rc.d/rc.powerfail
/sbin/setsysfont
%ghost %attr(664,root,utmp) /var/log/wtmp
%ghost %attr(664,root,utmp) /var/run/utmp
%dir %_sysconfdir/firsttime.d
%dir %_localstatedir/rsbac

%changelog
* Sun Oct 03 2004 Dmitry V. Levin <ldv@altlinux.org> 0.9.2-alt1
- rc.sysinit:
  + enhanced LVM support, based on patch from Vladimir Kholmanov.
- scripts/cleanup:
  + recreate some directories in /tmp/ with proper permissions.

* Mon Aug 09 2004 Dmitry V. Levin <ldv@altlinux.org> 0.9.1-alt1
- scripts/vconfig-update: do nothing if /etc/alternatives
  directory doesn't exist.

* Wed May 26 2004 Dmitry V. Levin <ldv@altlinux.org> 0.9.0-alt1
- Removed scripts: init.d/ieee1394, init.d/usb.

* Wed May 26 2004 Dmitry V. Levin <ldv@altlinux.org> 0.8.4-alt1
- init.d/fbsetfont: fixed (#3120).
- sysconfig/clock: added missing desriptions (#3496).

* Sat Feb 07 2004 Dmitry V. Levin <ldv@altlinux.org> 0.8.3-alt1
- Requires: filesystem >= 0:2.1.7-alt1 (due to /sys).
- rc.d/rc.sysinit:
  + mount /sys where appropriate;
  + use "swapon -a -e" to activate swap partitions (#3781);
  + removed support for obsolete /lib/modules/default;
  + removed support for obsolete /boot/System.map;
  + added evms support (#3647).
- init.d/halt:
  + added nut support (#3701).
- sysctl.conf:
  + removed net.ipv4.ip_always_defrag key.

* Thu Jan 29 2004 Dmitry V. Levin <ldv@altlinux.org> 0.8.2-alt1
- rc.d/rc.sysinit: do not initialize console powersaver so early.
- setsysfont: source /etc/sysconfig/consolefont.

* Sun Jan 18 2004 Dmitry V. Levin <ldv@altlinux.org> 0.8.1-alt1
- sysctl.conf: fixed comment for net.ipv4.tcp_timestamps,
  thanks to Solar for the hint.
- Packaged as noarch (#3407).

* Wed Dec 24 2003 Dmitry V. Levin <ldv@altlinux.org> 0.8-alt1
- rc.sysinit:
  + removed old bits of linuxconf support;
  + enhanced USEMODULES support.

* Sun Oct 26 2003 Dmitry V. Levin <ldv@altlinux.org> 0.7-alt1
- %_sysconfdir/adjtime: relocated to hwclock package.
- scripts/indexhtml_update: relocated to indexhtml package.
- scripts/first_time:
  + moved menu support to menu package;
  + moved index.html support to indexhtml package;
  + moved aumix support to aumix-minimal package;
  + moved mozilla support to mozilla packages.
- init.d/clock:
  + check for /etc/localtime before 'clock start';
  + try to set timezone if not set.
  + new mode: tzset.
- rc.d/rc.sysinit:
  When /etc/adjtime is present and non-empty, run
  "clock start" after root filesystem is mounted read-write.

* Thu Oct 16 2003 Dmitry V. Levin <ldv@altlinux.org> 0.6-alt1
- init.d/ieee1394: new script (rider).
- scripts/first_time: removed kudzu call (rider).

* Tue Jun 03 2003 Dmitry V. Levin <ldv@altlinux.org> 0.5-alt1
- init.d/*: fixed lockfiles handling.
- init.d/killall: if first argument is not "start", exit.

* Wed May 28 2003 Dmitry V. Levin <ldv@altlinux.org> 0.4-alt1
- Added firsttime.d support (#0002287).

* Sun May 25 2003 Dmitry V. Levin <ldv@altlinux.org> 0.3-alt1
- init.d/fbsetfont: fixed tty initialization.

* Wed May 21 2003 Dmitry V. Levin <ldv@altlinux.org> 0.2-alt1
- Relocated scripts/framebuffer_setfont -> init.d/fbsetfont.
- Removed framebuffer_setfont entry from inittab.
- Dropped gen_kernel_headers in favour of adjust_kernel_headers.
- Removed update_wms and gen_kernel_headers calls from rc.sysinit.

* Mon May 12 2003 Dmitry V. Levin <ldv@altlinux.org> 0.1-alt1
- rc.sysinit:
  + removed (never used) devfs initialization code;
  + fixed ROOTFSTYPE initialization.
- init.d/halt: call poweroff in halt mode by default.
- scripts/indexhtml_update: use subst instead of perl.
- setsysfont: use absolute() to find path.
- scripts/lang: rewritten.
- everywhere:
  + use new functions from service package;
  + set WITHOUT_RC_COMPAT=1 .

* Wed Apr 23 2003 Dmitry V. Levin <ldv@altlinux.org> 0.0.2-alt1
- Relocated %_sysconfdir/rc?.d and %_sysconfdir/rc.d/rc?.d
  from this package to service package.

* Mon Apr 21 2003 Dmitry V. Levin <ldv@altlinux.org> 0.0.1-alt1
- Removed all service and networking code and packaged them separately.
- Renamed to startup.

* Sat Apr 19 2003 Dmitry V. Levin <ldv@altlinux.org> 5.49-ipl54mdk
- %_initdir/sound: don't sort aliases in LoadModule (#0001802).
- %_initdir/clock: test $HWCLOCK_ADJUST also for "true" value (#0002351).
- %_initdir/functions:
  + fixed check logic in daemon() a bit (#0002407).
  + fixed return code in killproc() (#0002412).
- %_initdir/outformat: check argumnets being passed to tput (#0002450).
- /etc/sysctl.conf:
  + set "net.ipv4.icmp_echo_ignore_broadcasts = 1" by default (#0002472);
  + added comments from Owl's sysctl.conf file.
- usernetctl: support variable definitions quoted with single quotes.
