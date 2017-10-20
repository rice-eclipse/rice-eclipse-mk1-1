#!/usr/bin/env bash
cd build
#Uses g++ because it doesn't seem to build right with default.
#May want to investigate compiler later.
cmake -B. -H.. -DCMAKE_CXX_COMPILER=g++
make