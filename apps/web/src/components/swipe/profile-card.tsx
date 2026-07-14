"use client";

import { motion } from "framer-motion";
import { Badge } from "@/components/ui/badge";
import { SmartImage } from "@/components/ui/image";
import { calculateDistance } from "@/lib/utils";
import { useAuthStore } from "@/store/auth";
import { useTg } from "@/components/providers/telegram-provider";

interface ProfileCardProps {
  profile: {
    public_id: string;
    nickname: string;
    age: number;
    gender: string;
    region?: string | null;
    city?: string | null;
    bio?: string | null;
    interests?: string[];
    avatar_url?: string | null;
    photos?: string[];
    is_online: boolean;
    is_verified?: boolean;
    is_premium?: boolean;
    is_boosted?: boolean;
    distance_km?: number | null;
  };
  onSwipe?: (direction: "left" | "right" | "up") => void;
}

export function ProfileCard({ profile, onSwipe }: ProfileCardProps) {
  const { user: tgUser } = useTg();
  const photos = profile.photos?.length ? profile.photos : (profile.avatar_url ? [profile.avatar_url] : []);
  const mainPhoto = photos[0];

  return (
    <motion.div
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      dragElastic={0.7}
      onDragEnd={(_, info) => {
        if (Math.abs(info.offset.x) > 100) {
          onSwipe?.(info.offset.x > 0 ? "right" : "left");
        }
      }}
      whileDrag={{ scale: 1.05, rotate: 0 }}
      className="relative h-full w-full overflow-hidden rounded-3xl bg-dark-900 shadow-2xl"
    >
      {/* Photo */}
      <div className="relative h-3/4 w-full">
        <SmartImage
          src={mainPhoto}
          alt={profile.nickname}
          className="h-full w-full"
          fallback="🖼️"
        />
        {/* Photo indicators */}
        {photos.length > 1 && (
          <div className="absolute top-3 left-0 right-0 flex gap-1 px-3 z-10">
            {photos.map((_, i) => (
              <div key={i} className="flex-1 h-1 bg-white/30 rounded-full overflow-hidden">
                <div className="h-full w-1/2 bg-white rounded-full" />
              </div>
            ))}
          </div>
        )}
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/30" />
        {/* Top badges */}
        <div className="absolute top-4 right-4 flex flex-col gap-2 z-10">
          {profile.is_boosted && <Badge variant="boost">⚡ Boost</Badge>}
          {profile.is_premium && <Badge variant="gold">💎 Premium</Badge>}
          {profile.is_verified && <Badge variant="verified">✓</Badge>}
          {profile.is_online && (
            <div className="flex items-center gap-1 bg-green-500 text-white px-2 py-1 rounded-full text-xs font-semibold">
              <span className="w-2 h-2 bg-white rounded-full animate-pulse" />
              Online
            </div>
          )}
        </div>
      </div>

      {/* Info */}
      <div className="absolute bottom-0 left-0 right-0 p-5 text-white z-10">
        <div className="flex items-baseline gap-2 mb-1">
          <h2 className="text-3xl font-bold">{profile.nickname}</h2>
          <span className="text-2xl font-light opacity-90">{profile.age}</span>
        </div>
        {(profile.city || profile.region) && (
          <p className="text-sm opacity-90 mb-1">📍 {[profile.city, profile.region].filter(Boolean).join(", ")}</p>
        )}
        {profile.distance_km != null && (
          <p className="text-xs opacity-75 mb-2">📏 {profile.distance_km} km uzoqda</p>
        )}
        {profile.bio && <p className="text-sm opacity-90 line-clamp-2 mb-2">{profile.bio}</p>}
        {profile.interests && profile.interests.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {profile.interests.slice(0, 4).map((tag) => (
              <span key={tag} className="px-2 py-1 bg-white/20 backdrop-blur rounded-full text-xs">
                #{tag}
              </span>
            ))}
            {profile.interests.length > 4 && (
              <span className="px-2 py-1 bg-white/20 backdrop-blur rounded-full text-xs">
                +{profile.interests.length - 4}
              </span>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
}
