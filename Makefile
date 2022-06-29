PWD := $(shell pwd)
KVERSION := $(shell uname -r)

SRC := $(notdir $(wildcard $(M)/*.c))

OBJ := $(SRC:%.c=%.o)

TAR_FILES := $(wildcard *.c) Makefile $(wildcard *.py)

obj-m := $(OBJ)

all:
	echo modules $(obj-m)
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) modules

clean:
	rm -f *.ko *.mod* *.o modules.order Module.symvers

tar:
	tar cvfJ ec-drivers.tar.xz Makefile $(TAR_FILES) 
