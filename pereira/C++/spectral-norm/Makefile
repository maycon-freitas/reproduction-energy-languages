CXX = clang++-19
RAPL ?= ../../RAPL-powercap/main

compile:
	$(CXX) -c -pipe -O3 -fomit-frame-pointer -march=native -mfpmath=sse -msse2 -fopenmp -mfpmath=sse -msse2 spectralnorm.gpp-6.c++ -o spectralnorm.gpp-6.c++.o &&  $(CXX) spectralnorm.gpp-6.c++.o -o spectralnorm.gpp-6.gpp_run -fopenmp
measure:
	sudo -E $(RAPL) "./spectralnorm.gpp-6.gpp_run 5500" C++ spectral-norm

run:
	./spectralnorm.gpp-6.gpp_run 5500

mem:
	/usr/bin/time -v ./spectralnorm.gpp-6.gpp_run 5500

valgrind:
	valgrind --tool=massif --stacks=yes ./spectralnorm.gpp-6.gpp_run 5500

memtotal:
	mprof run -o mprofile-spectral-norm.dat ./spectralnorm.gpp-6.gpp_run 5500
