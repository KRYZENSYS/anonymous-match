"use client";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Trophy, Lock, CheckCircle2 } from "lucide-react";
import { api } from "@/lib/api";
import { useTranslation } from "@/i18n";

interface Achievement {
  id: number;
  code: string;
  name: string;
  description: string;
  icon: string;
  tier: string;
  reward_coins: number;
  condition_type: string;
  condition_value: number;
  progress: number;
  unlocked: boolean;
  unlocked_at: string | null;
}

const TIER_COLORS: Record<string, string> = {
  bronze: "from-amber-600 to-amber-800",
  silver: "from-slate-300 to-slate-500",
  gold: "from-yellow-400 to-yellow-600",
  platinum: "from-cyan-400 to-cyan-600",
  diamond: "from-purple-400 to-pink-600",
};

export default function AchievementsPage() {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [filter, setFilter] = useState<"all" | "unlocked" | "locked">("all");
  const [loading, setLoading] = useState(true);
  const t = useTranslation();

  useEffect(() => {
    api.get("/gamification/achievements").then((d) => {
      setAchievements(d);
      setLoading(false);
    });
  }, []);

  const filtered = achievements.filter((a) => {
    if (filter === "unlocked") return a.unlocked;
    if (filter === "locked") return !a.unlocked;
    return true;
  });

  const unlockedCount = achievements.filter((a) => a.unlocked).length;
  const totalReward = achievements.filter((a) => a.unlocked).reduce((sum, a) => sum + a.reward_coins, 0);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-950 text-white p-4">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-6">
          <Trophy className="w-16 h-16 mx-auto text-yellow-400 mb-2" />
          <h1 className="text-3xl font-bold mb-2">{t("achievements.title")}</h1>
          <p className="text-slate-400">{unlockedCount} / {achievements.length} {t("achievements.unlocked")}</p>
          <p className="text-yellow-400 mt-1">💰 {totalReward} {t("achievements.coins_earned")}</p>
        </div>
        <div className="flex gap-2 mb-6 bg-slate-800/50 p-1 rounded-full">
          {(["all", "unlocked", "locked"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`flex-1 py-2 px-4 rounded-full text-sm font-medium transition ${
                filter === f ? "bg-rose-500 text-white" : "text-slate-400"
              }`}
            >
              {t(`achievements.${f}`)}
            </button>
          ))}
        </div>
        <div className="space-y-3">
          {filtered.map((a, i) => (
            <motion.div
              key={a.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className={`relative overflow-hidden rounded-2xl p-4 ${
                a.unlocked
                  ? `bg-gradient-to-br ${TIER_COLORS[a.tier]} bg-opacity-20 border border-white/20`
                  : "bg-slate-800/50 border border-slate-700"
              }`}
            >
              <div className="flex items-center gap-4">
                <div className={`text-5xl ${a.unlocked ? "" : "grayscale opacity-30"}`}>{a.icon}</div>
                <div className="flex-1">
                  <h3 className="font-bold text-lg flex items-center gap-2">
                    {a.name}
                    {a.unlocked && <CheckCircle2 className="w-5 h-5 text-green-400" />}
                  </h3>
                  <p className="text-sm text-slate-300">{a.description}</p>
                  <div className="mt-2 flex items-center justify-between">
                    <div className="flex-1 mr-3">
                      <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                        <motion.div
                          className="h-full bg-gradient-to-r from-rose-400 to-pink-600"
                          initial={{ width: 0 }}
                          animate={{ width: `${Math.min(100, (a.progress / a.condition_value) * 100)}%` }}
                          transition={{ duration: 1 }}
                        />
                      </div>
                      <div className="text-xs text-slate-400 mt-1">
                        {a.progress} / {a.condition_value}
                      </div>
                    </div>
                    <div className="text-yellow-400 font-bold text-sm">+{a.reward_coins} 🪙</div>
                  </div>
                </div>
                {!a.unlocked && <Lock className="w-5 h-5 text-slate-500" />}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
