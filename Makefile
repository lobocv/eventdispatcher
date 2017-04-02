CC=gcc

PYTHON_VERSION = 2.7
PYTHON_INCLUDE = /usr/include/python$(PYTHON_VERSION)

BOOST_LIB = /usr/local/boost_1_63_0/stage/lib
TARGET = eventdispatcher
SRC_DIR = eventdispatcher/src
OUTPUT_DIR = eventdispatcher/cpp


$(OUTPUT_DIR)/$(TARGET).so: $(OUTPUT_DIR)/$(TARGET).o
	$(CC) -shared -I BOOT_LIB -o $(OUTPUT_DIR)/$(TARGET).so $(OUTPUT_DIR)/$(TARGET).o -lpython2.7 -lboost_python


$(OUTPUT_DIR)/$(TARGET).o: 
	$(CC) -o $(OUTPUT_DIR)/$(TARGET).o -c $(SRC_DIR)/$(TARGET).cpp -Wall -fPIC -I$(PYTHON_INCLUDE)


clean:
	rm $(OUTPUT_DIR)/*
	touch $(OUTPUT_DIR)/__init__.py
