#!/bin/make -f

.PHONY: all clean tags install release

sources = $(wildcard mod_*.c)
targets = $(sources:.py=.pyc)

WOTDIR = ./wot
wotver = 0.9.10
wotmod = res_mods/$(wotver)
wotmod_scripts = $(wotmod)/scripts/client/gui/mods
wotmod_configs = $(wotmod)/scripts/client/gui/mods

all: $(targets)

	python -m compileall mod_*.py

clean:

	rm *.pyc

tags:

	ctags -R -n --totals=yes

install: all

	cp -f mod_*.pyc $(WOTDIR)/$(wotmod_scripts)
	cp -f mod_*.xml $(WOTDIR)/$(wotmod_configs)
	cp -rf res/* $(WOTDIR)/$(wotmod)

release: all

	mkdir -p $(wotmod_scripts)
	cp -vf mod_*.pyc $(wotmod_scripts)
	cp -rvf res/* $(wotmod)
	tar cv res_mods/ | bzip2 -c -9 > wotmods-$(wotver).tar.bz2
	rm -rf res_mods/ 

