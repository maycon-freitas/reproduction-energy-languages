CXX = clang++-19
RAPL ?= ../../RAPL-powercap/main

compile:
	$(CXX) -c -pipe -O3 -fomit-frame-pointer -march=native  -std=c++11 -fopenmp fannkuchredux.gpp-5.c++ -o fannkuchredux.gpp-5.c++.o &&  $(CXX) fannkuchredux.gpp-5.c++.o -o fannkuchredux.gpp-5.gpp_run -fopenmp 
measure:
	sudo -E $(RAPL) "./fannkuchredux.gpp-5.gpp_run 12" C++ fannkuch-redux

run:
	./fannkuchredux.gpp-5.gpp_run 12

mem:
	 /usr/bin/time -v  ./fannkuchredux.gpp-5.gpp_run 12
valgrind:
	valgrind --tool=massif --stacks=yes  ./fannkuchredux.gpp-5.gpp_run 12


memtotal:
	mprof run -o mprofile-fannkuch-redux.dat ./fannkuchredux.gpp-5.gpp_run 12
