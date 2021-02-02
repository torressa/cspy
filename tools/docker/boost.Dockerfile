FROM ubuntu:rolling as builder

RUN apt-get update -qq && \
 apt-get install -yq wget build-essential openssh-client python3 python3-pip

RUN wget "https://cmake.org/files/v3.18/cmake-3.18.1-Linux-x86_64.sh" \
&& chmod a+x cmake-3.18.1-Linux-x86_64.sh \
&& ./cmake-3.18.1-Linux-x86_64.sh --prefix=/usr/local/ --skip-license \
&& rm cmake-3.18.1-Linux-x86_64.sh


RUN wget -O boost_1_75_0.tar.gz http://sourceforge.net/projects/boost/files/boost/1.75.0/boost_1_75_0.tar.gz/download && \
 tar xzvf boost_1_75_0.tar.gz && \
 cd boost_1_75_0 && \
 ./bootstrap.sh --exec-prefix=/usr/local --with-python=python3 && \
 ./b2 threading=multi && \
 ./b2 install threading=multi && \
 cd .. && \
 rm boost_1_75_0.tar.gz && \
 rm -r boost_1_75_0 && \
 ln -s /usr/lib/x86_64-linux-gnu/libboost_python-py34.so /usr/lib/x86_64-linux-gnu/libboost_python3.so

WORKDIR /root/
COPY . .
RUN mv tools/docker/scripts/run_boost . \
&& chmod +x run_boost
