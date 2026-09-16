PYTHON = python3
RAPL ?= ../../RAPL-powercap/main

compile:
	cp fannkuchredux.python3-4.python3 fannkuchredux.python3-4.py
measure:
	sudo -E $(RAPL) "$(PYTHON) -OO fannkuchredux.python3-4.py 12" Python fannkuch-redux

run:
	$(PYTHON) -OO fannkuchredux.python3-4.py 12
mem:
	/usr/bin/time -v $(PYTHON) -OO fannkuchredux.python3-4.py 12

memtotal:
	mprof run -o mprofile-fannkuch-redux.dat $(PYTHON) -OO fannkuchredux.python3-4.py 12
