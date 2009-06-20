
PLUGINDIR=/usr/lib/rhythmbox/plugins

install:
	install -d $(DESTDIR)$(PLUGINDIR)
	cp -a rhythmweb $(DESTDIR)$(PLUGINDIR)

install-user:
	install -d $(HOME)/.local/share/rhythmbox/plugins
	cp -a rhythmweb $(HOME)/.local/share/rhythmbox/plugins

dist:
	git archive $(RELEASE) | gzip > rhythmweb-$(RELEASE).tar.gz
