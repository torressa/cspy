FROM quay.io/pypa/manylinux2014_x86_64 AS builder

ENV PATH=/usr/local/bin:$PATH

RUN yum install -y python3-devel wget

# Download and install SWIG from git
RUN git clone https://github.com/swig/swig.git --branch v4.0.2 \
&& cd swig && ./autogen.sh && ./configure \
&& make && make install && cd .. && rm -rf swig/

CMD [ "/usr/bin/bash" ]

FROM builder AS dev

# Input arguments
ARG BUILD_DOCS
ARG BUILD_CLEAN
ARG BUILD_RELEASE

# Define environment variables (may differ from arguments)
ENV BENCHMARK_TESTS ${BENCHMARK_TESTS:-false}
ENV BUILD_DOCS ${BUILD_DOCS:-false}
ENV BUILD_CLEAN ${BUILD_CLEAN:-false}
ENV BUILD_RELEASE ${BUILD_RELEASE:-false}
ENV BUILD_PYTHON ${BUILD_PYTHON:-true}

WORKDIR /root/
COPY . .
RUN mv tools/docker/scripts/* . \
&& chmod +x run_tests build_manylinux_wheels
