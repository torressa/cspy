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
ENV BUILD_DOTNET ${BUILD_DOTNET:-false}

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
# Boost vars (1.78 doesn't work)
ENV BOOST_VERSION 1.75.0
ENV BOOST_VERSION_UNDERSCORE 1_75_0

# Install boost
RUN wget -O boost_${BOOST_VERSION_UNDERSCORE}.tar.gz \
 http://sourceforge.net/projects/boost/files/boost/${BOOST_VERSION}/boost_${BOOST_VERSION_UNDERSCORE}.tar.gz/download \
&& tar xzvf boost_${BOOST_VERSION_UNDERSCORE}.tar.gz \
&& cd boost_${BOOST_VERSION_UNDERSCORE} \
&& ./bootstrap.sh --exec-prefix=/usr/local --without-libraries=python \
&& ./b2 threading=multi \
&& ./b2 install threading=multi \
&& cd .. \
&& rm boost_${BOOST_VERSION_UNDERSCORE}.tar.gz \
&& rm -r boost_${BOOST_VERSION_UNDERSCORE}

WORKDIR /root/
COPY . .
RUN mv tools/docker/scripts/run_tests . \
&& chmod +x run_tests
