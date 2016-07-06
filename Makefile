# Global
TMPDIR := ./tmp
LIBRARY = $(TMPDIR)/library
LOCAL_MIRROR = /tmp/pypi
MIRROR_REQ = ./dependencies/requirements.txt
DOCS = ./docs
SAMPLES = $(DOCS)/samples
SITE_PACKAGES := $(shell python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")

# Assets-related
ASSETS_DIR = ./ui_assets_src
OUTPUT_DIR = ./librarian/static
COMPASS_CONF = $(ASSETS_DIR)/compass.rb
COFFEE_SRC = $(ASSETS_DIR)/coffee
SCSS_SRC = $(ASSETS_DIR)/scss
JS_OUT = $(OUTPUT_DIR)/js
JS_NOPRUNE = $(JS_OUT)/vendor

# FSAL-related
FSAL_SAMPLE = $(SAMPLES)/fsal.ini
FSAL_CONF := $(TMPDIR)/fsal.ini
FSAL_SOCK := $(TMPDIR)/fsal.ctrl

# Librarian-related
LIBRARIAN_SAMPLE = $(SAMPLES)/librarian.ini
LIBRARIAN_CONF := $(TMPDIR)/librarian.ini

# PID files
COMPASS_PID = $(TMPDIR)/.compass_pid
COFFEE_PID = $(TMPDIR)/.coffee_pid
FSAL_PID = $(TMPDIR)/.fsal_pid

.PHONY: \
	stop-assets \
	prepare \
	local-mirror \
	start \
	stop \
	restart \
	restart-assets \
	restart-fsal \
	start-assets \
	stop-assets \
	start-fsal \
	stop-fsal \
	start-coffee \
	start-compass \
	stop-compass \
	stop-coffee \
	recompile-assets \
	reindex \
	docs \
	clean-doc

prepare: local-mirror $(FSAL_CONF) $(LIBRARIAN_CONF)
	pip install -e . --upgrade --pre \
		--extra-index-url file://$(LOCAL_MIRROR)/simple

local-mirror:
	pip install --upgrade pip
	pip install --upgrade pip2pi
	pip2pi --normalize-package-names $(LOCAL_MIRROR) --no-deps \
		--no-binary :all: --pre -r $(MIRROR_REQ)

start: start-assets start-fsal

stop: stop-assets stop-fsal

restart: restart-assets rstart-fsal

start-assets: $(COMPASS_PID) $(COFFEE_PID)

stop-assets: stop-compass stop-coffee

restart-assets: stop-assets watch-assets

start-compass: $(COMPASS_PID)

start-coffee: $(COFFEE_PID)

stop-compass:
	@-kill -s TERM $$(cat $(COMPASS_PID))
	@-rm $(COMPASS_PID)

stop-coffee:
	@-kill -s INT $$(cat $(COFFEE_PID))
	@-rm $(COFFEE_PID)

start-fsal: $(LIBRARY) $(FSAL_PID)

stop-fsal:
	@-kill -s TERM $$(cat $(FSAL_PID))

restart-fsal: stop-fsal
	# We don't use start as a dependency because we need a 5s pause
	@echo "Waiting for things to settle..."
	@sleep 5
	@make start-fsal

recompile-assets:
	@compass compile --force -c $(COMPASS_CONF)
	@find $(JS_OUT) -path $(JS_NOPRUNE) -prune -o -name "*.js" -exec rm {} +
	@coffee --bare -c --output $(JS_OUT) $(COFFEE_SRC)
	@librarian --assets

docs: clean-doc
	@make -C $(DOCS) html

clean-doc:
	@make -C $(DOCS) clean

reindex: $(FSAL_SOCK)
	@python scripts/reindex.py -s $(FSAL_SOCK)

$(COMPASS_PID): $(TMPDIR)
	@compass watch -c $(COMPASS_CONF) & echo $$! > $@

$(COFFEE_PID): $(TMPDIR)
	@coffee --bare --watch --output $(JS_OUT) $(COFFEE_SRC) & echo $$! > $@

$(FSAL_PID): $(TMPDIR)
	@fsal-daemon --conf $(FSAL_CONF) --pid-file $@

$(FSAL_CONF): $(FSAL_SAMPLE) $(TMPDIR)
	@cat $< | sed 's|PREFIX|$(SITE_PACKAGES)|' > $@

$(LIBRARIAN_CONF): $(LIBRARIAN_SAMPLE) $(TMPDIR)
	@cat $< > $@

$(LIBRARY):
	@mkdir -p $@

$(TMPDIR):
	@mkdir -p $@
