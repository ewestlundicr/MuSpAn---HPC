# Muspan Neighbourhood Analysis (HPC)
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


## Step 5 - Edit the `run_clustering.sh` script to specify the input and output directories

Open the 'run_clustering.sh' script in the editor
```bash
vi run_clustering.sh
```

Click 'i' on the keyboard to initiate editing mode. Update the --input and --output paths.
* `Inputs`: directory on Alma containing CSV files with cell coordinates and labels
* `Output`: directory on Alma where results (JSON, plots, domains) will be written

Click 'esc' on the keyboard to leave editing mode. 

Close the vi-viewer by writing ':wq' and press enter on the keyboard.


## Step 6 - Make the script executable 

```bash 
chmod +x run_clustering.sh
```

Confirm that it is executable by running
```bash
ls
```
and check that 'run_clustering.sh' is green.

## Step 7 - Submit the job to HPC

```bash 
sbatch run_clustering.sh
```

## Step 8 - Check status

```bash 
squeue -u $USER
```
Can be run multiple times while script is running.

An error and output file will be created if the script fails. Run
```bash 
ls
```
to see it in your repo folder. View the error file by running
```bash 
vi muspan_JOB_ID.err
```
where JOB_ID is unique to the current job.

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

## Recommended Step 4 - Check/update --input and --output directories

```bash
vi run_clustering.sh
```

Click 'i' on the keyboard to initiate editing mode. Update the --input and --output paths.
* `Inputs`: directory on Alma containing CSV files with cell coordinates and labels
* `Output`: directory on Alma where results (JSON, plots, domains) will be written


## Step 5 - Make the script executable 
Check if 'run_clustering.sh' is already executable. Write

```bash
ls
```
and check if 'run_clustering.sh' is green.

If not green, run
```bash 
chmod +x run_clustering.sh
```

## Step 6 - Submit the job to HPC

```bash 
sbatch run_clustering.sh
```

## Step 7 - Check status

```bash 
squeue -u $USER
```
---


# Outputs
The pipeline generates:
* Neighbourhood enrichment matrices (.json)
* Elbow plot (elbow_plot.jpg)
* Neighbourhood heatmap (heatmap.jpg)
* Saved Muspan domains
* CSV exports of domains
All outputs are written to the `specified output directory`.
