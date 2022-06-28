PWD := $(shell pwd)
KVERSION := $(shell uname -r)

SRC := $(notdir $(wildcard $(M)/*.c))

OBJ := $(SRC:%.c=%.o)

obj-m := $(OBJ)

all:
	echo modules $(obj-m)
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) modules

clean:
	rm -f *.ko *.mod* *.o

#make -C /lib/modules/$(KVERSION)/build M=$(PWD) SRC="$(SRC)" modules

