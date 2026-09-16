PYTHON = python3
RAPL ?= ../../RAPL-powercap/main

compile:
	cp binarytrees.python3 binarytrees.py
measure:
	sudo -E $(RAPL) "$(PYTHON) -OO binarytrees.py 21" Python binary-trees

run:
	$(PYTHON) -OO binarytrees.py 21

mem:
	/usr/bin/time -v $(PYTHON) -OO binarytrees.py 21

memtotal:
	mprof run -o mprofile-binary-trees.dat $(PYTHON) -OO binarytrees.py 21
