PYTHON = python3
RAPL ?= ../../RAPL-powercap/main

compile:
	cp pidigits.python3-2.python3 pidigits.python3-2.py
measure:
	sudo -E $(RAPL) "$(PYTHON) -OO pidigits.python3-2.py 10000" Python pidigits

run:
	$(PYTHON) -OO pidigits.python3-2.py 10000
mem:
	/usr/bin/time -v $(PYTHON) -OO pidigits.python3-2.py 10000

memtotal:
	mprof run -o mprofile-pidigits.dat $(PYTHON) -OO pidigits.python3-2.py 10000
