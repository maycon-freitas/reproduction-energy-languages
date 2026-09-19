FROM ubuntu:latest

VOLUME [ "/root/data" ]

# General.
RUN apt update \
    && DEBIAN_FRONTEND=noninteractive apt install -y tzdata \
    && apt install -y git cmake ninja-build sudo curl wget pkg-config gnupg \
    && apt clean && rm -rf /var/lib/apt/lists/*

COPY docker/keys /root/Energy-Languages/docker/keys
RUN gpg --import /root/Energy-Languages/docker/keys/*

# C++.
ARG CLANG_VERSION=19
RUN apt update \
    && apt install -y lsb-release wget software-properties-common gnupg \
    && curl -sSf https://apt.llvm.org/llvm.sh | bash -s -- ${CLANG_VERSION} all \
    && apt clean && rm -rf /var/lib/apt/lists/*
ENV CC=clang-${CLANG_VERSION}
ENV CXX=clang++-${CLANG_VERSION}
RUN ln -s /usr/bin/llvm-ar-${CLANG_VERSION} /usr/bin/llvm-ar
RUN ln -s /usr/bin/llvm-profdata-${CLANG_VERSION} /usr/bin/llvm-profdata

# C/C++ libraries.
RUN apt update \
    && apt install -y libapr1-dev libgmp-dev libpcre3-dev libboost-regex-dev \
    && apt clean && rm -rf /var/lib/apt/lists/*

# Python.
ARG PYTHON_VERSION=3.12.6
# https://devguide.python.org/getting-started/setup-building/index.html#build-dependencies
RUN apt update \
    && apt install -y build-essential gdb lcov pkg-config libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev lzma lzma-dev tk-dev uuid-dev zlib1g-dev \
    && apt clean && rm -rf /var/lib/apt/lists/*
RUN wget --no-verbose https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz \
    && wget --no-verbose https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz.asc \
    && gpg --verify Python-${PYTHON_VERSION}.tar.xz.asc Python-${PYTHON_VERSION}.tar.xz \
    && tar -xJf Python-${PYTHON_VERSION}.tar.xz \
    && cd Python-${PYTHON_VERSION} && ./configure --enable-optimizations --with-lto && make -j && make install && cd .. \
    && rm -rf Python-${PYTHON_VERSION}.tar.xz Python-${PYTHON_VERSION}.tar.xz.asc Python-${PYTHON_VERSION}

# Python dependencies.
RUN python3 -m pip install --upgrade pip
COPY benchmarks/Python/requirements.txt /root/Energy-Languages/
RUN python3 -m pip install -r /root/Energy-Languages/requirements.txt
COPY scripts/requirements.txt /root/Energy-Languages/
RUN python3 -m pip install -r /root/Energy-Languages/requirements.txt

WORKDIR /root/Energy-Languages
COPY fasta-5000000.txt fasta-5000000.txt
COPY fasta-25000000.txt fasta-25000000.txt
COPY benchmarks benchmarks
COPY experiments experiments
COPY scripts scripts
ENTRYPOINT [ "python3", "-m", "scripts.measure", "-o", "/root/data" ]
