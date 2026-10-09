"""
remote_runner.py

Synchronous SSH runner for executing Python scripts on the Windows COMSOL machine.
Copies the script to the remote Windows drive, runs it, copies results back.

Usage
-----
    python scripts/remote_runner.py scripts/phononic_band.py

    # Install mph on the remote machine (one-time setup):
    python scripts/remote_runner.py --setup

Setup checklist (one-time, on the Windows machine)
---------------------------------------------------
1. Fill in REMOTE_HOST and REMOTE_DIR below.
2. Ensure SSH key auth works:
       ssh -i ~/.ssh/id_ed25519 REMOTE_HOST
3. Install mph and matplotlib:
       run: python scripts/remote_runner.py --setup
   Or manually on the Windows machine:
       py -3.12 -m pip install mph matplotlib numpy
4. COMSOL must be installed; mph finds it automatically via the Windows registry.

Results (.npz, .png) are written to REMOTE_DIR by the script and pulled to ./results/.
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

# =============================================================================
# SSH / REMOTE CONFIG  -- fill these in before first use
# =============================================================================

REMOTE_HOST = 'USERNAME@HOST'                           # e.g. 'alice@192.168.1.10'
SSH_KEY     = os.path.expanduser('~/.ssh/id_ed25519')   # local private key path
REMOTE_DIR  = r'C:\Users\USERNAME\Documents\optomechanics'  # <-- fill in username
PYTHON_CMD  = 'py -3.12'

# =============================================================================

LOCAL_RESULTS = Path(__file__).parent.parent / 'results'


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
    """Pull files matching remote_glob back to local_dir."""
    os.makedirs(local_dir, exist_ok=True)
    cmd = ['scp', '-i', SSH_KEY, '-o', 'StrictHostKeyChecking=no',
           f'{REMOTE_HOST}:{remote_glob}', str(local_dir)]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        print(f'  scp pull warning (may be no matching files): {result.stderr.decode()}')


def setup_remote():
    """Install Python dependencies on the remote machine."""
    print('Creating remote directory...')
    ssh(f'if not exist "{REMOTE_DIR}" mkdir "{REMOTE_DIR}"')

    print('Installing Python dependencies on remote machine...')
    rc = ssh(f'{PYTHON_CMD} -m pip install mph matplotlib numpy')
    if rc != 0:
        print('WARNING: pip install exited with a non-zero code. Check output above.')
    else:
        print('Dependencies installed successfully.')

    print('Verifying mph can find COMSOL...')
    out, err, rc = ssh(f'{PYTHON_CMD} -c "import mph; c = mph.start(); c.clear(); print(\'mph OK\')"',
                       capture=True)
    if rc == 0 and 'mph OK' in out:
        print('mph + COMSOL: OK')
    else:
        print('mph/COMSOL check failed. stdout:', out.strip())
        print('stderr:', err.strip())
        print('Make sure COMSOL is installed on the remote machine.')


def run_remote_script(script_path: str):
    script_path = Path(script_path)
    if not script_path.exists():
        print(f'ERROR: script not found: {script_path}')
        sys.exit(1)

    remote_script  = REMOTE_DIR + '\\' + script_path.name
    local_configs  = Path(__file__).parent.parent / 'configs'
    remote_configs = REMOTE_DIR + r'\configs'

    print(f'[1/4] Creating remote directories...')
    ssh(f'if not exist "{REMOTE_DIR}" mkdir "{REMOTE_DIR}"')
    if local_configs.exists():
        ssh(f'if not exist "{remote_configs}" mkdir "{remote_configs}"')

    print(f'[2/4] Copying {script_path.name} to Windows...')
    scp_to(script_path, remote_script)
    if local_configs.exists():
        for cfg_file in local_configs.glob('*.json'):
            scp_to(cfg_file, remote_configs + '\\' + cfg_file.name)
            print(f'       + configs/{cfg_file.name}')

    print(f'[3/4] Running script on Windows (this may take a long time)...')
    rc = ssh(f'cd "{REMOTE_DIR}" && {PYTHON_CMD} "{script_path.name}"')
    if rc != 0:
        print(f'WARNING: remote script exited with code {rc}')

    print(f'[4/4] Pulling results back...')
    for ext in ('*.npz', '*.png', '*.mat', '*.csv'):
        scp_from(REMOTE_DIR + '\\' + ext, LOCAL_RESULTS)
    print(f'Results in: {LOCAL_RESULTS}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a script remotely on the COMSOL Windows machine')
    parser.add_argument('script', nargs='?', help='Path to the local Python script to run')
    parser.add_argument('--setup', action='store_true',
                        help='Install Python dependencies on the remote machine')
    args = parser.parse_args()

    if args.setup:
        setup_remote()
    elif args.script:
        run_remote_script(args.script)
    else:
        parser.print_help()
