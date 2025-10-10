from typing import List

from pydantic import BaseModel, Field


class CPUMetrics(BaseModel):
    usage_percent: float = Field(..., description="Overall CPU usage percentage")
    usage_per_core: List[float] = Field(..., description="CPU usage per core")
    frequency_mhz: float | None = Field(
        None, description="Current CPU frequency in MHz"
    )
    cores_physical: int | None = Field(None, description="Number of physical cores")
    cores_logical: int | None = Field(None, description="Number of logical cores")


class GPUMetrics(BaseModel):
    name: str = Field(..., description="GPU name/model")
    load_percent: float = Field(..., description="GPU load percentage")
    memory_used_gb: float = Field(..., description="GPU memory used in GB")
    memory_total_gb: float = Field(..., description="Total GPU memory in GB")
    memory_usage_percent: float = Field(..., description="GPU memory usage percentage")
    temperature_c: float = Field(..., description="GPU temperature in Celsius")


class RAMMetrics(BaseModel):
    total_gb: float = Field(..., description="Total RAM in GB")
    available_gb: float = Field(..., description="Available RAM in GB")
    used_gb: float = Field(..., description="Used RAM in GB")
    usage_percent: float = Field(..., description="RAM usage percentage")


class DiskMetrics(BaseModel):
    total_gb: float = Field(..., description="Total disk space in GB")
    used_gb: float = Field(..., description="Used disk space in GB")
    free_gb: float = Field(..., description="Free disk space in GB")
    usage_percent: float = Field(..., description="Disk usage percentage")


class TemperatureSensor(BaseModel):
    label: str = Field(..., description="Sensor label/name")
    current_c: float = Field(..., description="Current temperature in Celsius")
    high_c: float | None = Field(None, description="High threshold in Celsius")
    critical_c: float | None = Field(None, description="Critical threshold in Celsius")


class SystemMetrics(BaseModel):
    timestamp: str = Field(..., description="Timestamp in ISO format")
    platform: str = Field(..., description="Operating system platform")
    cpu: CPUMetrics = Field(..., description="CPU metrics")
    gpu: List[GPUMetrics] | None = Field(None, description="GPU metrics (NVIDIA/AMD)")
    ram: RAMMetrics = Field(..., description="RAM metrics")
    disk: DiskMetrics = Field(..., description="Disk metrics")
    temperature: List[TemperatureSensor] | None = Field(
        None, description="Temperature sensors (Linux only)"
    )

    def to_json(self) -> str:
        return self.model_dump_json()

    @classmethod
    def from_json(cls, json_str: str) -> "SystemMetrics":
        return cls.model_validate_json(json_str)

    def to_dict(self) -> dict:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "SystemMetrics":
        return cls.model_validate(data)
