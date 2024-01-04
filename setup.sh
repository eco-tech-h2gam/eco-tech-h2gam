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

#!/bin/bash

# Install Miniconda (replace with the appropriate URL for your platform)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda
rm miniconda.sh

# Add Miniconda to the PATH
export PATH="$HOME/miniconda/bin:$PATH"

# Update conda and create a Conda environment
conda update -q conda
conda create -q -n eco-tech-h2gam python=3.8

# Activate the Conda environment
source activate eco-tech-h2gam

# Install your Conda dependencies (replace with your actual dependencies)
conda install -q regionmask cartopy cdsapi

# (Optional) Install additional Python dependencies using pip
pip install -r requirements.txt

# Your other setup commands go here


