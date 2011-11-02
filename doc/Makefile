NAME = cas
VERSION = $(shell echo `awk '/^Version:/ {print $$2}' cas.spec`)

all:
	echo "newp"

install:
	mkdir -p $(DESTDIR)/usr/share/doc/$(NAME)-$(VERSION)
	mkdir -p $(DESTDIR)/usr/share/doc/$(NAME)-$(VERSION)/_images
	mkdir -p $(DESTDIR)/usr/share/doc/$(NAME)-$(VERSION)/_static
	mkdir -p $(DESTDIR)/usr/share/doc/$(NAME)-$(VERSION)/_sources
	install -m655 * $(DESTDIR)/usr/share/doc/$(NAME)-$(VERSION)/.
	install -m655 * $(DESTDIR)/usr/share/doc/$(NAME)-$(VERSION)/_images/.
	install -m655 * $(DESTDIR)/usr/share/doc/$(NAME)-$(VERSION)/_static/.
	install -m655 * $(DESTDIR)/usr/share/doc/$(NAME)-$(VERSION)/_sources/.
