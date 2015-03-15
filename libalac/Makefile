LIBALAC=../contrib/alac/codec
CFLAGS=-I$(LIBALAC) -Wno-multichar -fPIC -O2 -s
CXXFLAGS=$(CFLAGS)

libalac.so: libalac.o $(patsubst %.cpp,%.o,$(wildcard $(LIBALAC)/*.cpp)) $(patsubst %.c,%.o,$(wildcard $(LIBALAC)/*.c))
	$(LINK.cc) -shared $^ -Wl,--version-script=exports -o $@

clean:
	rm -f *.o $(LIBALAC)/*.o *.so

.PHONY: clean
