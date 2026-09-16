PYTHON = python3
RAPL ?= ../../RAPL-powercap/main

compile:
	cp fasta.python3-3.python3 fasta.python3-3.py
measure:
	sudo -E $(RAPL) "$(PYTHON) -OO fasta.python3-3.py 25000000" Python fasta

run:
	$(PYTHON) -OO fasta.python3-3.py 25000000

make mem:
	/usr/bin/time -v  $(PYTHON) -OO fasta.python3-3.py 25000000

memtotal:
	mprof run -o mprofile-fasta.dat $(PYTHON) -OO fasta.python3-3.py 25000000
