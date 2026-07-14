"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { motion } from "framer-motion";
import { Users, MessageSquare, Heart, DollarSign, AlertCircle, TrendingUp, Activity } from "lucide-react";
import { api } from "@/lib/api";
import { Spinner } from "@/components/ui/spinner";

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState<"dashboard" | "users" | "reports" | "broadcast">("dashboard");

  const { data: stats, isLoading } = useQuery({
    queryKey: ["admin-stats"],
    queryFn: async () => (await api.get("/admin/stats")).data,
  });

  if (isLoading) return <div className="flex h-screen items-center justify-center"><Spinner size="lg" /></div>;

  return (
    <div className="min-h-screen bg-dark-50 dark:bg-dark-950 p-6">
      <header className="mb-6">
        <h1 className="text-3xl font-bold">🛡️ Admin Panel</h1>
        <p className="text-sm text-dark-500">Anonymous Match</p>
      </header>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto no-scrollbar">
        {[
          { k: "dashboard", l: "📊 Dashboard" },
          { k: "users", l: "👥 Users" },
          { k: "reports", l: "🚨 Reports" },
          { k: "broadcast", l: "📢 Broadcast" },
        ].map((t) => (
          <button
            key={t.k}
            onClick={() => setActiveTab(t.k as any)}
            className={`px-4 py-2 rounded-xl font-semibold text-sm whitespace-nowrap ${
              activeTab === t.k ? "bg-rose-500 text-white" : "bg-white dark:bg-dark-900"
            }`}
          >
            {t.l}
          </button>
        ))}
      </div>

      {activeTab === "dashboard" && stats && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <StatCard icon={Users} label="Foydalanuvchilar" value={stats.total_users} sub={`+${stats.new_users_today} bugun`} color="from-blue-500 to-cyan-500" />
            <StatCard icon={Activity} label="Online" value={stats.online_now} sub="Hozir" color="from-green-500 to-emerald-500" />
            <StatCard icon={Heart} label="Matchlar" value={stats.total_matches} color="from-rose-500 to-pink-500" />
            <StatCard icon={MessageSquare} label="Xabarlar" value={stats.total_messages} color="from-purple-500 to-violet-500" />
            <StatCard icon={TrendingUp} label="Premium" value={stats.total_premium_users} color="from-yellow-500 to-orange-500" />
            <StatCard icon={DollarSign} label="Daromad" value={`${stats.revenue_total_stars} ⭐`} color="from-green-500 to-teal-500" />
            <StatCard icon={AlertCircle} label="Reports" value={stats.total_reports_pending} sub="kutilmoqda" color="from-red-500 to-rose-500" />
            <StatCard icon={Users} label="Faol bugun" value={stats.active_users_today} sub={`${stats.active_users_week} / hafta`} color="from-indigo-500 to-blue-500" />
          </div>

          <div className="card p-5">
            <h2 className="font-bold mb-3">Bugungi faollik</h2>
            <div className="space-y-2 text-sm">
              <Row label="Yangi userlar" value={stats.new_users_today} />
              <Row label="Online" value={stats.online_now} />
              <Row label="Faol bugun" value={stats.active_users_today} />
              <Row label="Faol hafta" value={stats.active_users_week} />
            </div>
          </div>
        </div>
      )}

      {activeTab === "users" && <UsersTab />}
      {activeTab === "reports" && <ReportsTab />}
      {activeTab === "broadcast" && <BroadcastTab />}
    </div>
  );
}

function StatCard({ icon: Icon, label, value, sub, color }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="card p-4"
    >
      <div className={`w-10 h-10 rounded-lg bg-gradient-to-r ${color} flex items-center justify-center mb-2`}>
        <Icon className="w-5 h-5 text-white" />
      </div>
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-xs text-dark-500">{label}</div>
      {sub && <div className="text-xs text-green-500 mt-0.5">{sub}</div>}
    </motion.div>
  );
}

function Row({ label, value }: any) {
  return (
    <div className="flex justify-between">
      <span className="text-dark-500">{label}</span>
      <span className="font-bold">{value}</span>
    </div>
  );
}

function UsersTab() {
  const { data, isLoading } = useQuery({
    queryKey: ["admin-users"],
    queryFn: async () => (await api.get("/admin/users", { params: { limit: 100 } })).data,
  });

  if (isLoading) return <Spinner />;
  return (
    <div className="card overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-dark-100 dark:bg-dark-900">
          <tr>
            <th className="p-3 text-left">ID</th>
            <th className="p-3 text-left">User</th>
            <th className="p-3">Premium</th>
            <th className="p-3">Status</th>
          </tr>
        </thead>
        <tbody>
          {data?.users?.map((u: any) => (
            <tr key={u.id} className="border-t border-dark-200 dark:border-dark-800">
              <td className="p-3 font-mono text-xs">{u.public_id}</td>
              <td className="p-3">{u.first_name || u.username || "—"}</td>
              <td className="p-3 text-center">{u.is_premium ? "💎" : "—"}</td>
              <td className="p-3 text-center">
                {u.is_banned ? "🚫" : u.is_online ? "🟢" : "⚪"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ReportsTab() {
  const { data, isLoading } = useQuery({
    queryKey: ["admin-reports"],
    queryFn: async () => (await api.get("/admin/reports/pending")).data,
  });
  if (isLoading) return <Spinner />;
  return (
    <div className="space-y-2">
      {data?.reports?.length === 0 ? (
        <div className="card p-8 text-center text-dark-500">Kutilayotgan reportlar yo'q ✅</div>
      ) : (
        data?.reports?.map((r: any) => (
          <div key={r.id} className="card p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono text-xs">#{r.id}</span>
              <span className="text-xs px-2 py-1 bg-red-500/10 text-red-500 rounded-full">{r.reason}</span>
            </div>
            <p className="text-sm">{r.description || "Tavsif yo'q"}</p>
            <div className="flex gap-2 mt-3">
              <button className="btn-secondary text-xs">🚫 Ban</button>
              <button className="btn-secondary text-xs">⚠️ Warn</button>
              <button className="btn-secondary text-xs">✓ No action</button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

function BroadcastTab() {
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [target, setTarget] = useState("all");

  const broadcast = useMutation({
    mutationFn: () => api.post("/admin/broadcast", { title, body, target }),
    onSuccess: (res: any) => {
      alert(`✅ ${res.data.sent_to} ta foydalanuvchiga yuborildi`);
      setTitle("");
      setBody("");
    },
  });

  return (
    <div className="card p-5 space-y-3">
      <h2 className="font-bold">📢 Xabar yuborish</h2>
      <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Sarlavha" className="input" />
      <textarea value={body} onChange={(e) => setBody(e.target.value)} placeholder="Matn" rows={4} className="input" />
      <select value={target} onChange={(e) => setTarget(e.target.value)} className="input">
        <option value="all">Hammaga</option>
        <option value="premium">Faqat Premium</option>
        <option value="online">Online</option>
        <option value="new_users">Yangi userlar (7 kun)</option>
      </select>
      <button
        onClick={() => broadcast.mutate()}
        disabled={!title || !body || broadcast.isPending}
        className="btn-primary w-full"
      >
        Yuborish
      </button>
    </div>
  );
}
