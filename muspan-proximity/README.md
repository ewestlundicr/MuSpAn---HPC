# Muspan Proximity Analysis (HPC)
This repository contains scripts to run Muspan-based proximity analysis on spatial single-cell data using an AlmaLinux HPC environment (SLURM).

# Make sure you have done step 1-4 for the initial start-up, or 1-3 if you have used this script before

## Step 1 - Navigate to the muspan-proximity directory
Run
```bash 
cd muspan-proximity
```
and run
```bash 
ls
```
to see the two scripts "muspan-hpc_proximity.py" and "run_proximity.sh"

## Step 2 - Edit the `run_proximity.sh` script to specify the arguments

Open the 'run_proximity.sh' script in the editor
```bash
vi run_proximity.sh
```

Click 'i' on the keyboard to initiate editing mode. Update the arguments.
* `Inputs`: directory on Alma containing muspan domain files
* `Output`: directory on Alma where results count arrays will be written
* `path_classes_to_investigate`: path to csv file containing the label and markers to use for the proximity analysis. The csv should have one column with the header being the name of the label in the muspan domain and the entries are the names of the categories you want to investigate in that label, e.g. header: "Phenotype", entries: "panCK", "CD8", "aSMA"
* `max_edge_distance`: integer to specify the max_edge_distance when generating the proximity network

* change the email for mail-user to get an email if the script errors

Click 'esc' on the keyboard to leave editing mode. 

Close the vi-viewer by writing ':wq' and press enter on the keyboard.

## Step 3 - Make the script executable 

```bash 
chmod +x run_proximity.sh
```

Confirm that it is executable by running
```bash
ls
```
and check that 'run_proximity.sh' is green.

## Step 4 - Submit the job to HPC

```bash 
sbatch run_proximity.sh
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
* Count arrays for each individual domain (.npy)
* Total array, with and without connections with itself (.npy)
* Normalised total array, with and without connections to itself (.npy)
All outputs are written to the `specified output directory`.
