#!/bin/bash

# Set UTF-8 encoding
export PYTHONUTF8=1

# Install Miniconda (replace with the appropriate URL for your platform)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda
rm miniconda.sh

# Add Miniconda to the PATH and initialize conda
export PATH="$HOME/miniconda/bin:$PATH"
conda init bash

# Update conda and create a Conda environment
conda update -n base -c defaults conda
conda env create -f environment.yml

# Activate the Conda environment
conda activate eco-tech-h2gam

conda install --yes --file environment.yml

# Install your Conda dependencies (replace with your actual dependencies)

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
