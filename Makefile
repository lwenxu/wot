#!/bin/make -f

.PHONY: all clean install 

wotdir = wot
wotver = 0.9.17.0.3
wotmod = res_mods/$(wotver)/scripts/client/gui/mods

all:
	python -m compileall mod_*.py

clean:
	rm *.pyc

install: all
	mkdir -p "$(wotdir)/$(wotmod)"
	cp -f mod_auto_equip.pyc mod_fast_repair.pyc mod_target.pyc "$(wotdir)/$(wotmod)"

