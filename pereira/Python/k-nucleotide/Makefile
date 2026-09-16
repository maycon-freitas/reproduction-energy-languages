PYTHON = python3
RAPL ?= ../../RAPL-powercap/main

compile:
	cp knucleotide.python3-3.python3 knucleotide.python3-3.py
measure:
	sudo -E $(RAPL) "$(PYTHON) -OO knucleotide.python3-3.py 0 < ../../knucleotide-input25000000.txt" Python k-nucleotide

run:
	$(PYTHON) -OO knucleotide.python3-3.py 0 < ../../knucleotide-input25000000.txt

mem:
	/usr/bin/time -v $(PYTHON) -OO knucleotide.python3-3.py 0 < ../../knucleotide-input25000000.txt

memtotal:
	mprof run -o mprofile-k-nucleotide.dat $(PYTHON) -OO knucleotide.python3-3.py 0 < ../../knucleotide-input25000000.txt
