import os
import subprocess
import time
import json
import traceback
import sys
from pathlib import Path
from provenance import now, sha256

def run_lacuna_analysis_b(input_pdb: Path, output_dir: Path) -> dict:
    started_at = now()
    start_time = time.perf_counter()
    command_argv = []
    
    result = {
        'status': 'FAILED',
        'started_at': started_at,
        'command_argv': command_argv,
        'input_sha256': sha256(input_pdb) if input_pdb.exists() else None,
        'stdout': '',
        'stderr': '',
        'runtime': None,
        'return_code': None,
        'outputs': {}
    }
    
    try:
        import lacuna
        from lacuna.ensemble.nma_backend import NMABackend
        
        result['tool_version'] = getattr(lacuna, '__version__', 'unknown')
        if result['tool_version'] != '1.2.0':
            raise RuntimeError(f"Required lacuna_pockets version 1.2.0, found {result['tool_version']}")
            
        backend = NMABackend(cutoff=8.0, n_modes=10, max_rmsd=2.0, seed=42)
        if type(backend).__name__ == 'RandomBackend':
            raise RuntimeError("NMABackend fell back to RandomBackend silently.")
            
        lacuna_exe = Path(sys.executable).parent / 'lacuna.exe' if os.name == 'nt' else Path(sys.executable).parent / 'lacuna'
        
        command_argv = [
            str(lacuna_exe), 'discover',
            str(input_pdb),
            '--conformers', '20',
            '--detector', 'alpha',
            '--rank-by', 'learned',
            '--no-sequence',
            '--output', str(output_dir)
        ]
        result['command_argv'] = command_argv
        
        process_res = subprocess.run(command_argv, capture_output=True, text=True, check=False)
        result['stdout'] = process_res.stdout
        result['stderr'] = process_res.stderr
        result['return_code'] = process_res.returncode
        
        if 'alling back' in process_res.stdout or 'alling back' in process_res.stderr or 'Falling back' in process_res.stdout or 'Falling back' in process_res.stderr:
            raise RuntimeError("Lacuna silently fell back.")
            
        if process_res.returncode == 0:
            result['status'] = 'SUCCESS'
            pocket_report = output_dir / 'pocket_report.json'
            if pocket_report.exists():
                with open(pocket_report, 'r') as pr:
                    pr_data = json.load(pr)
                if pr_data.get('ranked_by') != 'learned':
                    raise RuntimeError(f"Expected ranked_by=learned, got {pr_data.get('ranked_by')}")
            for out_file in output_dir.iterdir():
                if out_file.is_file():
                    result['outputs'][out_file.name] = sha256(out_file)
        else:
            result['status'] = 'FAILED'
            result['error'] = f"Lacuna exited with code {process_res.returncode}"
    except Exception as e:
        result['error'] = str(e)
        result['traceback'] = traceback.format_exc()
        
    result['finished_at'] = now()
    result['runtime'] = time.perf_counter() - start_time
    return result

def run_p2rank_analysis_b(p2rank_sh: Path, input_pdb: Path, output_dir: Path) -> dict:
    started_at = now()
    start_time = time.perf_counter()
    
    command_argv = [
        str(p2rank_sh), 'predict',
        '-f', str(input_pdb),
        '-o', str(output_dir),
        '-threads', '1',
        '-seed', '42',
        '-visualizations', '0'
    ]
    
    result = {
        'status': 'FAILED',
        'started_at': started_at,
        'command_argv': command_argv,
        'command': ' '.join(command_argv),
        'input_sha256': sha256(input_pdb) if input_pdb.exists() else None,
        'stdout': '',
        'stderr': '',
        'runtime': None,
        'return_code': None,
        'outputs': {}
    }
    
    try:
        java_exe = Path(os.getcwd()) / 'jdk-21.0.2' / 'bin' / 'java.exe'
        if not java_exe.exists():
            raise RuntimeError(f"Pinned Java runtime not found at {java_exe}")
            
        env = os.environ.copy()
        env['JAVA_HOME'] = str(Path(os.getcwd()) / 'jdk-21.0.2')
        env['PATH'] = str(java_exe.parent) + os.pathsep + env.get('PATH', '')
        
        java_res = subprocess.run([str(java_exe), '-version'], env=env, capture_output=True, text=True, check=False)
        if '21.' not in java_res.stderr:
            raise RuntimeError(f"Unexpected Java version: {java_res.stderr.splitlines()[0]}")
            
        process_res = subprocess.run(command_argv, env=env, capture_output=True, text=True, check=False)
        result['stdout'] = process_res.stdout
        result['stderr'] = process_res.stderr
        result['return_code'] = process_res.returncode
        
        if process_res.returncode == 0:
            predictions_csv = output_dir / f"{input_pdb.name}_predictions.csv"
            if predictions_csv.exists():
                with open(predictions_csv, 'r') as f:
                    lines = f.readlines()
                    if len(lines) < 1:
                        raise RuntimeError("Empty predictions.csv")
                result['status'] = 'SUCCESS'
                for out_file in output_dir.iterdir():
                    if out_file.is_file():
                        result['outputs'][out_file.name] = sha256(out_file)
            else:
                raise RuntimeError("predictions.csv not found")
        else:
            result['status'] = 'FAILED'
            result['error'] = f"P2Rank exited with code {process_res.returncode}"
            
    except Exception as e:
        result['error'] = str(e)
        result['traceback'] = traceback.format_exc()
        
    result['finished_at'] = now()
    result['runtime'] = time.perf_counter() - start_time
    return result
