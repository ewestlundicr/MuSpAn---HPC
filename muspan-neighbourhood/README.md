# Muspan Neighbourhood Analysis (HPC)
This repository contains scripts to run Muspan-based neighbourhood analysis on spatial single-cell data using an AlmaLinux HPC environment (SLURM).

# Make sure you have done step 1-4 for the initial start-up, or 1-3 if you have used this script before

## Step 1 - Navigate to the muspan-neighbourhood directory
Run
```bash 
cd muspan-neighbourhood
```
and run
```bash 
ls
```
to see the two scripts "muspan-hpc_neighbourhood.py" and "run_neighbourhood.sh"

## Step 2 - Edit the `run_neighbourhood.sh` script to specify the input and output directories

Open the 'run_neighbourhood.sh' script in the editor
```bash
vi run_neighbourhood.sh
```

Click 'i' on the keyboard to initiate editing mode. Update the --input and --output paths.
* `Inputs`: directory on Alma containing CSV files with cell coordinates and labels
* `Output`: directory on Alma where results (JSON, plots, domains) will be written

Click 'esc' on the keyboard to leave editing mode. 

Close the vi-viewer by writing ':wq' and press enter on the keyboard.

## Step 3 - Make the script executable 

```bash 
chmod +x run_neighbourhood.sh
```

Confirm that it is executable by running
```bash
ls
```
and check that 'run_neighbourhood.sh' is green.

## Step 4 - Submit the job to HPC

```bash 
sbatch run_neighbourhood.sh
```

## Step 5 - Check status

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

# Outputs
The pipeline generates:
* Neighbourhood enrichment matrices (.json)
* Elbow plot (elbow_plot.jpg)
* Neighbourhood heatmap (heatmap.jpg)
* Saved Muspan domains
* CSV exports of domains
All outputs are written to the `specified output directory`.
