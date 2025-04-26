# Makefile for SDL3 project
SRC_DIR = src
BUILD_DIR = build/debug
CC = g++
SRC_FILES = $(wildcard $(SRC_DIR)/*.cpp)
OBJ_NAME = play
INCLUDE_PATHS = -Iinclude
LIBRARY_PATHS = -L/usr/local/lib
COMPILER_FLAGS = -std=c++11 -Wall -O0 -g
LINKER_FLAGS = -lsdl3

all:
	$(CC) $(COMPILER_FLAGS) $(LINKER_FLAGS) $(INCLUDE_PATHS) $(LIBRARY_PATHS) $(SRC_FILES) -o $(BUILD_DIR)/$(OBJ_NAME)

# Run the program
run: all
	./$(BUILD_DIR)/$(OBJ_NAME)

# Clean build files
clean:
	rm -rf $(BUILD_DIR)

# Allow `make` to be executed without arguments
.PHONY: all run clean
