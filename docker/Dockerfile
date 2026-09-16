FROM ubuntu:24.04

# time: o alvo mem dos Makefiles chama /usr/bin/time -v, que o embutido do shell nao aceita.
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       ca-certificates curl wget gnupg lsb-release software-properties-common \
       build-essential make git sudo time \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ARG CLANG_VERSION=19
RUN curl -sSf https://apt.llvm.org/llvm.sh -o /tmp/llvm.sh \
    && bash /tmp/llvm.sh ${CLANG_VERSION} \
    && rm -f /tmp/llvm.sh \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# libomp: necessaria para -fopenmp com clang.
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       libomp-${CLANG_VERSION}-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# binary-trees (apr-1), pidigits (gmp) e regex-redux (boost_regex).
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       libapr1-dev libgmp-dev libboost-regex-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ARG PYTHON_VERSION=3.12.6
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
       libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev lzma lzma-dev \
       tk-dev uuid-dev zlib1g-dev pkg-config \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN wget --no-verbose https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz \
    && tar -xJf Python-${PYTHON_VERSION}.tar.xz \
    && cd Python-${PYTHON_VERSION} \
    && ./configure --enable-optimizations --with-lto \
    && make -j"$(nproc)" && make install \
    && cd .. && rm -rf Python-${PYTHON_VERSION} Python-${PYTHON_VERSION}.tar.xz

# gmpy2 (pidigits), memory_profiler (alvo memtotal), lazyme (compile_all.py).
RUN python3 -m pip install --no-cache-dir --break-system-packages \
       gmpy2 memory_profiler lazyme

RUN clang++-${CLANG_VERSION} --version | head -1 \
    && python3 --version \
    && python3 -c "import gmpy2, memory_profiler, lazyme; print('pacotes Python ok')" \
    && /usr/bin/time --version

WORKDIR /repo/pereira
CMD ["/bin/bash"]
