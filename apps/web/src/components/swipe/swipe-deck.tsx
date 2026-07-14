"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Heart, X, Star, Undo2 } from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { ProfileCard } from "./profile-card";
import { discoverAPI } from "@/lib/api";
import { hapticFeedback } from "@/hooks/useTelegram";
import { Spinner } from "@/components/ui/spinner";

export function SwipeDeck() {
  const qc = useQueryClient();
  const [index, setIndex] = useState(0);
  const [showMatch, setShowMatch] = useState<{ matchId: number; profile: any } | null>(null);

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["discover"],
    queryFn: () => discoverAPI.list({ limit: 20 }),
  });

  const swipeMutation = useMutation({
    mutationFn: ({ target_user_id, action }: { target_user_id: number; action: "like" | "pass" | "superlike" }) =>
      discoverAPI.swipe(target_user_id, action),
    onSuccess: (res) => {
      if (res.is_match && res.match_id) {
        setShowMatch({ matchId: res.match_id, profile: data.profiles[index] });
        hapticFeedback("heavy");
      }
      setIndex((i) => i + 1);
      qc.invalidateQueries({ queryKey: ["discover"] });
      qc.invalidateQueries({ queryKey: ["matches"] });
    },
    onError: (e: any) => {
      toast.error(e.response?.data?.detail || "Xatolik yuz berdi");
    },
  });

  const handleSwipe = (direction: "left" | "right" | "up") => {
    const profile = data?.profiles?.[index];
    if (!profile) return;
    const action = direction === "left" ? "pass" : direction === "up" ? "superlike" : "like";
    hapticFeedback(direction === "up" ? "heavy" : "medium");
    swipeMutation.mutate({ target_user_id: profile.user_id || profile.public_id, action });
  };

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  const profiles = data?.profiles || [];
  const profile = profiles[index];

  if (!profile) {
    return (
      <div className="flex h-full flex-col items-center justify-center p-8 text-center">
        <div className="text-6xl mb-4">😢</div>
        <h2 className="text-2xl font-bold mb-2">Profil topilmadi</h2>
        <p className="text-sm text-dark-500 mb-6">Keyinroq qaytib ko'ring yoki filtrlarni o'zgartiring</p>
        <button onClick={() => { setIndex(0); refetch(); }} className="btn-primary">Qayta yuklash</button>
      </div>
    );
  }

  return (
    <div className="relative h-full w-full">
      <AnimatePresence>
        <motion.div
          key={profile.public_id}
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="absolute inset-0 p-4"
        >
          <ProfileCard profile={profile} onSwipe={handleSwipe} />
        </motion.div>
      </AnimatePresence>

      {/* Action buttons */}
      <div className="absolute bottom-6 left-0 right-0 flex items-center justify-center gap-4 z-20">
        <button
          onClick={() => handleSwipe("left")}
          className="w-14 h-14 rounded-full bg-white shadow-lg flex items-center justify-center text-dark-900 hover:scale-110 transition active:scale-95"
          aria-label="Pass"
        >
          <X className="w-7 h-7" strokeWidth={3} />
        </button>
        <button
          onClick={() => handleSwipe("up")}
          className="w-12 h-12 rounded-full bg-blue-500 shadow-lg flex items-center justify-center text-white hover:scale-110 transition active:scale-95"
          aria-label="Superlike"
        >
          <Star className="w-6 h-6" fill="currentColor" />
        </button>
        <button
          onClick={() => handleSwipe("right")}
          className="w-14 h-14 rounded-full bg-gradient-to-r from-rose-500 to-pink-500 shadow-lg flex items-center justify-center text-white hover:scale-110 transition active:scale-95"
          aria-label="Like"
        >
          <Heart className="w-7 h-7" fill="currentColor" />
        </button>
        <button
          onClick={() => toast("Undo hozircha mavjud emas")}
          className="w-10 h-10 rounded-full bg-white shadow-lg flex items-center justify-center text-yellow-500 hover:scale-110 transition active:scale-95"
          aria-label="Undo"
        >
          <Undo2 className="w-5 h-5" />
        </button>
      </div>

      {/* Match modal */}
      {showMatch && (
        <MatchModal
          profile={showMatch.profile}
          onClose={() => setShowMatch(null)}
        />
      )}
    </div>
  );
}

function MatchModal({ profile, onClose }: { profile: any; onClose: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-6"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.5, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: "spring", damping: 20 }}
        className="text-center"
      >
        <div className="text-7xl mb-4 animate-pulse">🎉</div>
        <h1 className="text-4xl font-bold gradient-text mb-2">Bu MATCH!</h1>
        <p className="text-lg text-white mb-2">Siz va <b>{profile.nickname}</b></p>
        <p className="text-sm text-dark-300 mb-8">bir-biringizga yoqdingiz!</p>
        <div className="flex gap-3">
          <button onClick={onClose} className="btn-secondary px-6">Davom etish</button>
          <button onClick={onClose} className="btn-primary px-6">Yozish 💬</button>
        </div>
      </motion.div>
    </motion.div>
  );
}
