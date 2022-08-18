# syntax=docker/dockerfile:1
ARG BASE_REGISTRY=mcr.microsoft.com \
    BASE_IMAGE=vscode/devcontainers/base \
    BASE_TAG=ubuntu-22.04

FROM ${BASE_REGISTRY}/${BASE_IMAGE}:${BASE_TAG} as base
USER root
ENV DEBIAN_FRONTEND=noninteractive
# install runtime requirements
SHELL ["/bin/bash","-c"]
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
    # [VENV && PIP]
    python3.10-venv python3-pip=22.0.2+dfsg-1 \
    # [GEOS && PROJ && GDAL] needed for cartopy
    libgeos-dev=3.10.2-1 libproj-dev=8.2.1-1 libgdal-dev=3.4.1+dfsg-1build4 \
    && rm -rf /var/lib/apt/lists/*
# 
# 
# 
FROM base as builder
USER root
ENV PATH="/opt/venv/bin:$PATH"
ENV DEBIAN_FRONTEND=noninteractive
# install tools needed to compile cartopy
SHELL ["/bin/bash","-c"]
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
    python3-dev \
    build-essential \
    # osgeo -> cartopy
    proj-bin=8.2.1-1 \
    gdal-bin=3.4.1+dfsg-1build4 \
    # ecCode -> cfgrib 
    cmake   \
    gfortran \ 
    && rm -rf /var/lib/apt/lists/*
# COMPILE ECCODES FOR CFGRIB
ARG ECCODES="eccodes-2.24.2-Source" \
    ECCODES_DIR="/usr/include/eccodes"
WORKDIR /tmp
# download and extract the ecCodes archive
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN wget -c --progress=dot:giga \
        https://confluence.ecmwf.int/download/attachments/45757960/${ECCODES}.tar.gz  -O - | tar -xz -C . --strip-component=1 
# hop into the build directory 
WORKDIR /tmp/build
# install the ecCodes
RUN cmake -DCMAKE_INSTALL_PREFIX="${ECCODES_DIR}" -DENABLE_PNG=ON .. \
    && make \
    && make install

ENV ECCODES_DIR=$ECCODES_DIR
# for docker caching purpose last install requirements
RUN python3 -m venv /opt/venv \
    && pip install --upgrade pip \
    && pip install wheel 
    
COPY requirements.txt .
COPY requirements-dev.txt .

RUN pip install -r requirements.txt \
    && pip install -r requirements-dev.txt
# 
# 
# 
FROM base as final
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG ECCODES_DIR="/usr/include/eccodes"
# set PATH and copy the virtual env
ENV PATH="/opt/venv/bin:$PATH"
ENV ECCODES_DIR=$ECCODES_DIR
COPY --chown=$USERNAME:$USER_GID --from=builder /opt/venv /opt/venv
COPY --chown=$USERNAME:$USER_GID --from=builder $ECCODES_DIR $ECCODES_DIR

USER $USERNAME

