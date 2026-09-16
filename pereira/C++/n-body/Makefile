CXX = clang++-19
RAPL ?= ../../RAPL-powercap/main

compile:
	$(CXX) -c -pipe -O3 -fomit-frame-pointer -march=native -mfpmath=sse -msse3 --std=c++11 nbody.gpp-8.c++ -o nbody.gpp-8.c++.o &&  $(CXX) nbody.gpp-8.c++.o -o nbody.gpp-8.gpp_run -fopenmp
measure:
	sudo -E $(RAPL) "./nbody.gpp-8.gpp_run 50000000" C++ n-body

run:
	./nbody.gpp-8.gpp_run 50000000

mem:
	/usr/bin/time -v ./nbody.gpp-8.gpp_run 50000000

valgrind:
	valgrind --tool=massif --stacks=yes ./nbody.gpp-8.gpp_run 50000000



memtotal:
	mprof run -o mprofile-n-body.dat ./nbody.gpp-8.gpp_run 50000000
