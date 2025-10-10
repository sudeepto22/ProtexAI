import React, { useState, useEffect } from "react";
import mqtt, { MqttClient } from "mqtt";
import { Card, CardContent, CardHeader, CardTitle } from "./components/ui/card";
import MetricCard from "./components/MetricCard";
import { getUsageColor } from "./lib/color";

interface SystemMetrics {
  timestamp: string;
  platform: string;
  cpu: {
    usage_percent: number;
    cores_physical: number;
    cores_logical: number;
    frequency_mhz: number;
  };
  gpu: Array<{
    load_percent: number;
    memory_usage_percent: number;
    temperature_c: number | null;
  }> | null;
  ram: {
    total_gb: number;
    used_gb: number;
    usage_percent: number;
  };
  disk: {
    total_gb: number;
    used_gb: number;
    usage_percent: number;
  };
  temperature: Array<{
    label: string;
    temperature_c: number;
  }> | null;
}

function App() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [connected, setConnected] = useState(false);
  const [history, setHistory] = useState<SystemMetrics[]>([]);

  useEffect(() => {
    const brokerUrl =
      process.env.REACT_APP_MQTT_BROKER || "ws://localhost:9001";
    const topic = process.env.REACT_APP_MQTT_TOPIC || "protexai/sensors";

    const client: MqttClient = mqtt.connect(brokerUrl, {
      clientId: `ui-consumer-${Math.random().toString(16).slice(2, 10)}`,
    });

    client.on("connect", () => {
      setConnected(true);
      client.subscribe(topic);
    });

    client.on("message", (_topic: string, message: Buffer) => {
      try {
        const data: SystemMetrics = JSON.parse(message.toString());

        setMetrics(data);
        setHistory((prev) => [data, ...prev].slice(0, 10));
      } catch (err) {
        console.error("Error parsing message:", err);
      }
    });

    client.on("error", (err) => {
      console.error("MQTT error:", err);
      setConnected(false);
    });

    client.on("close", () => {
      setConnected(false);
    });

    return () => {
      client.end();
    };
  }, []);

  const getTempMap = (
    temps: SystemMetrics["temperature"]
  ): Record<string, number> => {
    const tempMap: Record<string, number> = {};
    if (!temps || temps.length === 0) return tempMap;

    temps.forEach((temp) => {
      tempMap[temp.label] = temp.temperature_c;
    });

    return tempMap;
  };

  if (!connected) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Card className="w-96">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
              <span>Connecting to MQTT broker...</span>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Card className="w-96">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>Waiting for metrics...</span>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const tempMap = getTempMap(metrics.temperature);
  const cpuTemp = tempMap["CPU"];
  const ssdTemp = tempMap["SSD"];

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-slate-900">
              System Monitor
            </h1>
            <p className="text-slate-600 mt-1">{metrics.platform}</p>
          </div>
          <div className="flex items-center space-x-2 text-sm text-slate-600">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>Connected</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="CPU"
            value={metrics.cpu.usage_percent}
            details={`${metrics.cpu.cores_physical}P / ${metrics.cpu.cores_logical}L cores`}
            temperature={cpuTemp}
            progressColor="bg-blue-500"
          />
          <MetricCard
            title="RAM"
            value={metrics.ram.usage_percent}
            details={`${metrics.ram.used_gb.toFixed(
              1
            )} / ${metrics.ram.total_gb.toFixed(1)} GB`}
            progressColor="bg-purple-500"
          />
          <MetricCard
            title="Disk"
            value={metrics.disk.usage_percent}
            details={`${metrics.disk.used_gb.toFixed(
              1
            )} / ${metrics.disk.total_gb.toFixed(1)} GB`}
            temperature={ssdTemp}
            progressColor="bg-orange-500"
          />
          <MetricCard
            title="GPU"
            value={metrics.gpu?.[0]?.load_percent}
            details={
              metrics.gpu?.[0]
                ? `Memory: ${metrics.gpu?.[0]?.memory_usage_percent}%`
                : null
            }
            temperature={metrics.gpu?.[0]?.temperature_c}
            progressColor="bg-pink-500"
          />
        </div>

        <div className="text-center text-sm text-slate-500">
          Last updated: {new Date(metrics.timestamp).toLocaleString()}
        </div>

        {history.length > 1 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Recent Metrics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2 px-4 font-medium text-slate-600">
                        Time
                      </th>
                      <th className="text-left py-2 px-4 font-medium text-slate-600">
                        CPU %
                      </th>
                      <th className="text-left py-2 px-4 font-medium text-slate-600">
                        RAM %
                      </th>
                      <th className="text-left py-2 px-4 font-medium text-slate-600">
                        Disk %
                      </th>
                      {history[0].gpu && (
                        <th className="text-left py-2 px-4 font-medium text-slate-600">
                          GPU %
                        </th>
                      )}
                    </tr>
                  </thead>
                  <tbody>
                    {history.slice(0, 5).map((item, idx) => (
                      <tr
                        key={idx}
                        className="border-b last:border-0 hover:bg-slate-50"
                      >
                        <td className="py-2 px-4 text-slate-700">
                          {new Date(item.timestamp).toLocaleTimeString()}
                        </td>
                        <td className="py-2 px-4">
                          <span
                            className={getUsageColor(item.cpu.usage_percent)}
                          >
                            {item.cpu.usage_percent}%
                          </span>
                        </td>
                        <td className="py-2 px-4">
                          <span
                            className={getUsageColor(item.ram.usage_percent)}
                          >
                            {item.ram.usage_percent}%
                          </span>
                        </td>
                        <td className="py-2 px-4">
                          <span
                            className={getUsageColor(item.disk.usage_percent)}
                          >
                            {item.disk.usage_percent}%
                          </span>
                        </td>
                        {item.gpu && (
                          <td className="py-2 px-4">
                            <span
                              className={getUsageColor(
                                item.gpu[0].load_percent
                              )}
                            >
                              {item.gpu[0].load_percent}%
                            </span>
                          </td>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

export default App;
