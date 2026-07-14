"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Crown, Check, Sparkles, Zap, Heart, Eye } from "lucide-react";
import { premiumAPI } from "@/lib/api";
import { Spinner } from "@/components/ui/spinner";
import { useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";

export default function PremiumPage() {
  const router = useRouter();
  const { data: plans, isLoading: plansLoading } = useQuery({
    queryKey: ["premium-plans"],
    queryFn: premiumAPI.plans,
  });
  const { data: status, isLoading: statusLoading } = useQuery({
    queryKey: ["premium-status"],
    queryFn: premiumAPI.status,
  });

  const boostMutation = useMutation({
    mutationFn: premiumAPI.boost,
    onSuccess: (res) => {
      if (res.success) toast.success(`⚡ Boost faollashtirildi! ${res.remaining_boosts} ta qoldi`);
      else toast.error(res.message);
    },
  });

  if (plansLoading || statusLoading) return <div className="flex h-screen items-center justify-center"><Spinner size="lg" /></div>;

  const features = [
    { icon: Heart, title: "Cheksiz yoqtirishlar", desc: "Kunlik limit sizlar uchun emas" },
    { icon: Zap, title: "Ko'proq super like", desc: "5 dan 9999 gacha super like" },
    { icon: Eye, title: "Kim ko'rganini bilish", desc: "Profilingizni kim ko'rganini ko'ring" },
    { icon: Sparkles, title: "Boost har oy", desc: "30 daqiqaga eng yuqoriga chiqing" },
  ];

  return (
    <div className="min-h-screen safe-top safe-bottom pb-20">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-white/80 dark:bg-dark-950/80 backdrop-blur-xl border-b border-dark-200 dark:border-dark-800 px-4 py-3 flex items-center gap-3">
        <button onClick={() => router.back()} className="text-sm">← Orqaga</button>
        <h1 className="font-bold flex-1 text-center">Premium</h1>
      </div>

      {/* Hero */}
      <div className="px-6 pt-8 pb-6 text-center">
        <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} className="inline-block">
          <Crown className="w-16 h-16 text-yellow-500 mx-auto" fill="currentColor" />
        </motion.div>
        <h1 className="text-3xl font-bold gradient-text mt-4">Anonymous Match Premium</h1>
        <p className="text-sm text-dark-500 mt-2">Barcha imkoniyatlarga ega bo'ling</p>
      </div>

      {/* Status */}
      {status?.is_premium && (
        <div className="mx-4 mb-6 card p-4 bg-gradient-to-r from-yellow-500/10 to-yellow-600/10 border-yellow-500/30">
          <div className="flex items-center gap-3">
            <Crown className="w-6 h-6 text-yellow-500" />
            <div>
              <div className="font-bold">Premium: {status.tier.toUpperCase()}</div>
              <div className="text-xs text-dark-500">{status.days_left} kun qoldi</div>
            </div>
          </div>
          {status.boost_count > 0 && (
            <button
              onClick={() => boostMutation.mutate()}
              disabled={boostMutation.isPending}
              className="mt-3 btn-primary w-full"
            >
              ⚡ Boost faollashtirish ({status.boost_count})
            </button>
          )}
        </div>
      )}

      {/* Features */}
      <div className="px-6 space-y-3 mb-8">
        {features.map((f, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
            className="flex items-center gap-3"
          >
            <div className="w-10 h-10 rounded-full bg-gradient-to-r from-rose-500 to-pink-500 flex items-center justify-center flex-shrink-0">
              <f.icon className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-sm">{f.title}</h3>
              <p className="text-xs text-dark-500">{f.desc}</p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Plans */}
      <div className="px-4 space-y-3">
        {plans?.plans?.map((plan: any, i: number) => (
          <motion.div
            key={plan.tier}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 + i * 0.1 }}
            className={`card p-5 ${plan.tier === "platinum" ? "border-rose-500 shadow-lg shadow-rose-500/20" : ""}`}
          >
            {plan.tier === "platinum" && (
              <div className="text-xs font-bold text-rose-500 mb-1">🔥 MASHHUR</div>
            )}
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="text-xl font-bold flex items-center gap-2">
                  {plan.tier === "plus" && "🌟"}
                  {plan.tier === "gold" && "💫"}
                  {plan.tier === "platinum" && "💠"}
                  {plan.name}
                </h3>
                <p className="text-xs text-dark-500">{plan.duration_days} kun</p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold">{plan.price_stars} ⭐</div>
                <div className="text-xs text-dark-500">${plan.price_usd}</div>
              </div>
            </div>
            <ul className="space-y-1 mb-4">
              {plan.features.slice(0, 4).map((f: string) => (
                <li key={f} className="text-xs flex items-start gap-2">
                  <Check className="w-3.5 h-3.5 text-green-500 flex-shrink-0 mt-0.5" />
                  <span>{f}</span>
                </li>
              ))}
            </ul>
            <button className="btn-primary w-full">Sotib olish</button>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
