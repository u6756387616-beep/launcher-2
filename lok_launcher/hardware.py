import platform
import shutil
import subprocess
import psutil

def _gpu_name():
    if platform.system() == "Windows":
        try:
            out = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command",
                 "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name"],
                text=True, stderr=subprocess.DEVNULL, timeout=4
            )
            names = [x.strip() for x in out.splitlines() if x.strip()]
            return ", ".join(names[:2]) if names else "Nie wykryto"
        except Exception:
            return "Nie udało się odczytać"
    return "Sprawdź sterownik systemowy"

def scan_hardware():
    mem = psutil.virtual_memory()
    disk = shutil.disk_usage("/")
    return {
        "cpu": platform.processor() or platform.machine(),
        "cores": psutil.cpu_count(logical=False) or 1,
        "threads": psutil.cpu_count(logical=True) or 1,
        "ram_total": round(mem.total / 1024**3, 1),
        "ram_available": round(mem.available / 1024**3, 1),
        "gpu": _gpu_name(),
        "system": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "disk_free": round(disk.free / 1024**3, 1),
    }
