export const getUsageColor = (percent?: number): string => {
  if (!percent) return "text-slate-500";
  if (percent > 80) return "text-red-600";
  if (percent > 60) return "text-yellow-600";
  return "text-green-600";
};
