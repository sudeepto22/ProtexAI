import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { getUsageColor } from "../lib/color";

interface MetricCardProps {
  title: string;
  value?: number;
  details?: string | null;
  temperature?: number | null;
  progressColor?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  details,
  temperature,
  progressColor = "bg-blue-500",
}) => {
  return (
    <Card className="flex flex-col justify-between">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-slate-600">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {value !== undefined ? (
          <div className={`text-3xl font-bold ${getUsageColor(value)}`}>
            {value}%
          </div>
        ) : (
          <div className="text-3xl font-bold text-slate-500">N/A</div>
        )}
        {details && <p className="text-xs text-slate-500 mt-2">{details}</p>}
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
