# Muspan Neighbourhood Analysis (HPC)
This repository contains scripts to run Muspan-based neighbourhood analysis on spatial single-cell data using an AlmaLinux HPC environment (SLURM).

## Step 1 - Connect to Alma and run an interactive node:
```bash
ssh alma.icr.ac.uk
srun -p interactive --time 4:00:00 --cpus-per-task=4 --pty bash
```

Navigate to your scratch or RDS directory where you would like to run the scripts

## Step 2 - Clone the repository:
```bash
git clone git@github.com:ewestlundicr/MuSpAn---HPC.git
cd MuSpAn---HPC
```

## Step 3 - Create a Muspan env if not already done, and install all required packages

Note that you only need to do this step once
```bash
conda create -n muspan_env python=3.10 -y
conda activate muspan_env
pip install --upgrade pip
pip install -r requirements.txt
```

# Step 4 - Edit the `run_clustering.sh` script to specify the input and output directories
```bash
python run_muspan.py \
  --inputs /path/to/input_csvs \
  --output /path/to/output_directory
```
* `Inputs`: directory on Alma containing CSV files with cell coordinates and labels
* `Output`: directory on Alma where results (JSON, plots, domains) will be written

# Step 5 - Submit the job to HPC
Start by making the script executable
```bash 
chmod +x run_clustering.sh
```

Then, run the job
```bash 
sbatch run_clustering.sh
```

# Outputs
The pipeline generates:
* Neighbourhood enrichment matrices (.json)
* Elbow plot (elbow_plot.jpg)
* Neighbourhood heatmap (heatmap.jpg)
* Saved Muspan domains
* CSV exports of domains
All outputs are written to the `specified output directory`.