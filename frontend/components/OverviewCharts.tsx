"use client";

import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from "recharts";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"];

interface Props {
  dailyCosts: { date: string; cost: number }[];
  teamData: { team: string; total: number }[];
}

export default function OverviewCharts({ dailyCosts, teamData }: Props) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Line chart — coûts par jour */}
      <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
        <h2 className="text-lg font-semibold mb-4">Coûts journaliers</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={dailyCosts}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12 }}
              tickFormatter={(v) => v.slice(8)} // "2026-03-01" → "01"
            />
            <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `$${v}`} />
            <Tooltip formatter={(v) => [`$${Number(v).toFixed(2)}`, "Coût"]} />
            <Line type="monotone" dataKey="cost" stroke="#3b82f6" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Pie chart — coûts par équipe */}
      <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
        <h2 className="text-lg font-semibold mb-4">Coûts par equipe</h2>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={teamData}
              dataKey="total"
              nameKey="team"
              cx="50%"
              cy="50%"
              outerRadius={100}
              label={({ name, value }) => `${name}: $${value}`}
            >
              {teamData.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(v) => `$${Number(v).toFixed(2)}`} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
