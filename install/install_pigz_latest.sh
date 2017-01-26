#!/usr/bin/env bash


# mkdir -p /opt/pigz && cd /opt/pigz && wget "http://zlib.net/zlib-1.2.8.tar.gz" && tar xvf  zlib-1.2.8.tar.gz && rm zlib-1.2.8.tar.gz && cd zlib-1.2.8 && ./configure && make &&  make install

cd /tmp
wget http://www.zlib.net/pigz/pigz-2.3.3.tar.gz
tar xvf  pigz-2.3.3.tar.gz
rm pigz-2.3.3.tar.gz

cd pigz-2.3.3
#fix pigz's makefile
cat Makefile | sed 's/$(CC) $(LDFLAGS) -o pigz $^ -lpthread -lm/$(CC) -o pigz $^ -lpthread -lm $(LDFLAGS)/' > Makefile2
make --file=Makefile2

sudo cp pigz unpigz /usr/bin
