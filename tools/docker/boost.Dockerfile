FROM ubuntu:rolling as builder

ENV PATH=/usr/local/bin:$PATH
RUN apt-get update -qq \
&& apt-get install -yq wget build-essential openssh-client git \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN wget "https://cmake.org/files/v3.18/cmake-3.18.1-Linux-x86_64.sh" \
&& chmod a+x cmake-3.18.1-Linux-x86_64.sh \
&& ./cmake-3.18.1-Linux-x86_64.sh --prefix=/usr/local/ --skip-license \
&& rm cmake-3.18.1-Linux-x86_64.sh

RUN wget -O boost_1_75_0.tar.gz \
 http://sourceforge.net/projects/boost/files/boost/1.75.0/boost_1_75_0.tar.gz/download \
&& tar xzvf boost_1_75_0.tar.gz \
&& cd boost_1_75_0 \
&& ./bootstrap.sh --exec-prefix=/usr/local --without-libraries=python \
&& ./b2 threading=multi \
&& ./b2 install threading=multi \
&& cd .. \
&& rm boost_1_75_0.tar.gz \
&& rm -r boost_1_75_0

ARG BENCHMARK_TESTS
ENV BENCHMARK_TESTS ${BENCHMARK_TESTS:-false}

WORKDIR /root/
COPY . .
RUN mv tools/docker/scripts/run_boost . \
&& chmod +x run_boost
