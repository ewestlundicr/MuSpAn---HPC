# Muspan Nearest Neighbour Analysis (HPC)
This repository contains scripts to run Muspan-based nearest neighbour analysis on spatial single-cell data using an AlmaLinux HPC environment (SLURM).

# Make sure you have done step 1-4 for the initial start-up, or 1-3 if you have used this script before

## Step 1 - Navigate to the muspan-neighbourhood directory
Run
```bash 
cd muspan-nearestneighbour
```
and run
```bash 
ls
```
to see the two scripts "muspan-hpc_nearestneighbour.py" and "run_nearestneighbour.sh"

## Step 2 - Edit the `run_nearestneighbour.sh` script to specify the input and output directories

Open the 'run_nearestneighbour.sh' script in the editor
```bash
vi run_nearestneighbour.sh
```

Click 'i' on the keyboard to initiate editing mode. Update the --input and --output paths.
* `Inputs`: directory on Alma containing MuSpAn domains with cell coordinates and labels
* `Output`: directory on Alma where results (csv file of domains with nearest neighbour distances) will be written
* `classes_csv`: path to a csv file containing two columns for Class A and Class B. The smallest distance will be measured from Class A to each type in Class B individually.

### Example:


| Class A | Class B |
|----------|----------|
| Cancer   |      Fibroblast    |
|    |      T Cell    |
|   |  Endothelial       |

* The headers need to be called "Class A" and "Class B", case sensitive
* Only one cell type in Class A
* Multiple cell types in Class B

This will calculate the minimum distance between cells of type
* Cancer -> Fibroblast
* Cancer -> T Cell
* Cancer -> Endothelial 

Click 'esc' on the keyboard to leave editing mode. 

Close the vi-viewer by writing ':wq' and press enter on the keyboard.

## Step 3 - Make the script executable 

```bash 
chmod +x run_nearestneighbour.sh
```

Confirm that it is executable by running
```bash
ls
```
and check that 'run_nearestneighbour.sh' is green.

## Step 4 - Submit the job to HPC

```bash 
sbatch run_nearestneighbour.sh
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
* CSV exports of the domains with the shortest distance for specified cells as a column
All outputs are written to the `specified output directory`.
