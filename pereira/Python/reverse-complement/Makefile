PYTHON = python3
RAPL ?= ../../RAPL-powercap/main

compile:
	cp revcomp.python3-6.python3 revcomp.python3-6.py
measure:
	sudo -E $(RAPL) "$(PYTHON) -OO revcomp.python3-6.py 0 < ../../revcomp-input25000000.txt" Python reverse-complement

run:
	$(PYTHON) -OO revcomp.python3-6.py 0 < ../../revcomp-input25000000.txt

mem:
	/usr/bin/time -v $(PYTHON) -OO revcomp.python3-6.py 0 < ../../revcomp-input25000000.txt


memtotal:
	mprof run -o mprofile-reverse-complement.dat $(PYTHON) -OO revcomp.python3-6.py 0 < ../../revcomp-input25000000.txt
