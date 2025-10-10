import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

interface MetricCardProps {
  title: string;
  value: number;
  unit?: string;
  details: string[];
  temperature?: number | null;
  progressColor?: string;
  getUsageColor: (percent: number) => string;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit = "%",
  details,
  temperature,
  progressColor = "bg-blue-500",
  getUsageColor,
}) => {
  return (
    <Card className="flex flex-col justify-between">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-slate-600">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className={`text-3xl font-bold ${getUsageColor(value)}`}>
          {value}
          {unit}
        </div>
        {details.map((detail, idx) => (
          <p key={idx} className="text-xs text-slate-500 mt-2">
            {detail}
          </p>
        ))}
        {temperature && (
          <p className="text-xs text-slate-500 mt-1">
            Temperature: {temperature.toFixed(1)}°C
          </p>
        )}
      </CardContent>
      <div className="w-full h-2 bg-slate-200 overflow-hidden">
        <div
          className={`h-full ${progressColor} transition-all duration-500`}
          style={{ width: `${value}%` }}
        />
      </div>
    </Card>
  );
};

export default MetricCard;
