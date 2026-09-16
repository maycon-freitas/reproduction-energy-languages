CXX = clang++-19
RAPL ?= ../../RAPL-powercap/main

compile:
	$(CXX) -c -pipe -O3 -fomit-frame-pointer -march=native  -std=c++14 -g pidigits.gpp-4.c++ -o pidigits.gpp-4.c++.o &&  $(CXX) pidigits.gpp-4.c++.o -o pidigits.gpp-4.gpp_run -lgmp -lgmpxx 
measure:
	sudo -E $(RAPL) "./pidigits.gpp-4.gpp_run 10000" C++ pidigits

run:
	./pidigits.gpp-4.gpp_run 10000

mem:
	/usr/bin/time -v ./pidigits.gpp-4.gpp_run 10000

valgrind:
	valgrind --tool=massif --stacks=yes ./pidigits.gpp-4.gpp_run 10000

memtotal:
	mprof run -o mprofile-pidigits.dat ./pidigits.gpp-4.gpp_run 10000
