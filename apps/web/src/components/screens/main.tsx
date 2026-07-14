"use client";

import { useState } from "react";
import { Heart, MessageCircle, User as UserIcon, Sparkles } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { SwipeDeck } from "@/components/swipe/swipe-deck";
import { MatchesList } from "@/components/chat/matches-list";
import { ProfileScreen } from "@/components/screens/profile";

type Tab = "discover" | "matches" | "profile";

export default function MainScreen() {
  const [tab, setTab] = useState<Tab>("discover");

  return (
    <div className="flex h-screen flex-col safe-top safe-bottom">
      {/* Tab content */}
      <div className="flex-1 relative overflow-hidden">
        <AnimatePresence mode="wait">
          <motion.div
            key={tab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="absolute inset-0"
          >
            {tab === "discover" && <SwipeDeck />}
            {tab === "matches" && <MatchesList />}
            {tab === "profile" && <ProfileScreen />}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Bottom nav */}
      <nav className="border-t border-dark-200 dark:border-dark-800 bg-white/80 dark:bg-dark-950/80 backdrop-blur-xl">
        <div className="grid grid-cols-3 gap-1 px-2 py-2">
          {[
            { id: "discover", icon: Sparkles, label: "Kashf" },
            { id: "matches", icon: MessageCircle, label: "Chat" },
            { id: "profile", icon: UserIcon, label: "Profil" },
          ].map((item) => {
            const Icon = item.icon;
            const active = tab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setTab(item.id as Tab)}
                className={`relative flex flex-col items-center gap-1 py-2 rounded-xl transition ${
                  active ? "text-rose-500" : "text-dark-500 dark:text-dark-400"
                }`}
              >
                {active && (
                  <motion.div
                    layoutId="tab-indicator"
                    className="absolute -top-2 left-1/2 -translate-x-1/2 w-8 h-1 rounded-full bg-rose-500"
                  />
                )}
                <Icon className="w-6 h-6" strokeWidth={active ? 2.5 : 2} />
                <span className="text-xs font-semibold">{item.label}</span>
              </button>
            );
          })}
        </div>
      </nav>
    </div>
  );
}
