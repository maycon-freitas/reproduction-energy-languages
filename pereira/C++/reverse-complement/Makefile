CXX = clang++-19
RAPL ?= ../../RAPL-powercap/main

compile:
	$(CXX) -c -pipe -O3 -fomit-frame-pointer -march=native  -std=c++11 -mtune=native -mfpmath=sse -msse2 revcomp.gpp-4.c++ -o revcomp.gpp-4.c++.o &&  $(CXX) revcomp.gpp-4.c++.o -o revcomp.gpp-4.gpp_run -pthread 
measure:
	sudo -E $(RAPL) "./revcomp.gpp-4.gpp_run 0 < ../../revcomp-input25000000.txt" C++ reverse-complement

run:
	./revcomp.gpp-4.gpp_run 0 < ../../revcomp-input25000000.txt

mem:
	/usr/bin/time -v ./revcomp.gpp-4.gpp_run 0 < ../../revcomp-input25000000.txt

valgrind:
	valgrind --tool=massif --stacks=yes ./revcomp.gpp-4.gpp_run 0 < ../../revcomp-input25000000.txt

memtotal:
	mprof run -o mprofile-reverse-complement.dat ./revcomp.gpp-4.gpp_run 0 < ../../revcomp-input25000000.txt
