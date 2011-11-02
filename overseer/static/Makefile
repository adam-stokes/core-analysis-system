NAME=cas
PKGDIR=/usr/share/$(NAME)/overseer/static

all:
	echo "nada"

clean:
	rm -f *.pyc *.pyo *~

install:
	mkdir -p $(DESTDIR)$(PKGDIR)/blueprint
	mkdir -p $(DESTDIR)$(PKGDIR)/enhance
	install -m644 blueprint/*.css $(DESTDIR)$(PKGDIR)/blueprint/.
	install -m644 *.html $(DESTDIR)$(PKGDIR)/.
	install -m644 enhance/*.png $(DESTDIR)$(PKGDIR)/enhance/.
