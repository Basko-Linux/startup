# 	$Id$	
%define version 4.97
%define release 42mdk

Summary: The inittab file and the /etc/rc.d scripts.
Name: initscripts
Version: %{version}
Release: %{release}
Copyright: GPL
Group: System/Base
Source0: initscripts-%{version}.tar.bz2
Patch:	initscripts-mdkconf.patch.bz2
BuildRoot: %{_tmppath}/%{name}-root
Requires: mingetty, /bin/awk, /bin/sed, mktemp, e2fsprogs >= 1.18-2mdk, console-tools
Requires: procps >= 2.0.6-8mdk, modutils >= 2.3.10, sysklogd >= 1.3.31, mount >= 2.10f-2mdk
Requires: /sbin/fuser, which, setup >= 2.1.9-3mdk
Prereq: /sbin/chkconfig, /usr/sbin/groupadd, gawk
Obsoletes: rhsound sapinit
Conflicts: kernel <= 2.2, timeconfig < 3.0, pppd < 2.3.9, wvdial < 1.40-3
Conflicts: initscripts < 1.22.1-5
BuildPrereq: glib-devel
%ifarch alpha
Requires: util-linux >= 2.9w-26
%endif

%description
The initscripts package contains the basic system scripts used to boot
your Mandrake system, change run levels, and shut the system down cleanly.
Initscripts also contains the scripts that activate and deactivate most
network interfaces.

%prep
%setup -q
%patch0 -p2

%build
make CFLAGS="$RPM_OPT_FLAGS"
make -C mandrake/ CFLAGS="$RPM_OPT_FLAGS"

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/etc
make ROOT=$RPM_BUILD_ROOT install 
mkdir -p $RPM_BUILD_ROOT/var/run/netreport
chmod u=rwx,g=rwx,o=rx $RPM_BUILD_ROOT/var/run/netreport

for i in 0 1 2 3 4 5 6 ; do
  file=$RPM_BUILD_ROOT/etc/rc.d/rc$i.d
  mkdir $file
  chmod u=rwx,g=rx,o=rx $file
done

# Can't store symlinks in a CVS archive
ln -s ../init.d/random $RPM_BUILD_ROOT/etc/rc.d/rc0.d/K80random
ln -s ../init.d/random $RPM_BUILD_ROOT/etc/rc.d/rc1.d/S20random
ln -s ../init.d/random $RPM_BUILD_ROOT/etc/rc.d/rc2.d/S20random
ln -s ../init.d/random $RPM_BUILD_ROOT/etc/rc.d/rc3.d/S20random
ln -s ../init.d/random $RPM_BUILD_ROOT/etc/rc.d/rc4.d/S20random
ln -s ../init.d/random $RPM_BUILD_ROOT/etc/rc.d/rc5.d/S20random
ln -s ../init.d/random $RPM_BUILD_ROOT/etc/rc.d/rc6.d/K80random

ln -s ../init.d/netfs $RPM_BUILD_ROOT/etc/rc.d/rc0.d/K75netfs
ln -s ../init.d/netfs $RPM_BUILD_ROOT/etc/rc.d/rc1.d/K75netfs
ln -s ../init.d/netfs $RPM_BUILD_ROOT/etc/rc.d/rc2.d/K75netfs
ln -s ../init.d/netfs $RPM_BUILD_ROOT/etc/rc.d/rc3.d/S25netfs
ln -s ../init.d/netfs $RPM_BUILD_ROOT/etc/rc.d/rc4.d/S25netfs
ln -s ../init.d/netfs $RPM_BUILD_ROOT/etc/rc.d/rc5.d/S25netfs
ln -s ../init.d/netfs $RPM_BUILD_ROOT/etc/rc.d/rc6.d/K75netfs


ln -s ../init.d/network $RPM_BUILD_ROOT/etc/rc.d/rc0.d/K90network
ln -s ../init.d/network $RPM_BUILD_ROOT/etc/rc.d/rc1.d/K90network
ln -s ../init.d/network $RPM_BUILD_ROOT/etc/rc.d/rc2.d/S10network
ln -s ../init.d/network $RPM_BUILD_ROOT/etc/rc.d/rc3.d/S10network
ln -s ../init.d/network $RPM_BUILD_ROOT/etc/rc.d/rc4.d/S10network
ln -s ../init.d/network $RPM_BUILD_ROOT/etc/rc.d/rc5.d/S10network
ln -s ../init.d/network $RPM_BUILD_ROOT/etc/rc.d/rc6.d/K90network

ln -s ../init.d/killall $RPM_BUILD_ROOT/etc/rc.d/rc0.d/S00killall
ln -s ../init.d/killall $RPM_BUILD_ROOT/etc/rc.d/rc6.d/S00killall

ln -s ../init.d/halt $RPM_BUILD_ROOT/etc/rc.d/rc0.d/S01halt
ln -s ../init.d/halt $RPM_BUILD_ROOT/etc/rc.d/rc6.d/S01reboot

ln -s ../init.d/single $RPM_BUILD_ROOT/etc/rc.d/rc1.d/S00single

ln -s ../rc.local $RPM_BUILD_ROOT/etc/rc.d/rc2.d/S99local
ln -s ../rc.local $RPM_BUILD_ROOT/etc/rc.d/rc3.d/S99local
ln -s ../rc.local $RPM_BUILD_ROOT/etc/rc.d/rc5.d/S99local

mkdir -p $RPM_BUILD_ROOT/var/{log,run}
touch $RPM_BUILD_ROOT/var/run/utmp
touch $RPM_BUILD_ROOT/var/log/wtmp

#MDK
make -C mandrake/ install ROOT=$RPM_BUILD_ROOT

%pre
/usr/sbin/groupadd -g 22 -r -f utmp

%post
##Fixme
touch /etc/sysconfig/i18n
##
touch /var/log/wtmp
touch /var/run/utmp
chown root.utmp /var/log/wtmp /var/run/utmp
chmod 664 /var/log/wtmp /var/run/utmp

chkconfig --add random 
chkconfig --add netfs 
chkconfig --add network 
chkconfig --add sound
chkconfig --add kheader

%ifnarch sparc sparc64
chkconfig --add usb
%endif

# handle serial installs semi gracefully
if [ $1 = 0 ]; then
  if [ "$TERM" = "vt100" ]; then
      tmpfile=/etc/sysconfig/tmp.$$
      sed -e '/BOOTUP=color/BOOTUP=serial/' /etc/sysconfig/init > $tmpfile
      mv -f $tmpfile /etc/sysconfig/init
  fi
fi

# dup of timeconfig %post - here to avoid a dependency
if [ -L /etc/localtime ]; then
    _FNAME=`ls -ld /etc/localtime | awk '{ print $11}' | sed 's/lib/share/'`
    rm /etc/localtime
    cp -f $_FNAME /etc/localtime
    if ! grep -q "^ZONE=" /etc/sysconfig/clock ; then
      echo "ZONE=\"$_FNAME"\" | sed -e "s|[^\"]*/usr/share/zoneinfo/||" >> /etc/sysconfig/clock
    fi
fi

%preun
if [ $1 = 0 ]; then
  chkconfig --del random
  chkconfig --del netfs
  chkconfig --del network
%ifnarch sparc sparc64
  chkconfig --del usb
%endif
  chkconfig --del sound
  chkconfig --add kheader
fi

%triggerpostun -- initscripts <= 4.72

. /etc/sysconfig/init
. /etc/sysconfig/network

# These are the non-default settings. By putting them at the end
# of the /etc/sysctl.conf file, it will override the default
# settings earlier in the file.

if [ -n "$FORWARD_IPV4" -a "$FORWARD_IPV4" != "no" -a "$FORWARD_IPV4" != "false" ]; then
	echo "# added by initscripts install on `date`" >> /etc/sysctl.conf
	echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
fi
if [ "$DEFRAG_IPV4" = "yes" -o "$DEFRAG_IPV4" = "true" ]; then
	echo "# added by initscripts install on `date`" >> /etc/sysctl.conf
	echo "net.ipv4.ip_always_defrag = 1" >> /etc/sysctl.conf
fi
if [ -n "$MAGIC_SYSRQ" -a "$MAGIC_SYSRQ" != "no" ]; then
	echo "# added by initscripts install on `date`" >> /etc/sysctl.conf
	echo "kernel.sysrq = 0" >> /etc/sysctl.conf
fi
if uname -m | grep -q sparc ; then
   if [ -n "$STOP_A" -a "$STOP_A" != "no" ]; then
	echo "# added by initscripts install on `date`" >> /etc/sysctl.conf
	echo "kernel. = 1" >> /etc/sysctl.conf
   fi
fi

%postun
if [ -f /var/lock/TMP_1ST ];then 
		rm -f /var/lock/TMP_1ST
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%dir /etc/sysconfig/network-scripts
%config %verify(not md5 mtime size) /etc/adjtime
%config(noreplace) /etc/sysconfig/init
/etc/sysconfig/network-scripts/ifdown
%config /sbin/ifdown
%config /etc/sysconfig/network-scripts/ifdown-post
/etc/sysconfig/network-scripts/ifup
%config /sbin/ifup
%dir /etc/sysconfig/console
%config /etc/sysconfig/network-scripts/network-functions
%config /etc/sysconfig/network-scripts/ifup-post
%config /etc/sysconfig/network-scripts/ifcfg-lo
%config /etc/sysconfig/network-scripts/ifdown-ppp
%config /etc/sysconfig/network-scripts/ifdown-sl
%config /etc/sysconfig/network-scripts/ifup-ppp
%config /etc/sysconfig/network-scripts/ifup-sl
%config /etc/sysconfig/network-scripts/ifup-routes
%config /etc/sysconfig/network-scripts/ifup-plip
%config /etc/sysconfig/network-scripts/ifup-aliases
%config /etc/sysconfig/network-scripts/ifup-ipx
%config /etc/X11/prefdm
%config /etc/inittab
%dir    /etc/rc.d
%config /etc/rc.d/rc.sysinit
%dir    /etc/rc.d/rc0.d
%config(missingok) /etc/rc.d/rc0.d/*
%dir    /etc/rc.d/rc1.d
%config(missingok) /etc/rc.d/rc1.d/*
%dir    /etc/rc.d/rc2.d
%config(missingok) /etc/rc.d/rc2.d/*
%dir    /etc/rc.d/rc3.d
%config(missingok) /etc/rc.d/rc3.d/*
%dir    /etc/rc.d/rc4.d
%config(missingok) /etc/rc.d/rc4.d/*
%dir    /etc/rc.d/rc5.d
%config(missingok) /etc/rc.d/rc5.d/*
%dir    /etc/rc.d/rc6.d
%config(missingok) /etc/rc.d/rc6.d/*
%dir    /etc/rc.d/init.d
%config(missingok) /etc/rc.d/init.d/*
%config /etc/rc.d/rc
%config(noreplace) /etc/rc.d/rc.local
%config(noreplace) /etc/sysctl.conf
%config /etc/profile.d/lang.sh
%config /etc/profile.d/lang.csh
%config /etc/profile.d/inputrc.sh
%config /etc/profile.d/inputrc.csh
/usr/sbin/sys-unconfig
/sbin/setsysfont
/bin/doexec
/bin/ipcalc
/bin/usleep
%attr(4755,root,root) /usr/sbin/usernetctl
/sbin/consoletype
/sbin/getkey
%attr(2755,root,root) /sbin/netreport
/sbin/initlog
/sbin/minilogd
/sbin/service
/sbin/installkernel
/sbin/ppp-watch
/usr/man/man*/*
%dir %attr(775,root,root) /var/run/netreport
%config /etc/ppp/ip-up
%config /etc/ppp/ip-down
%config /etc/initlog.conf
%ghost %attr(0664,root,utmp) /var/log/wtmp
%ghost %attr(0664,root,utmp) /var/run/utmp
%config /etc/modules
%config /etc/rc.d/rc.modules
/sbin/is_depmod_necessary
%ifnarch sparc
/usr/sbin/supermount
%endif
%ifarch %ix86
/usr/sbin/detectloader
%endif
/usr/bin/*
%doc sysconfig.txt sysvinitfiles ChangeLog

%changelog
* Tue May 30 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-42mdk
- mandrake/installkernel: fix typo.

* Mon May 29 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-41mdk
- mandrake/usb: Don't load/unload keyboard on alpha (usb keyboard
  are builtins in alpha).
- mandrake/tmpdir.csh: Remove the /bin/csh to don't depend of csh.
- rc.d/rc.sysinit: Better devfs support (titi).
- mandrake/inputrc.csh: Remove = (not needed).

* Sun May 28 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-40mdk
- mandrake/Makefile: Include usb for alpha. 
- initscripts.spec: Include usb for alpha.

* Sun May 28 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-39mdk
- mandrake/mandrake_everytime: Always clean /tmp/esrv* and
  /tmp/kio* files when CLEAN_TMP is set.
- mandrake/mandrake_everytime: Don't disable supermount	 on sparc
  (not even present).
- mandrake/usb: if USB=no in /etc/sysconfig/usb return 0
- mandrake/rc.modules: Fix typo.
- mandrake/installkernel: remove the \. from the label for lilo to
  minimize the chars.
- mandrake/installkernel: don't try to do something with lilo or
  grub when we are not on a x86 machines.
- mandrake/installkernel: Add --quiet options.
- mandrake/installkernel: remove the mdk for secure for lilo to minimize
  the chars.
- mandrake/Makefile: Add binfmt_aout to /etc/modules on alpha for netscape.
- rc.d/rc.sysinit: Merge Adam Lesback <adam@mandrakesoft.com> ppc change.

* Fri May 26 2000 Adam Lebsack <adam@mandrakesoft.com> 4.97-38mdk
- Patch for rc.sysinit for Powermac clock

* Tue May 23 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-37mdk
- mandrake/Makefile: Add various if{,n}eq $(ARCH) for alpha and sparc.
- mandrake/initscripts.spec: Add various %ifarch for alpha and sparc.

* Tue May 16 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-36mdk
- mandrake/kheader: exit 0 when no mdk kernel.

* Wed May 10 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-35mdk
-  mandrake/inputrc.csh: Fix typo (jerome).

* Mon May  8 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-34mdk
- mandrake/usb: set sleep between loading interfaces.

* Sun May  7 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-33mdk
- mandrake/mandrake_firstime: fix when setting mixer and there is
 no mixer.

* Sat May  6 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-32mdk
- sysconfig/network-scripts/(ifup|ifdown): Set by default dhcpcd not dhcpxd.
- rc.d/init.d/network: Set ipv4 forwarding when  FORWARD_IPV4=(yes|true).

* Fri May  5 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-31mdk
- mandrake/usb: Add printer support.

* Fri May  5 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-30mdk
- mandrake/mandrake_firstime: set the mixer to 80% by default.
- mandrake/sound: use of aumix even for alsa.  printk=0 when loading
  modules.

* Tue May  2 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-29mdk
- rc.d/init.d/netfs: starting and stopping netfs properly.
- sysconfig/network-scripts/ifup{-aliases,plip}: remove old kernel
  compatibilities.

* Fri Apr 28 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-28mdk
- sysconfig/network-scripts/ifup (DHCP_ARGS): fix ugly ''basename
  command not found''
- sysconfig/network-scripts/ifdown (CONFIG): fix support for
  multiple dhcp client.

* Wed Apr 26 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-27mdk
- mandrake/usb: fix mounting proc usb and umount usbdevfs when stoping.
- mandrake/kheader: exit 0 when no mdk kernel.

* Mon Apr 24 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-26mdk
- mandrake/installkernel (grub_device): root=$root_device not $kversion.

* Mon Apr 24 2000 Pixel <pixel@mandrakesoft.com> 4.97-25mdk
- mandrake/usb: fix missing 'fi'

* Sun Apr 23 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-24mdk
- mandrake/sound: Add alsa support.

* Sun Apr 23 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-23mdk
- mandrake/installkernel: move from kernel to here.
- mandrake/usb: Mount usbdevfs if present.
- mandrake/detectloader: Don't detect cdrom.

* Wed Apr 19 2000 Pixel <pixel@mandrakesoft.com> 4.97-22mdk
- mandrake/mandrake_firstime: call postinstall.sh for webmin if there

* Tue Apr 18 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-21mdk
- mandrake/detectloader.8: man pages of detectloader.
- mandrake/detectloader: A new greatest hit.

* Mon Apr 17 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-20mdk
- rc.d/rc: if no askrunlevel installed jump directly to runlevel 1.
- rc.d/rc: s|ASKRUNLEVEL|failsafe|;
- rc.d/rc.sysinit: s|ASKRUNLEVEL|failsafe|;

* Sun Apr 16 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-19mdk
- rc.d/rc.sysinit: check if ASKRUNLEVEL arg.
- rc.d/rc: if specify ASKRUNLEVEL on commandline then run
askrunlevel interactively.
- rc.d/rc: if we found the tag "halt: yes" then stop the script even
if no subsytem is touched.
- sysconfig/network-scripts/network-functions: /dev/null some
error message.
- sysconfig/network-scripts/ifdown: Check to make sure the device
is actually up
- src/netreport.c (main): if no args then show usage.
- src/minilogd.c: stat the PATH_LOG better.
- service: add --full-restart options.
- rc.d/rc.sysinit (CLOCKFLAGS): if no UTC then set up as localtime.
- rc.d/init.d/network: If this is a final shutdown/halt, check for
network FS, and unmount them even if the user didn't turn on netfs
- rc.d/init.d/network: setting syscontrol network here.
- rc.d/init.d/network: fix typos.
- rc.d/init.d/halt: specify when retrying to umount devices.
- ppp/ip-up: using "$@" instead of "$*"
- ppp/ip-down: using "$@" instead of "$*"
- mandrake/sound: Add level 6 in chkconfig.

* Thu Apr 13 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-18mdk
- initscripts.spec: Conflicts: linuxconf <= 1.17r9 (for askrunlevel).
- mandrake/sound: new script.
- rc.d/rc.sysinit: check for executable when launching rc.modules.
- rc.d/rc.sysinit: remove sound stuff.
- rc.d/init.d/halt: remove sound stuff.
- rc.d/rc: if user ask for interactive setup, launch askrunlevel
  to change runlevel on the fly and (re)configure system before
  booting.

* Wed Apr 12 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-17mdk
- mandrake/usb: Try to find a usb adaptator.
- mandrake/usb: zip support.
- mandrake/supermount: lots of supermount fix from <denis@mandrakesoft.com>.

* Thu Apr  6 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-16mdk
- sysconfig.txt: Upgrade doc.
- mandrake/mandrake_everytime: Clean up /tmp if it choose at
  install.
- rc.d/init.d/halt: don't umount /var/shm do this from
  /etc/fstab.
- rc.d/rc.sysinit: don't mount /var/shm do this from
  /etc/fstab.

* Wed Apr  5 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-15mdk
- mandrake/supermount: add a chmod 0644 after writing the file
  (don't be nazi, let's permit the simple user to read the
  /etc/fstab file :\).

* Wed Apr  5 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-14mdk
- mandrake/supermount: fix multiple bugs (multiple cdrom, handle options).
- mandrake/mandrake_everytime: don't use insmod -p to detect is supermount 
  module is here.

* Mon Apr  3 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-13mdk
- rc.d/init.d/network: don't exclude ipp[0-9] from interfaces.

* Fri Mar 31 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-12mdk
- rc.d/rc.sysinit:  devfsd, shm support (titi).
- rc.d/init.d/halt: shm support (titi).

* Tue Mar 28 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-11mdk
- initscripts.spec: Add sysctl.conf in %files.

* Sat Mar 25 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-10mdk
- rc.d/rc.sysinit: ignore failure of symlinking System.map (aka	stderr to dave null)(pixel).
- mandrake/modules: new file kernel modules to load at boot time (btw: add vfat).
- mandrake/rc.modules: new file to load modules of /etc/modules.
- mandrake/supermount: Fix typo and chmou stupidity.
- mandrake/Makefile: Add kheader/rc.modules/modules.
- mandrake/mandrake_everytime: use better approach to detect if	
  supermount modules is not present.
- mandrake/mandrake_everytime: Remove the modprobe vfat.
- mandrake/mandrake_firstime: erase first logfile if the file is empty.
- initscripts.spec: Add kheader in %post %preun.
- initscripts.spec: Add rc.modules and modules in %files.
- initscripts.spec: chkconfig --del usb in %preun.
- initscripts.spec: Add changeLog in %doc.
- rc.d/rc.sysinit: remove generation of /boot/kernel.h (moved to
	kheader script).
- mandrake/kheader: new file
- mandrake/usb: fix description.
- sysconfig.txt: upgrade documentation.
- sysconfig/network-scripts/ifup: if BOOTPROTO=bootp launch them
  via pump.
- sysconfig/network-scripts/ifup: by default launch dhcpxd for
  DHCP if is not installed launch dhclient || dhcpcd || pump. If
  the variable DHCP_CLIENT= is specified in ifcfg-$device configure
  this one.

* Wed Mar 22 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-9mdk
- rc.d/rc.sysinit: fix buggy call in linuxconf stuff.
- mandrake/Makefile: include is_depmod_necessary
- mandrake/is_depmod_necessary.c: move it here from modutils package.

* Tue Mar 21 2000 Pixel <pixel@mandrakesoft.com> 4.97-8mdk
- rc.d/init.d/halt: added removing of entry /initrd/loopfs in
/etc/mtab. removed unused lnx4win stuff

- rc.d/rc.sysinit: added adding of entry /initrd/loopfs in
/etc/mtab

- rc.d/rc.sysinit: move the chmou linuxconf stuff (buggy by the
way, sed doesn't exit code depending on succeeding subst)

* Sun Mar 19 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-7mdk
- mandrake/Makefile: fix typo.
- initscripts.spec: Conflicts with linuxconf <= 1.17r5
- rc.d/rc.sysinit: preliminary linuxconf profile support.
- rc.d/rc.local: don't display too much information in issue.net
  if SECURITY_LEVEL => 4.
- mandrake/supermount.8: minor modifications.
- mandrake/usb: remove unused sleep
- initscripts.spec: add inputrc.csh in %files.

* Sat Mar 18 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-6mdk
- initscripts.spec: add inputrc.csh in %files.

* Thu Mar 16 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-5mdk
- initscripts.spec: requires setup >= 2.1.9-3mdk (for inputrc).

* Mon Mar 13 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-4mdk
- initscripts.spec: Adjust groups. 

* Mon Mar 13 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-3mdk
- rc.d/rc.sysinit: Remove nasty mount /boot stuff (pixel)
- mandrake/usb: Get working with the new configuration scheme for usb.
- mandrake/usb: Preferring to use usb-interface to usb-mouse-interface.

* Sun Mar 12 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.97-2mdk
- *: upgrade to 4.97.
- ChangeLog: new one.
- initscripts.spec: clean-up spec.
- sysconfig/network-scripts/ifup: fix typo.
- sysctl.conf: sysrq = 1 on mandrake.
- service: Exclude mandrake_firstime | mandrake_everytime.
- mandrake/usb: make compatible with usb backport.

* Sun Feb  6 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.72-14mdk
- Don't optimize for DVD-ROM(#740).

* Wed Jan 12 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.72-13mdk
- Fix wrong supermount man pages.

* Fri Jan  7 2000 Pixel <pixel@mandrakesoft.com> 4.72-12mdk
- more intelligent prefdm (in case of bad sysconfig/desktop)

* Thu Jan  6 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 4.72-11mdk
- remove the -i switch to dhcpd (thanks Gary Simmons <darshu@sympatico.ca).

* Thu Dec 30 1999 Chmouel Boudjnah <chmouel@mandrakesoft.com>
- Add supermount manpages (camille).

* Wed Dec 29 1999 Chmouel Boudjnah <chmouel@mandrakesoft.com>
- Add a supermount script to disable or enable supermount.
- fix typos.

* Wed Dec 29 1999 Chmouel Boudjnah <chmouel@mandrakesoft.com>
- Add makewhatis on first boot.

* Fri Dec 24 1999 Frederic Lepied <flepied@mandrakesoft.com> 4.72-4mdk
- fix halt not to call umount /proc.

* Tue Dec 21 1999 Chmouel Boudjnah <chmouel@mandrakesoft.com>
- 4.72.
- Fix a lot of bugs.
