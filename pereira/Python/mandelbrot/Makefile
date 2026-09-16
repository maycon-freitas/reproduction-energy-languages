PYTHON = python3
RAPL ?= ../../RAPL-powercap/main

compile:
	cp mandelbrot.python3-7.python3 mandelbrot.python3-7.py
measure:
	sudo -E $(RAPL) "$(PYTHON) -OO mandelbrot.python3-7.py 16000" Python mandelbrot

run:
	$(PYTHON) -OO mandelbrot.python3-7.py 16000

mem:
	/usr/bin/time -v $(PYTHON) -OO mandelbrot.python3-7.py 16000

memtotal:
	mprof run -o mprofile-mandelbrot.dat $(PYTHON) -OO mandelbrot.python3-7.py 16000
