#!/bin/sh



echo "############ 安装基础依赖 ############"

apt-get update && apt-get install -y --no-install-recommends \
        cmake \
        git \
        wget \
        curl \
        python-dev \
        python-pip \
        vim


echo "############ 安装anaconda ############"

curl -so /miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
&& chmod +x /miniconda.sh \
&& /miniconda.sh -b -p /miniconda \
&& rm /miniconda.sh

PATH=/miniconda/bin:$PATH



echo "############ 设置时区 ############"

ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime


echo "############ 设置编码 ############"

LANG C.UTF-8 LC_ALL=C.UTF-8


