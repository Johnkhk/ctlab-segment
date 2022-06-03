# FROM ubuntu:focal
FROM nvidia/opengl:1.0-glvnd-devel-ubuntu20.04

RUN apt-get -qq update && apt-get -qq -y install curl bzip2 \
    && curl -sSL https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -bfp /usr/local \
    && rm -rf /tmp/miniconda.sh \
    && conda install -y python=3 \
    && conda update conda \
    && apt-get -qq -y remove curl bzip2 \
    && apt-get -qq -y autoremove \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* /var/log/dpkg.log \
    && conda clean --all --yes

ENV PATH /opt/conda/bin:$PATH

WORKDIR /workspace

# Install mamba
RUN conda install -n base -c conda-forge mamba

COPY env.yml .

RUN conda create -n ct_vis python=3.8
RUN mamba env update -n ct_vis -f env.yml

# Add activate to ~/.bashrc
RUN echo ". /usr/local/etc/profile.d/conda.sh">>~/.bashrc && \
    echo "conda activate ct_vis" >> ~/.bashrc

CMD ["bash"]
