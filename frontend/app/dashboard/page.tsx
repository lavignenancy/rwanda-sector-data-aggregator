import React from "react";
import { SectorDataNode } from "@/types";

async function fetchDashboardMetrics(): Promise<SectorDataNode[]> {
  const res = await fetch("http://localhost:8000/v1/sectors/summary", {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error("Failed to pull aggregated sector datasets");
  }
  return res.json();
}

export default async function DashboardPage() {
  const data = await fetchDashboardMetrics();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 p-8">
      <header className="mb-8 border-b border-slate-800 pb-4">
        <h1 className="text-3xl font-bold tracking-tight">Rwanda Sector Data Aggregator</h1>
        <p className="text-slate-400 mt-1">Autonomous public sector data collection and monitoring dashboard</p>
      </header>

      <main className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Geographic Distribution Panel */}
        <section className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 min-h-[450px]">
          <h2 className="text-xl font-semibold mb-4 text-slate-200">Regional Data Choropleth</h2>
          <div className="w-full h-full flex items-center justify-center border border-dashed border-slate-700 rounded-lg text-slate-500">
            [Interactive Map Interface Initialization Area]
          </div>
        </section>

        {/* Aggregation Insights Column */}
        <section className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h2 className="text-xl font-semibold mb-4 text-slate-200">Sector Inventories</h2>
          <div className="space-y-4">
            {data.map((item) => (
              <div key={item.id} className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-medium text-slate-300">{item.sector}</span>
                  <span className="text-xs px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                    {item.data_type}
                  </span>
                </div>
                <p className="text-xs text-slate-500 truncate mb-1">Source: {item.source_url}</p>
                <div className="text-sm mt-2 text-slate-400">
                  Updated: {new Date(item.updated_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
