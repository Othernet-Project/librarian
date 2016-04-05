# Global
TMPDIR := ./tmp
LOCAL_MIRROR = /tmp/pypi
MIRROR_REQ = ./dependencies/requirements.txt

# Assets-related
ASSETS_DIR = ./ui_assets_src
OUTPUT_DIR = ./librarian/static
COMPASS_CONF = $(ASSETS_DIR)/compass.rb
COFFEE_SRC = $(ASSETS_DIR)/coffee
SCSS_SRC = $(ASSETS_DIR)/scss
JS_OUT = $(OUTPUT_DIR)/js
JS_NOPRUNE = $(JS_OUT)/vendor

# FSAL-related
FSAL_CONF := $(TMPDIR)/fsal.ini

# PID files
COMPASS_PID = $(TMPDIR)/.compass_pid
COFFEE_PID = $(TMPDIR)/.coffee_pid
FSAL_PID = $(TMPDIR)/.fsal_pid

.PHONY: \
	stop-assets \
	restart-assets \
	recompile-assets \
	prepare \
	start \
	stop \
	start-fsal \
	start-coffee \
	start-compass \
	stop-compass \
	stop-coffee

prepare:
	pip install pip2pi
	pip2pi --normalize-package-names $(LOCAL_MIRROR) --no-deps \
		--no-binary :all: -r $(MIRROR_REQ)
	pip install -e . --extra-index-url file://$(LOCAL_MIRROR) 

start: start-asset start-fsal

stop: stop-assets stop-fsal

start-assets: $(COMPASS_PID) $(COFFEE_PID)

stop-assets: stop-compass stop-coffee

start-fsal: $(FSAL_PID)

stop-compass: $(COMPASS_PID)
	-kill -s TERM $$(cat $<)
	-rm $<

stop-coffee: $(COFFEE_PID)
	-kill -s INT $$(cat $<)
	-rm $<

stop-fsal: $(FSAL_PID)
	-kill -s TERM $$(cat $<)
	-rm $<

restart-assets: stop-assets watch-assets

recompile-assets: 
	compass compile --force -c $(COMPASS_CONF)
	find $(JS_OUT) -path $(JS_NOPRUNE) -prune -o -name "*.js" -exec rm {} +
	coffee --bare -c --output $(JS_OUT) $(COFFEE_SRC)

$(COMPASS_PID):
	compass watch -c $(COMPASS_CONF) & echo $$! > $@

$(COFFEE_PID):
	coffee --bare --watch --output $(JS_OUT) $(COFFEE_SRC) & echo $$! > $@

$(FSAL_PID): $(FSAL_CONF)
	fsal-daemon --conf $(FSAL_CONF) --pid-file $@ && echo $$! > $@
