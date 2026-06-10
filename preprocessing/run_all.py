"""
run_all.py - Runs all 7 preprocessing scripts in sequence
Usage: python preprocessing/run_all.py
"""
import subprocess, sys, os

scripts = [
    "politeness_prep.py",
    "tone_prep.py",
    "intent_prep.py",
    "pa_prep.py",
    "sarcasm_prep.py",
    "urgency_prep.py",
    "power_prep.py",
]

base = os.path.dirname(__file__)
for script in scripts:
    path = os.path.join(base, script)
    print(f"\n{'='*50}")
    print(f"Running {script}...")
    print('='*50)
    result = subprocess.run([sys.executable, path], capture_output=False)
    if result.returncode != 0:
        print(f"ERROR in {script} — returncode {result.returncode}")
    else:
        print(f"{script} completed successfully.")

print("\nAll preprocessing done. Check data/processed/ for output files.")
