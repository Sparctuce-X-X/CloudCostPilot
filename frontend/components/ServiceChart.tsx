"use client";

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

interface Props {
  services: { name: string; cost: number }[];
}

export default function ServiceChart({ services }: Props) {
  return (
    <div className="bg-white rounded-xl p-6 border border-[#E0E7FF]">
      <h2 className="text-lg font-semibold text-[#1E1B4B] mb-1">Répartition par service</h2>
      <p className="text-sm text-[#475569] mb-4">Coûts détaillés par service AWS</p>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={services} layout="vertical" margin={{ left: 120 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E0E7FF" />
          <XAxis
            type="number"
            tickFormatter={(v) => `$${v}`}
            tick={{ fontSize: 11, fill: "#475569" }}
            stroke="#E0E7FF"
          />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fontSize: 12, fill: "#475569" }}
            width={110}
            stroke="#E0E7FF"
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#fff",
              border: "1px solid #E0E7FF",
              borderRadius: "8px",
              fontSize: "13px",
            }}
            formatter={(v) => `$${Number(v).toFixed(2)}`}
          />
          <Bar dataKey="cost" fill="#6366F1" radius={[0, 6, 6, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
