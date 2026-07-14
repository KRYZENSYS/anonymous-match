"use client";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Coins, Sparkles, Gift, Trophy, Crown } from "lucide-react";
import { api } from "@/lib/api";
import { useTranslation } from "@/i18n";
import { useTelegram } from "@/hooks/useTelegram";

export default function CoinsPage() {
  const [balance, setBalance] = useState(0);
  const [packages, setPackages] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const t = useTranslation();
  const { haptic } = useTelegram();

  useEffect(() => {
    Promise.all([
      api.get("/gamification/coins/balance"),
      api.get("/community/coins/packages"),
    ]).then(([b, p]) => {
      setBalance(b.balance);
      setPackages(p);
      setLoading(false);
    });
  }, []);

  const buyPackage = async (pkg: any) => {
    try {
      // In real app: trigger Telegram Stars payment
      alert(`Buying ${pkg.name} for ${pkg.price_stars} ⭐`);
      // const result = await api.post("/community/coins/purchase", { package_id: pkg.id, telegram_payment_charge_id: "demo" });
      // setBalance(balance + result.coins_added);
      haptic.notification("success");
    } catch (e) {}
  };

  if (loading) return <div className="h-screen flex items-center justify-center">{t("common.loading")}</div>;

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 to-orange-50 dark:from-slate-900 dark:to-slate-950 p-4">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-amber-400 to-orange-500 rounded-full mb-3">
            <Coins className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold mb-1">{balance} 🪙</h1>
          <p className="text-slate-500">{t("coins.balance")}</p>
        </div>
        <h2 className="text-xl font-bold mb-3">🛒 {t("coins.packages")}</h2>
        <div className="grid grid-cols-2 gap-3 mb-6">
          {packages.map((pkg, i) => (
            <motion.button
              key={pkg.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              onClick={() => buyPackage(pkg)}
              className={`relative p-4 bg-white dark:bg-slate-800 rounded-2xl shadow-sm text-left ${
                pkg.is_popular ? "ring-2 ring-rose-500" : ""
              }`}
            >
              {pkg.is_popular && (
                <div className="absolute -top-2 -right-2 bg-rose-500 text-white text-xs px-2 py-0.5 rounded-full flex items-center gap-1">
                  <Sparkles className="w-3 h-3" /> POPULAR
                </div>
              )}
              <div className="text-3xl font-bold text-amber-500 mb-1">
                {pkg.coins + (pkg.bonus_coins || 0)} 🪙
              </div>
              {pkg.bonus_coins > 0 && (
                <div className="text-xs text-green-500">+{pkg.bonus_coins} bonus</div>
              )}
              <div className="text-sm text-slate-500 mt-2">{pkg.name}</div>
              <div className="mt-2 text-lg font-bold">⭐ {pkg.price_stars}</div>
            </motion.button>
          ))}
        </div>
        <h2 className="text-xl font-bold mb-3">💡 {t("coins.earn")}</h2>
        <div className="space-y-2">
          {[
            { icon: <Sparkles className="text-rose-500" />, title: t("coins.daily_streak"), reward: "+10-100" },
            { icon: <Gift className="text-pink-500" />, title: t("coins.new_match"), reward: "+5" },
            { icon: <Trophy className="text-yellow-500" />, title: t("coins.achievements"), reward: "+50-10000" },
            { icon: <Crown className="text-purple-500" />, title: t("coins.referrals"), reward: "+500" },
          ].map((e, i) => (
            <div key={i} className="flex items-center gap-3 p-3 bg-white dark:bg-slate-800 rounded-xl">
              <div className="w-10 h-10 bg-slate-100 dark:bg-slate-700 rounded-full flex items-center justify-center">
                {e.icon}
              </div>
              <div className="flex-1 font-medium">{e.title}</div>
              <div className="text-amber-500 font-bold">{e.reward} 🪙</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
