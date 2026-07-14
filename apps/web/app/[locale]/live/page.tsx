"use client";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Video, Users, Heart, Gift } from "lucide-react";
import { api } from "@/lib/api";
import { useTranslation } from "@/i18n";
import { useTelegram } from "@/hooks/useTelegram";

interface LiveStream {
  id: number;
  host_nickname: string;
  host_avatar?: string;
  title: string;
  viewers_count: number;
  stream_url: string;
  thumbnail_url?: string;
  visibility: string;
  started_at: string;
}

export default function LivePage() {
  const [streams, setStreams] = useState<LiveStream[]>([]);
  const [loading, setLoading] = useState(true);
  const t = useTranslation();
  const { haptic } = useTelegram();

  useEffect(() => {
    api.get("/community/live/active").then((d) => {
      setStreams(d);
      setLoading(false);
    });
  }, []);

  const startLive = async () => {
    try {
      const res = await api.post("/community/live/start", { title: "Live stream" });
      haptic.notification("success");
      alert(`Stream started! Channel: ${res.channel}`);
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) return <div className="h-screen flex items-center justify-center">{t("common.loading")}</div>;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 p-4">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Video className="w-7 h-7 text-rose-500" />
          {t("live.title")}
        </h1>
        <button onClick={startLive} className="px-4 py-2 bg-rose-500 text-white rounded-full text-sm font-medium">
          🔴 {t("live.start")}
        </button>
      </div>
      {streams.length === 0 ? (
        <div className="text-center py-20 text-slate-400">
          <Video className="w-20 h-20 mx-auto mb-4 opacity-30" />
          {t("live.empty")}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {streams.map((s, i) => (
            <motion.div
              key={s.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.05 }}
              className="relative aspect-video bg-slate-900 rounded-2xl overflow-hidden cursor-pointer"
            >
              {s.thumbnail_url ? (
                <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: `url(${s.thumbnail_url})` }} />
              ) : (
                <div className="absolute inset-0 bg-gradient-to-br from-rose-500/30 to-purple-600/30 flex items-center justify-center">
                  <Video className="w-16 h-16 text-white/50" />
                </div>
              )}
              <div className="absolute top-2 left-2 px-2 py-1 bg-red-500 text-white text-xs rounded-full flex items-center gap-1">
                <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                LIVE
              </div>
              <div className="absolute top-2 right-2 px-2 py-1 bg-black/50 backdrop-blur text-white text-xs rounded-full flex items-center gap-1">
                <Users className="w-3 h-3" /> {s.viewers_count}
              </div>
              <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/80 to-transparent text-white">
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-6 h-6 rounded-full bg-gradient-to-br from-rose-400 to-pink-600" />
                  <span className="font-medium text-sm">{s.host_nickname}</span>
                </div>
                <div className="text-sm">{s.title}</div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
