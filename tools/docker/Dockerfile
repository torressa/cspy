FROM alpine:edge AS builder

ENV PATH=/usr/local/bin:$PATH
RUN apk add --no-cache git build-base linux-headers cmake swig
CMD [ "/bin/sh" ]

FROM builder AS dev

ARG BENCHMARK_TESTS
ARG	BUILD_DOCS
ARG	BUILD_CLEAN

ENV BENCHMARK_TESTS ${BENCHMARK_TESTS:-false}
ENV BUILD_DOCS ${BUILD_DOCS:-false}
ENV BUILD_CLEAN ${BUILD_CLEAN:-false}
ENV BUILD_PYTHON ${BUILD_PYTHON:-false}
ENV BUILD_RELEASE ${BUILD_RELEASE:-false}

WORKDIR /root/
COPY . .
RUN mv tools/docker/scripts/run_tests .
