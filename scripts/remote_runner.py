"""
remote_runner.py

Synchronous SSH runner for executing Python scripts on the Windows COMSOL machine.
Copies the script to the remote Windows drive, runs it, copies results back.

Usage
-----
    python remote_runner.py scripts/phononic_band.py

The remote working directory is C:\\Users\\hopel\\Documents\\Abby\\optomechanics.
Results (.npz, .png) are written there by the script and pulled back to ./results/.
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

# ─── SSH / Remote config ──────────────────────────────────────────────────────
REMOTE_HOST = 'jvlab@100.68.160.53'
SSH_KEY     = os.path.expanduser('~/.ssh/id_ed25519')
REMOTE_DIR  = r'C:\Users\hopel\Documents\Abby\optomechanics'
PYTHON_CMD  = 'py -3.12'

LOCAL_RESULTS = Path(__file__).parent.parent / 'results'

# ─── Helpers ─────────────────────────────────────────────────────────────────

def ssh(cmd, capture=False):
    """Run a shell command on the remote Windows machine."""
    full = ['ssh', '-i', SSH_KEY, '-o', 'StrictHostKeyChecking=no', REMOTE_HOST, cmd]
    if capture:
        r = subprocess.run(full, capture_output=True, text=True)
        return r.stdout, r.stderr, r.returncode
    else:
        r = subprocess.run(full)
        return r.returncode


def scp_to(local_path, remote_path):
    """Copy a local file to the remote machine."""
    cmd = ['scp', '-i', SSH_KEY, '-o', 'StrictHostKeyChecking=no',
           str(local_path), f'{REMOTE_HOST}:{remote_path}']
    subprocess.run(cmd, check=True)


def scp_from(remote_glob, local_dir):
    """
    Pull files matching remote_glob back to local_dir.
    remote_glob uses Windows path + wildcard, e.g.
        C:\\path\\to\\dir\\phononic_band_*.npz
    """
    os.makedirs(local_dir, exist_ok=True)
    cmd = ['scp', '-i', SSH_KEY, '-o', 'StrictHostKeyChecking=no',
           f'{REMOTE_HOST}:{remote_glob}', str(local_dir)]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        print(f'  scp pull warning (may be no matching files): {result.stderr.decode()}')


# ─── Main ────────────────────────────────────────────────────────────────────

def run_remote_script(script_path: str):
    script_path = Path(script_path)
    if not script_path.exists():
        print(f'ERROR: script not found: {script_path}')
        sys.exit(1)

    remote_script = REMOTE_DIR + '\\' + script_path.name

    print(f'[1/4] Creating remote directory...')
    ssh(f'if not exist "{REMOTE_DIR}" mkdir "{REMOTE_DIR}"')

    print(f'[2/4] Copying {script_path.name} to Windows...')
    scp_to(script_path, remote_script)

    print(f'[3/4] Running script on Windows (this may take a long time)...')
    rc = ssh(f'cd "{REMOTE_DIR}" && {PYTHON_CMD} "{script_path.name}"')
    if rc != 0:
        print(f'WARNING: remote script exited with code {rc}')

    print(f'[4/4] Pulling results back...')
    for ext in ('*.npz', '*.png', '*.mat'):
        remote_glob = REMOTE_DIR + '\\' + ext
        scp_from(remote_glob, LOCAL_RESULTS)
    print(f'Results in: {LOCAL_RESULTS}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a script remotely on the COMSOL Windows machine')
    parser.add_argument('script', help='Path to the local Python script to run')
    args = parser.parse_args()
    run_remote_script(args.script)
