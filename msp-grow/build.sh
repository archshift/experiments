#!/bin/bash
msp430-elf-g++ -mmcu=msp430f5529 -g -I $(dirname $(which msp430-elf-g++))/../include main.cpp -o msp-grow
