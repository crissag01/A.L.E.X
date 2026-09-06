import os
import subprocess
import psutil

def open_program(program: str) -> str:
    try:
        os.startfile(program)
        return f"Abrí: {program}"
    except OSError:
        try:
            subprocess.Popen(program, shell=True)
            return f"Abrí: {program}"
        except Exception as e:
            return f"Error abriendo {program}: {e}"

def get_system_info() -> str:
    cpu = psutil.cpu_percent(interval=0.5)
    vm = psutil.virtual_memory()
    disk = psutil.disk_usage("C:\\")
    return (
        f"CPU: {cpu}%\n"
        f"RAM: {vm.used/(1024**3):.1f} / {vm.total/(1024**3):.1f} GB ({vm.percent}%)\n"
        f"Disco C: {disk.used/(1024**3):.1f} / {disk.total/(1024**3):.1f} GB ({disk.percent}%)"
    )
