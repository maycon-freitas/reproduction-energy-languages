PYTHON = python3
RAPL ?= ../../RAPL-powercap/main

compile:
	cp regexredux.python3 regexredux.py
measure:
	sudo -E $(RAPL) "$(PYTHON) -OO regexredux.py 0 < ../../regexredux-input5000000.txt" Python regex-redux

run:
	$(PYTHON) -OO regexredux.py 0 < ../../regexredux-input5000000.txt

mem:
	/usr/bin/time -v $(PYTHON) -OO regexredux.py 0 < ../../regexredux-input5000000.txt

memtotal:
	mprof run -o mprofile-regex-redux.dat $(PYTHON) -OO regexredux.py 0 < ../../regexredux-input5000000.txt
