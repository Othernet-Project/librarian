# Global
TMPDIR := ./tmp

# Assets-related
COFFEE_SRC = src/coffee
JSDIR = librarian/static/js
SCSS_SRC = src/scss
COMPASS_CONF = conf/config.rb
SCRIPTS = scripts
EXCLUDE = vendor
COMPASS_PID = $(TMPDIR)/.compass_pid
COFFEE_PID = $(TMPDIR)/.coffee_pid

.PHONY: watch-assets stop-assets restart-assets recompile-assets

watch-assets: $(COMPASS_PID) $(COFFEE_PID) $(DEMO_COMPASS_PID) \
	$(DEMO_COFFEE_PID)

stop-assets:
	$(SCRIPTS)/compass.sh stop $(COMPASS_PID)
	$(SCRIPTS)/coffee.sh stop $(COFFEE_PID)

restart-assets: stop watch

recompile-assets: 
	compass compile --force -c $(COMPASS_CONF)
	find $(JSDIR) -path $(JSDIR)/$(EXCLUDE) -prune -o -name "*.js" -exec rm {} +
	coffee --bare -c --output $(JSDIR) $(COFFEE_SRC)

$(COMPASS_PID): $(SCRIPTS)/compass.sh
	$< start $@ $(COMPASS_CONF)

$(COFFEE_PID): $(SCRIPTS)/coffee.sh
	$< start $@ $(COFFEE_SRC) $(JSDIR)
