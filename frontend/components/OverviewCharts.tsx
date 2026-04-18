"use client";

import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from "recharts";

const COLORS = ["#6366F1", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"];

interface Props {
  dailyCosts: { date: string; cost: number }[];
  teamData: { team: string; total: number }[];
}

export default function OverviewCharts({ dailyCosts, teamData }: Props) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
      <div className="bg-white rounded-xl p-4 md:p-6 border border-[#E0E7FF]">
        <h2 className="text-base md:text-lg font-semibold text-[#1E1B4B] mb-1">Coûts journaliers</h2>
        <p className="text-xs md:text-sm text-[#475569] mb-4">Évolution des coûts sur 30 jours</p>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={dailyCosts}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E0E7FF" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 11, fill: "#475569" }}
              tickFormatter={(v) => v.slice(8)}
              stroke="#E0E7FF"
            />
            <YAxis
              tick={{ fontSize: 11, fill: "#475569" }}
              tickFormatter={(v) => `$${v}`}
              stroke="#E0E7FF"
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#fff",
                border: "1px solid #E0E7FF",
                borderRadius: "8px",
                fontSize: "13px",
              }}
              formatter={(v) => [`$${Number(v).toFixed(2)}`, "Coût"]}
            />
            <Line type="monotone" dataKey="cost" stroke="#6366F1" strokeWidth={2.5} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white rounded-xl p-4 md:p-6 border border-[#E0E7FF]">
        <h2 className="text-base md:text-lg font-semibold text-[#1E1B4B] mb-1">Coûts par équipe</h2>
        <p className="text-xs md:text-sm text-[#475569] mb-4">Répartition mensuelle</p>
        <ResponsiveContainer width="100%" height={260}>
          <PieChart>
            <Pie
              data={teamData}
              dataKey="total"
              nameKey="team"
              cx="50%"
              cy="50%"
              outerRadius={90}
              label={({ name, value }) => `${name}: $${value}`}
            >
              {teamData.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: "#fff",
                border: "1px solid #E0E7FF",
                borderRadius: "8px",
                fontSize: "13px",
              }}
              formatter={(v) => `$${Number(v).toFixed(2)}`}
            />
            <Legend wrapperStyle={{ fontSize: "12px", color: "#475569" }} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
