#!/usr/bin/env bash
#Useful arguments:
# -c Build for computer (not RPI)
# -d Build with debug symbols. < non-function right now :( >
#handle arguments:
DEBF=""
RPI=true
while test $# -gt 0
do
    case "$1" in
        "-d") DEBF="$DEBF -DCMAKE_BUILD_TYPE=DEBUG"
        ;;
        "-c") RPI=false
        ;;
    esac
    shift
done
#echo "test"
mkdir -p build
cd build
cmake "-DBUILD_RPI=$RPI" "$DEBF" -B. -H..
#=true
#-DCMAKE_CXX_FLAGS="CMAKE_CXX_FLAGS -std=c++11"
make