#!/bin/make -f

.PHONY: all clean install release

sources = $(wildcard mod_*.c)
targets = $(sources:.py=.pyc)

WOTDIR = wot
wotver = 0.9.17.0.3
wotmod = res_mods/$(wotver)
wotmod_scripts = $(wotmod)/scripts/client/gui/mods
wotmod_configs = $(wotmod)/scripts/client/gui/mods

all: $(targets)
	python -m compileall mod_*.py

clean:
	rm *.pyc

install: all
	mkdir -p "$(WOTDIR)/$(wotmod_scripts)"
	cp -f mod_auto_equip.pyc mod_fast_repair.pyc mod_target.pyc "$(WOTDIR)/$(wotmod_scripts)"

release: all
	mkdir -p "$(wotmod_scripts)"
	cp -f mod_*.pyc "$(wotmod_scripts)"
	cp -f xml/*.xml "$(wotmod_configs)"
	cp -rf res/* "$(wotmod)"
	zip -r lwp.zip res_mods/
	rm -rf res_mods/


