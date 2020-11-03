FROM ubuntu:rolling AS builder

ENV PATH=/usr/local/bin:$PATH
RUN apt-get update -qq \
&& apt-get install -yq \
	git wget libssl-dev build-essential swig python3-dev python3-pip \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install CMake 3.18.1
RUN wget "https://cmake.org/files/v3.18/cmake-3.18.1-Linux-x86_64.sh" \
&& chmod a+x cmake-3.18.1-Linux-x86_64.sh \
&& ./cmake-3.18.1-Linux-x86_64.sh --prefix=/usr/local/ --skip-license \
&& rm cmake-3.18.1-Linux-x86_64.sh
CMD [ "/usr/bin/bash" ]

FROM builder AS dev

ARG	BUILD_DOCS
ARG	BUILD_CLEAN
ARG	BUILD_RELEASE

ENV BENCHMARK_TESTS ${BENCHMARK_TESTS:-false}
ENV BUILD_DOCS ${BUILD_DOCS:-false}
ENV BUILD_CLEAN ${BUILD_CLEAN:-false}
ENV BUILD_PYTHON ${BUILD_PYTHON:-true}
ENV BUILD_RELEASE ${BUILD_RELEASE:-false}

WORKDIR /root/
COPY . .
RUN mv tools/docker/scripts/run_tests .
