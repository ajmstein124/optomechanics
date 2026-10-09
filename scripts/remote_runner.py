"""
remote_runner.py

SSH runner for executing Python or MATLAB scripts on the Windows COMSOL machine.
Copies the script to the remote Windows drive, runs it, copies results back.

Usage
-----
    # Run a MATLAB script:
    python scripts/remote_runner.py scripts/reproduce_Si_Mech_band.m

    # Run a Python script:
    python scripts/remote_runner.py scripts/some_script.py

    # Copy the .mph model file to the remote machine (one-time, large file):
    python scripts/remote_runner.py --copy-model scripts/unit_cell_3.mph

    # Verify SSH + MATLAB + COMSOL are working:
    python scripts/remote_runner.py --check

Setup checklist (one-time)
--------------------------
1. Fill in REMOTE_HOST, REMOTE_DIR, and MATLAB_CMD below.
2. Ensure SSH key auth works:
       ssh -i ~/.ssh/id_ed25519 REMOTE_HOST
3. Copy the .mph model file (one-time -- 718 MB, slow):
       python scripts/remote_runner.py --copy-model scripts/unit_cell_3.mph
4. COMSOL LiveLink for MATLAB must be installed on the Windows machine.
   MATLAB must be in the Windows PATH (or set full path in MATLAB_CMD below).
5. Run the check:
       python scripts/remote_runner.py --check

Results (.mat, .jpg, .csv, .npz, .png) are pulled to ./results/ after each run.
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

# =============================================================================
# SSH / REMOTE CONFIG  -- fill these in before first use
# =============================================================================

REMOTE_HOST = 'jvadmin@171.64.85.12'
SSH_KEY     = os.path.expanduser('~/.ssh/id_ed25519')
REMOTE_DIR  = r'C:\Users\JVadmin\Documents\optomechanics'
PYTHON_CMD  = 'py -3.12'
MATLAB_CMD  = r'"C:\Program Files\MATLAB\R2024b\bin\matlab.exe"'

# =============================================================================

LOCAL_RESULTS = Path(__file__).parent.parent / 'results'
RESULT_EXTS   = ('*.mat', '*.jpg', '*.csv', '*.npz', '*.png')


def ssh(cmd, capture=False):
    full = ['ssh', '-i', SSH_KEY, '-o', 'StrictHostKeyChecking=no', REMOTE_HOST, cmd]
    if capture:
        r = subprocess.run(full, capture_output=True, text=True)
        return r.stdout, r.stderr, r.returncode
    else:
        r = subprocess.run(full)
        return r.returncode


def scp_to(local_path, remote_path):
    cmd = ['scp', '-i', SSH_KEY, '-o', 'StrictHostKeyChecking=no',
           str(local_path), f'{REMOTE_HOST}:{remote_path}']
    subprocess.run(cmd, check=True)


def scp_from(remote_glob, local_dir):
    os.makedirs(local_dir, exist_ok=True)
    cmd = ['scp', '-i', SSH_KEY, '-o', 'StrictHostKeyChecking=no',
           f'{REMOTE_HOST}:{remote_glob}', str(local_dir)]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        print(f'  scp pull note (may be no matching files): {result.stderr.decode().strip()}')


def run_remote_script(script_path: str):
    script_path = Path(script_path)
    if not script_path.exists():
        print(f'ERROR: script not found: {script_path}')
        sys.exit(1)

    ext = script_path.suffix.lower()
    remote_script = REMOTE_DIR + '\\' + script_path.name

    print(f'[1/4] Creating remote directory...')
    ssh(f'if not exist "{REMOTE_DIR}" mkdir "{REMOTE_DIR}"')

    print(f'[2/4] Copying {script_path.name}...')
    scp_to(script_path, remote_script)

    print(f'[3/4] Running on Windows...')
    if ext == '.m':
        # Run MATLAB in batch mode from REMOTE_DIR so mphload finds the .mph file.
        # -batch runs the script headlessly and exits; stdout/stderr go to the SSH stream.
        script_name_no_ext = script_path.stem
        run_cmd = (f'cd /d "{REMOTE_DIR}" && '
                   f'{MATLAB_CMD} -batch "run(\'{script_name_no_ext}.m\')"')
    else:
        run_cmd = f'cd /d "{REMOTE_DIR}" && {PYTHON_CMD} "{script_path.name}"'

    rc = ssh(run_cmd)
    if rc != 0:
        print(f'WARNING: remote script exited with code {rc}')

    print(f'[4/4] Pulling results...')
    results_subdirs = [REMOTE_DIR + r'\simu_data']   # MATLAB scripts save here
    for subdir in results_subdirs:
        # Pull recursively by pulling from subdirectories matching simu_data\*
        scp_from(subdir + r'\*\*.mat', LOCAL_RESULTS)
        scp_from(subdir + r'\*\*.jpg', LOCAL_RESULTS)
    for ext_glob in RESULT_EXTS:
        scp_from(REMOTE_DIR + '\\' + ext_glob, LOCAL_RESULTS)
    print(f'Results in: {LOCAL_RESULTS}')


def copy_model(local_model_path: str):
    """Copy a large model file (.mph) to the remote machine. One-time operation."""
    p = Path(local_model_path)
    if not p.exists():
        print(f'ERROR: model file not found: {p}')
        sys.exit(1)
    remote_path = REMOTE_DIR + '\\' + p.name
    print(f'Creating remote directory...')
    ssh(f'if not exist "{REMOTE_DIR}" mkdir "{REMOTE_DIR}"')
    print(f'Copying {p.name} ({p.stat().st_size / 1e6:.0f} MB) -- this will take a while...')
    scp_to(p, remote_path)
    print(f'Model copied to {remote_path}')


def check_remote():
    """Verify SSH, MATLAB, and COMSOL LiveLink are working."""
    print('Checking SSH connection...')
    rc = ssh('echo SSH OK')
    if rc != 0:
        print('ERROR: SSH connection failed.')
        return

    print('Checking MATLAB...')
    out, err, rc = ssh(f'{MATLAB_CMD} -batch "disp(version); exit"', capture=True)
    if rc == 0:
        print(f'  MATLAB OK: {out.strip()[:80]}')
    else:
        print(f'  WARNING: MATLAB check failed (rc={rc})')
        print(f'  stdout: {out.strip()[:200]}')
        print(f'  stderr: {err.strip()[:200]}')
        print(f'  Is MATLAB in PATH? Try setting full path in MATLAB_CMD.')
        return

    print('Checking COMSOL LiveLink...')
    # Quick test: start a COMSOL server via mphstart (LiveLink function)
    test_script = 'mphstart; disp(\'LiveLink OK\'); exit'
    out, err, rc = ssh(f'{MATLAB_CMD} -batch "{test_script}"', capture=True)
    if rc == 0 and 'LiveLink OK' in out:
        print('  COMSOL LiveLink: OK')
    else:
        print(f'  WARNING: LiveLink check failed (rc={rc})')
        print(f'  stdout: {out.strip()[:200]}')
        print('  Make sure COMSOL LiveLink for MATLAB is installed.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run scripts remotely on the COMSOL Windows machine')
    parser.add_argument('script', nargs='?',
                        help='Path to .m or .py script to run')
    parser.add_argument('--copy-model', metavar='MODEL_FILE',
                        help='Copy a large .mph model file to the remote machine (one-time)')
    parser.add_argument('--check', action='store_true',
                        help='Verify SSH, MATLAB, and COMSOL LiveLink are working')
    args = parser.parse_args()

    if args.check:
        check_remote()
    elif args.copy_model:
        copy_model(args.copy_model)
    elif args.script:
        run_remote_script(args.script)
    else:
        parser.print_help()
