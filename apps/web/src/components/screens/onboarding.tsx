"use client";

import { motion } from "framer-motion";
import { Heart, Shield, MessageCircle } from "lucide-react";

export default function OnboardingScreen() {
  return (
    <div className="flex h-screen flex-col items-center justify-center p-8 text-center">
      <motion.div initial={{ scale: 0.5, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ type: "spring", damping: 15 }} className="mb-8">
        <div className="text-7xl">💖</div>
      </motion.div>

      <motion.h1 initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.2 }} className="text-4xl font-bold gradient-text mb-3">
        Anonymous Match
      </motion.h1>

      <motion.p initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.3 }} className="text-sm text-dark-500 mb-12">
        Yangi odamlar bilan anonim tanishing
      </motion.p>

      <div className="space-y-4 w-full max-w-sm">
        <Feature icon={Heart} title="Anonim va xavfsiz" description="Telegram username yashirin" delay={0.4} />
        <Feature icon={Shield} title="Hech kim tanib bo'lmaydi" description="Yuz, ism, telefon yashirin" delay={0.5} />
        <Feature icon={MessageCircle} title="Real-time chat" description="Moslik bo'lsa darhol yozing" delay={0.6} />
      </div>

      <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.8 }} className="text-xs text-dark-400 mt-8">
        Bot orqali kiring: @AnonymousMatchBot
      </motion.p>
    </div>
  );
}

function Feature({ icon: Icon, title, description, delay }: any) {
  return (
    <motion.div initial={{ x: -20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ delay }} className="card p-4 flex items-start gap-3 text-left">
      <div className="w-10 h-10 rounded-full bg-gradient-to-r from-rose-500 to-pink-500 flex items-center justify-center flex-shrink-0">
        <Icon className="w-5 h-5 text-white" />
      </div>
      <div>
        <h3 className="font-semibold text-sm">{title}</h3>
        <p className="text-xs text-dark-500 mt-0.5">{description}</p>
      </div>
    </motion.div>
  );
}
