FROM alpine:latest AS builder

ENV PATH=/usr/local/bin:$PATH
RUN apk add --no-cache git build-base linux-headers cmake wget

CMD [ "/bin/sh" ]

FROM builder AS dev

# Input arguments
ARG BENCHMARK_TESTS
ARG	BUILD_DOCS
ARG	BUILD_CLEAN

# Define environment variables (may differ from arguments)
ENV BENCHMARK_TESTS ${BENCHMARK_TESTS:-false}
ENV BUILD_DOCS ${BUILD_DOCS:-false}
ENV BUILD_CLEAN ${BUILD_CLEAN:-false}
ENV BUILD_RELEASE ${BUILD_RELEASE:-false}
ENV BUILD_PYTHON ${BUILD_PYTHON:-false}

WORKDIR /root/
COPY . .
RUN mv tools/docker/scripts/run_tests . \
&& chmod +x run_tests

FROM builder AS boost

# Input arguments
ARG BENCHMARK_TESTS
ARG	BUILD_DOCS
ARG	BUILD_CLEAN

# Define environment variables (may differ from arguments)
ENV BENCHMARK_TESTS ${BENCHMARK_TESTS:-false}
ENV BUILD_DOCS ${BUILD_DOCS:-false}
ENV BUILD_CLEAN ${BUILD_CLEAN:-false}
ENV BUILD_RELEASE ${BUILD_RELEASE:-false}
ENV BUILD_PYTHON ${BUILD_PYTHON:-false}

# Install boost
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

WORKDIR /root/
COPY . .
RUN mv tools/docker/scripts/run_tests . \
&& chmod +x run_tests
