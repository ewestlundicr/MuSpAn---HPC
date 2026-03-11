# MuSpAn Templates to be run on HPC
This repository contains scripts to run Muspan-based neighbourhood analysis on spatial single-cell data using an AlmaLinux HPC environment (SLURM).

# First Time Setup

## Step 1 - Connect to Alma and run an interactive node:
```bash
ssh alma.icr.ac.uk
srun -p interactive --time 4:00:00 --cpus-per-task=4 --pty bash
```

## Step 2 - Navigate to scratch or RDS directory where you would like to run the scripts

```bash
cd /path/to/where/to/run/script
```

## Step 3 - Clone the repository and navigate to it:

```bash
git clone git@github.com:ewestlundicr/MuSpAn---HPC.git
cd MuSpAn---HPC
```
Confirm the repository is correctly cloned by writing

```bash
ls
```

and check that the 'run_clustering.sh' and 'run_muspan.py' exists.

## Step 4 - Create a MuSpAn env and install all required packages

```bash
conda create -n muspan_env python=3.10 -y
conda activate muspan_env
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4* - (Alma first-time users) – Set up Conda/Mamba once for all

```bash
module use /opt/software/easybuild/modules/all
module load Mamba 
```

Initiate Conda

```bash
conda init 
```

Reload your .bashrc file

```bash
source ~/.bashrc
```

Try step 4 again.

## Step 5 - Find the script you want to run
Current options are 
- Neighbourhood
Find a set number of neighbourhoods over your domains
- Proximity
Find the distance between cells of certain types over your domains

Go to the README for each pipeline inside the directories.

---

# Suggested Workflow After Initial Setup

## Step 1 - Connect to Alma and run an interactive node:
```bash
ssh alma.icr.ac.uk
srun -p interactive --time 4:00:00 --cpus-per-task=4 --pty bash
```

## Step 2 - Navigate to scratch or RDS directory where the git repo and environment exist

```bash
cd /path/to/MuSpAn---HPC
```

## Optional Step 3 - Pull latest version from repo 
If you want the latest version of the repo, do this step. 
### WARNING
Pulling will overwrite the current state of 'run_clustering.sh' and 'run_muspan.py'. Skip this step if you want to run the script the same as last time, or remember to update the newest version if you pull.

```bash
git pull
```

## Step 4 - Find the script you want to run
Follow the instructions from the README in each respective directory.
