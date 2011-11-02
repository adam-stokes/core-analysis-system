# cas Makefile

NAME = cas
VERSION = $(shell echo `awk '/^Version:/ {print $$2}' cas.spec`)
RELEASE = $(shell echo `awk '/^Release:/ {gsub(/\%.*/,""); print $2}' cas.spec`)

SUBDIRS = caslib \
contrib \
snippets \
overseer \
overseer/static

PYFILES = $(wildcard *.py)

RPM_BUILD_DIR = rpm-build
RPM_DEFINES = --define "_topdir %(pwd)/$(RPM_BUILD_DIR)" \
	--define "_builddir %{_topdir}" \
	--define "_rpmdir %{_topdir}" \
	--define "_srcrpmdir %{_topdir}" \
	--define "_specdir %{_topdir}" \
	--define "_sourcedir %{_topdir}"
RPM = rpmbuild
RPM_WITH_DIRS = $(RPM) $(RPM_DEFINES)

# mainly for rhel5 and below
MD5_DEFINES=--define "_source_filedigest_algorithm md5" \
	--define "_binary_filedigest_algorithm md5"

build:
	for d in $(SUBDIRS); do make -C $$d; [ $$? = 0 ] || exit 1 ; done

install:
	mkdir -p $(DESTDIR)/usr/bin
	mkdir -p $(DESTDIR)/usr/share/man/man1
	mkdir -p $(DESTDIR)/usr/share/man/man5
	mkdir -p $(DESTDIR)/var/lib/cas/snippets
	mkdir -p $(DESTDIR)/usr/share/$(NAME)/tests
	mkdir -p $(DESTDIR)/etc
	gzip -c man/en/cas.1 > cas.1.gz
	gzip -c man/en/cas-admin.1 > cas-admin.1.gz
	gzip -c man/en/cas.conf.5 > cas.conf.5.gz
	install -m755 cas $(DESTDIR)/usr/bin/cas
	install -m755 cas-server $(DESTDIR)/usr/bin/cas-server
	install -m755 cas-admin $(DESTDIR)/usr/bin/cas-admin
	install -m644 cas.1.gz $(DESTDIR)/usr/share/man/man1/.
	install -m644 cas-admin.1.gz $(DESTDIR)/usr/share/man/man1/.
	install -m644 cas.conf.5.gz $(DESTDIR)/usr/share/man/man5/.
	install -m644 AUTHORS LICENSE README $(DESTDIR)/usr/share/$(NAME)/.
	install -m644 $(NAME).conf $(DESTDIR)/etc/$(NAME).conf
	for d in $(SUBDIRS); do make DESTDIR=`cd $(DESTDIR); pwd` -C $$d install; [ $$? = 0 ] || exit 1 ; done

$(NAME)-$(VERSION).tar.gz: clean
	mkdir -p $(RPM_BUILD_DIR)/$(NAME)-$(VERSION)
	git clone $(PWD) $(RPM_BUILD_DIR)/$(NAME)-$(VERSION)
	rm -rf $(RPM_BUILD_DIR)/$(NAME)-$(VERSION)/.git
	tar Ccvzf $(RPM_BUILD_DIR) $(RPM_BUILD_DIR)/$(NAME)-$(VERSION).tar.gz $(NAME)-$(VERSION)

srpm-rhel5: clean $(NAME)-$(VERSION).tar.gz
	$(RPM_WITH_DIRS) $(MD5_DEFINES) -ts $(RPM_BUILD_DIR)/$(NAME)-$(VERSION).tar.gz

srpm-fedora: clean $(NAME)-$(VERSION).tar.gz
	$(RPM_WITH_DIRS) -ts $(RPM_BUILD_DIR)/$(NAME)-$(VERSION).tar.gz

rpm: clean $(NAME)-$(VERSION).tar.gz
	$(RPM_WITH_DIRS) -tb $(RPM_BUILD_DIR)/$(NAME)-$(VERSION).tar.gz

clean:
	rm -rfv {dist,build}
	rm -rf *.\~* cas.1.gz cas-admin.1.gz cas.conf.5.gz
	rm -rf $(RPM_BUILD_DIR)
	rm -rf MANIFEST
	for i in `find . -iname *.pyc`; do \
		rm $$i; \
	done; \
	for d in $(SUBDIRS); do make -C $$d clean ; done

