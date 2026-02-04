import subprocess

# Step 1: generate CSVs
subprocess.run(["python", "abbr.py"])
subprocess.run(["python", "colors_data.py"])
subprocess.run(["python", "team_data.py"])

# Step 2: run model / generate model CSV
subprocess.run(["python", "ops-tracker.py"])

# Step 3: create database
subprocess.run(["python", "create_db.py"])

# Step 4: create plots
subprocess.run(["python", "plot.py"])