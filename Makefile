ROOT=/

VERSION=$(shell awk '/Version:/ { print $$2 }' initscripts.spec)
CVSTAG = r$(subst .,-,$(VERSION))

mandir=/usr/share/man

all:
	(cd src; $(MAKE) CFLAGS="$(CFLAGS)")

install:
	mkdir -p $(ROOT)/etc/profile.d $(ROOT)/sbin $(ROOT)/usr/sbin
	mkdir -p $(ROOT)$(mandir)/man8
	$(INSTALL) -m644  inittab $(ROOT)/etc
	$(INSTALL) -m644  adjtime $(ROOT)/etc
	$(INSTALL) -m755  setsysfont $(ROOT)/sbin
	$(INSTALL) -m755  lang.sh $(ROOT)/etc/profile.d
	$(INSTALL) -m755  lang.csh $(ROOT)/etc/profile.d
	$(INSTALL) -m755  service $(ROOT)/sbin
	$(INSTALL) -m755  sys-unconfig $(ROOT)/usr/sbin
	$(INSTALL) -m644  sys-unconfig.8 $(ROOT)$(mandir)/man8
	( if uname -m | grep -q sparc ; then \
	  $(INSTALL) -m644 sysctl.conf.sparc $(ROOT)/etc/sysctl.conf ; \
	  else \
	  $(INSTALL) -m644 sysctl.conf $(ROOT)/etc/sysctl.conf ; \
	  fi )
	mkdir -p $(ROOT)/etc/X11
	$(INSTALL) -m755 prefdm $(ROOT)/etc/X11/prefdm
	mkdir -p $(ROOT)/etc/sysconfig
	mkdir -p $(ROOT)/etc/sysconfig/console
	$(INSTALL) -m644 sysconfig/init $(ROOT)/etc/sysconfig/init
	$(INSTALL) -m644 sysconfig/rawdevices $(ROOT)/etc/sysconfig/rawdevices
	cp -af rc.d sysconfig ppp $(ROOT)/etc
	chmod 755 $(ROOT)/etc/rc.d/init.d/rawdevices
	mkdir -p $(ROOT)/sbin
	mv $(ROOT)/etc/sysconfig/network-scripts/ifup $(ROOT)/sbin
	mv $(ROOT)/etc/sysconfig/network-scripts/ifdown $(ROOT)/sbin
	(cd $(ROOT)/etc/sysconfig/network-scripts; \
	  ln -sf ../../../sbin/ifup . ; \
	  ln -sf ../../../sbin/ifdown . )
	(cd src; $(MAKE) install ROOT=$(ROOT) mandir=$(mandir))
	mkdir -p $(ROOT)/var/run/netreport
	-chown root.root $(ROOT)/var/run/netreport
	chmod og=rwx,o=rx $(ROOT)/var/run/netreport

check:
	for afile in `find . -type f -perm +111|grep -v \.csh ` ; do \
		if ! file $$afile | grep -s ELF  >/dev/null; then \
		    bash -n $$afile || { echo $$afile ; exit 1; } ; \
		fi  ;\
	done
	make -C mandrake check

changelog:
	make -C mandrake changelog

clean:
	(cd src; $(MAKE) clean)
	@rm -fv *~ changenew ChangeLog.old

tag-archive:
	@cvs -Q tag -F $(CVSTAG)

create-archive: tag-archive
	@rm -rf /tmp/initscripts
	@cd /tmp; cvs -Q -d $(CVSROOT) export -r$(CVSTAG) initscripts || echo GRRRrrrrr -- ignore [export aborted]
	@mv /tmp/initscripts /tmp/initscripts-$(VERSION)
	@cd /tmp; tar czSpf initscripts-$(VERSION).tar.gz initscripts-$(VERSION)
	@rm -rf /tmp/initscripts-$(VERSION)
	@cp /tmp/initscripts-$(VERSION).tar.gz .
	@rm -f /tmp/initscripts-$(VERSION).tar.gz 
	@echo " "
	@echo "The final archive is ./initscripts-$(VERSION).tar.gz."

archive: clean check tag-archive create-archive
