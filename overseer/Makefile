PYTHON=python
NAME=cas
PACKAGE = $(shell basename `pwd`)
PYFILES = $(wildcard *.py)
PKGDIR = /usr/share/$(NAME)/$(PACKAGE)

all:
	echo "nada"

clean:
	rm -f *.pyc *.pyo *~

install:
	mkdir -p $(DESTDIR)/$(PKGDIR)/static
	for p in $(PYFILES) ; do \
		install -m 755 $$p $(DESTDIR)/$(PKGDIR)/$$p; \
	done
	install -m 644 site.conf $(DESTDIR)/$(PKGDIR)/.
	$(PYTHON) -c "import compileall; compileall.compile_dir('$(DESTDIR)/$(PKGDIR)', 1, '$(PYDIR)', 1)"
