# Global
TMPDIR := ./tmp
SCRIPTS = scripts

# Assets-related
ASSETS_DIR = ./ui_assets_src
OUTPUT_DIR = ./librarian/static
COMPASS_CONF = $(ASSETS_DIR)/compass.rb
COFFEE_SRC = $(ASSETS_DIR)/coffee
SCSS_SRC = $(ASSETS_DIR)/scss
JS_OUT = $(OUTPUT_DIR)/js
JS_NOPRUNE = $(JS_OUT)/vendor
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
	find $(JS_OUT) -path $(JS_NOPRUNE) -prune -o -name "*.js" -exec rm {} +
	coffee --bare -c --output $(JS_OUT) $(COFFEE_SRC)

$(COMPASS_PID): $(SCRIPTS)/compass.sh
	$< start $@ $(COMPASS_CONF)

$(COFFEE_PID): $(SCRIPTS)/coffee.sh
	$< start $@ $(COFFEE_SRC) $(JS_OUT)
