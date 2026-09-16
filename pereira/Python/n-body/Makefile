PYTHON = python3
RAPL ?= ../../RAPL-powercap/main

compile:
	cp nbody.python3 nbody.py
measure:
	sudo -E $(RAPL) "$(PYTHON) -OO nbody.py 50000000" Python n-body

run:
	$(PYTHON) -OO nbody.py 50000000

mem:
	/usr/bin/time -v $(PYTHON) -OO nbody.py 50000000

memtotal:
	mprof run -o mprofile-n-body.dat $(PYTHON) -OO nbody.py 50000000
