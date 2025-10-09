import psutil
import platform
from datetime import datetime
import subprocess
from sensor.model import (
    CPUMetrics,
    GPUMetrics,
    RAMMetrics,
    DiskMetrics,
    TemperatureSensor,
    SystemMetrics
)

def get_cpu_usage() -> CPUMetrics:
    cpu_percent_total = psutil.cpu_percent(interval=5)
    cpu_percent_per_core = psutil.cpu_percent(interval=5, percpu=True)
    cpu_freq = psutil.cpu_freq()
    cpu_count_physical = psutil.cpu_count(logical=False)
    cpu_count_logical = psutil.cpu_count(logical=True)
    
    return CPUMetrics(
        usage_percent=cpu_percent_total,
        usage_per_core=cpu_percent_per_core,
        frequency_mhz=round(cpu_freq.current, 2) if cpu_freq else None,
        cores_physical=cpu_count_physical,
        cores_logical=cpu_count_logical
    )

def get_gpu_usage() -> list[GPUMetrics] | None:
    try:
        command = r'''rocm-smi --showuse --showmeminfo vram --showtemp --json'''
        
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0 or not result.stdout.strip():
            return None
        
        return None
        
    except Exception:
        return None

def get_ram_usage() -> RAMMetrics:
    mem = psutil.virtual_memory()
    
    return RAMMetrics(
        total_gb=round(mem.total / (1024**3), 2),
        available_gb=round(mem.available / (1024**3), 2),
        used_gb=round(mem.used / (1024**3), 2),
        usage_percent=mem.percent
    )

def get_disk_usage() -> DiskMetrics:
    disk = psutil.disk_usage('/')
    
    return DiskMetrics(
        total_gb=round(disk.total / (1024**3), 2),
        used_gb=round(disk.used / (1024**3), 2),
        free_gb=round(disk.free / (1024**3), 2),
        usage_percent=disk.percent
    )


def get_temperature() -> dict[str, list[TemperatureSensor]] | None:
    if platform.system() == 'Linux':
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                formatted_temps = []
                for name, entries in temps.items():
                    formatted_temps.extend(
                        [
                            TemperatureSensor(
                                label=entry.label or name,
                                current_c=entry.current,
                                high_c=entry.high if entry.high else None,
                                critical_c=entry.critical if entry.critical else None
                            ) 
                            for entry in entries
                        ]
                    )
                return formatted_temps
        except AttributeError:
            pass
    return None

def get_system_metrics() -> SystemMetrics:
    return SystemMetrics(
        timestamp=datetime.now().isoformat(),
        platform=platform.system(),
        cpu=get_cpu_usage(),
        gpu=get_gpu_usage(),
        ram=get_ram_usage(),
        disk=get_disk_usage(),
        temperature=get_temperature()
    )