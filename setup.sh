#!/bin/bash

# Set UTF-8 encoding
export PYTHONUTF8=1

# Install Miniconda (replace with the appropriate URL for your platform)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda
rm miniconda.sh

# Update conda and create a Conda environment
export PATH="$HOME/miniconda/bin:$PATH"
conda update -n base -c defaults conda
conda env create -f environment.yml

# Activate the Conda environment
source $HOME/miniconda/etc/profile.d/conda.sh
conda activate eco-tech-h2gam

# Install your Conda dependencies
conda install --yes --file environment.yml

# (Optional) Install additional Python dependencies using pip
pip install -r requirements.txt

# Your other setup commands go here

# Create Streamlit config files
mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"ludovic.giraud@essec.edu\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
