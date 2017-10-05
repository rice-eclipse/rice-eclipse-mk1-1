#!/bin/bash
#Uses g++ because it doesn't seem to build right with default.
#May want to investigate compiler later.
cmake -Bbuild -H. -DCMAKE_CXX_COMPILER=g++
make -C build