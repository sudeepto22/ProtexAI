from typing import List

from pydantic import BaseModel, Field

CRITICAL_THRESHOLD = 80


class CPUMetrics(BaseModel):
    usage_percent: float = Field(..., description="Overall CPU usage percentage")
    usage_per_core: List[float] = Field(..., description="CPU usage per core")
    frequency_mhz: float | None = Field(
        None, description="Current CPU frequency in MHz"
    )
    cores_physical: int | None = Field(None, description="Number of physical cores")
    cores_logical: int | None = Field(None, description="Number of logical cores")

    def __repr__(self) -> str:
        return f"{self.usage_percent}% ({self.cores_physical}P/{self.cores_logical}L cores)"


class GPUMetrics(BaseModel):
    name: str = Field(..., description="GPU name/model")
    load_percent: float = Field(..., description="GPU load percentage")
    memory_used_gb: float = Field(..., description="GPU memory used in GB")
    memory_total_gb: float = Field(..., description="Total GPU memory in GB")
    memory_usage_percent: float = Field(..., description="GPU memory usage percentage")
    temperature_c: float = Field(..., description="GPU temperature in Celsius")

    def __repr__(self) -> str:
        if not self.name:
            return "N/A"
        return f"{self.name} (Load={self.load_percent}% Memory={self.memory_usage_percent}%)"


class RAMMetrics(BaseModel):
    total_gb: float = Field(..., description="Total RAM in GB")
    available_gb: float = Field(..., description="Available RAM in GB")
    used_gb: float = Field(..., description="Used RAM in GB")
    usage_percent: float = Field(..., description="RAM usage percentage")

    def __repr__(self) -> str:
        return f"{self.used_gb}/{self.total_gb}GB ({self.usage_percent}%)"


class DiskMetrics(BaseModel):
    total_gb: float = Field(..., description="Total disk space in GB")
    used_gb: float = Field(..., description="Used disk space in GB")
    free_gb: float = Field(..., description="Free disk space in GB")
    usage_percent: float = Field(..., description="Disk usage percentage")

    def __repr__(self) -> str:
        return f"{self.used_gb}/{self.total_gb}GB ({self.usage_percent}%)"


class TemperatureSensor(BaseModel):
    label: str = Field(..., description="Sensor label/name")
    temperature_c: float = Field(..., description="Current temperature in Celsius")

    def __repr__(self) -> str:
        if not self.label:
            return "N/A"
        return f"{self.label} ({self.temperature_c}°C)"


class SystemMetrics(BaseModel):
    timestamp: str = Field(..., description="Timestamp in ISO format")
    platform: str = Field(..., description="Operating system platform")
    cpu: CPUMetrics = Field(..., description="CPU metrics")
    gpu: List[GPUMetrics] | None = Field(None, description="GPU metrics")
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

    def _set_alert(self, threshold: int) -> dict[str, float]:
        alert = {}
        if self.cpu.usage_percent > threshold:
            alert["cpu"] = self.cpu.usage_percent
        if self.gpu[0].load_percent > threshold if self.gpu else False:
            alert["gpu"] = self.gpu[0].load_percent if self.gpu else 0.0
        if self.ram.usage_percent > threshold:
            alert["ram"] = self.ram.usage_percent
        if self.disk.usage_percent > threshold:
            alert["disk"] = self.disk.usage_percent

        for temp in self.temperature if self.temperature else []:
            if temp.temperature_c > threshold:
                alert[f"{temp.label}_temp"] = temp.temperature_c

        return alert

    def is_critical(self) -> dict[str, float] | None:
        alert = self._set_alert(CRITICAL_THRESHOLD)
        if alert:
            return alert
