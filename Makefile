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

.PHONY: \
	stop-assets \
	restart-assets \
	recompile-assets \
	start-coffee \
	start-compass \
	stop-compass \
	stop-coffee

start-assets: $(COMPASS_PID) $(COFFEE_PID)

stop-assets: stop-compass stop-coffee

$(COMPASS_PID):
	compass watch -c $(COMPASS_CONF) & echo $$! > $@

$(COFFEE_PID):
	coffee --bare --watch --output $(JS_OUT) $(COFFEE_SRC) & echo $$! > $@

stop-compass: $(COMPASS_PID)
	kill -s TERM $$(cat $<)
	rm $<

stop-coffee: $(COFFEE_PID)
	kill -s INT $$(cat $<)
	rm $<

restart-assets: stop-assets watch-assets

recompile-assets: 
	compass compile --force -c $(COMPASS_CONF)
	find $(JS_OUT) -path $(JS_NOPRUNE) -prune -o -name "*.js" -exec rm {} +
	coffee --bare -c --output $(JS_OUT) $(COFFEE_SRC)
