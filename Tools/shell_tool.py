import subprocess

def execute_command(command: str) -> str:
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        parts = [f"Exit code: {result.returncode}"]
        if result.stdout:
            parts.append(f"STDOUT:\n{result.stdout.strip()[:8000]}")
        if result.stderr:
            parts.append(f"STDERR:\n{result.stderr.strip()[:8000]}")
        return "\n\n".join(parts)
    except subprocess.TimeoutExpired:
        return "Error: el comando excedió el tiempo límite (30s)."
    except Exception as e:
        return f"Error ejecutando comando: {e}"
