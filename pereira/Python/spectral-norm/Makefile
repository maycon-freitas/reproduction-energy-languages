PYTHON = python3
RAPL ?= ../../RAPL-powercap/main

compile:
	cp spectralnorm.python3-5.python3 spectralnorm.python3-5.py
measure:
	sudo -E $(RAPL) "$(PYTHON) -OO spectralnorm.python3-5.py 5500" Python spectral-norm

run:
	$(PYTHON) -OO spectralnorm.python3-5.py 5500

mem:
	/usr/bin/time -v $(PYTHON) -OO spectralnorm.python3-5.py 5500

memtotal:
	mprof run -o mprofile-spectral-norm.dat $(PYTHON) -OO spectralnorm.python3-5.py 5500
