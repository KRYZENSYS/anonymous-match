"use client";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, ChevronLeft, ChevronRight, Eye, Send, Heart } from "lucide-react";
import { api } from "@/lib/api";
import { useTelegram } from "@/hooks/useTelegram";
import { useTranslation } from "@/i18n";

interface Story {
  id: number;
  user_id: number;
  user_nickname: string;
  user_avatar?: string;
  media_type: string;
  media_url: string;
  text_overlay?: string;
  background_color: string;
  duration: number;
  views_count: number;
  is_viewed: boolean;
  is_mine: boolean;
  created_at: string;
}

export default function StoriesPage() {
  const [stories, setStories] = useState<Story[]>([]);
  const [current, setCurrent] = useState(0);
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(true);
  const [replyText, setReplyText] = useState("");
  const t = useTranslation();
  const { haptic } = useTelegram();

  useEffect(() => {
    load();
  }, []);

  useEffect(() => {
    if (current >= stories.length) return;
    const duration = stories[current].duration * 1000;
    const step = 100 / (duration / 50);
    const timer = setInterval(() => {
      setProgress((p) => {
        if (p + step >= 100) {
          next();
          return 0;
        }
        return p + step;
      });
    }, 50);
    api.post(`/stories/${stories[current].id}/view`).catch(() => {});
    return () => clearInterval(timer);
  }, [current, stories]);

  const load = async () => {
    setLoading(true);
    try {
      const data = await api.get("/stories/feed");
      setStories(data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const next = () => {
    if (current < stories.length - 1) {
      setCurrent(current + 1);
      setProgress(0);
    }
  };

  const prev = () => {
    if (current > 0) {
      setCurrent(current - 1);
      setProgress(0);
    }
  };

  const handleReact = async (reaction: string) => {
    try {
      await api.post(`/stories/${stories[current].id}/react?reaction=${reaction}`);
      haptic.impact("light");
    } catch (e) {}
  };

  const handleReply = async () => {
    if (!replyText.trim()) return;
    try {
      await api.post(`/stories/${stories[current].id}/reply`, { content: replyText });
      haptic.notification("success");
      setReplyText("");
      next();
    } catch (e) {}
  };

  if (loading) return <div className="h-screen flex items-center justify-center bg-black text-white">{t("common.loading")}</div>;
  if (stories.length === 0) return <div className="h-screen flex items-center justify-center bg-black text-white">{t("stories.empty")}</div>;

  const story = stories[current];

  return (
    <div className="fixed inset-0 bg-black flex flex-col">
      <div className="absolute top-0 left-0 right-0 z-20 p-3 flex gap-1">
        {stories.map((s, i) => (
          <div key={s.id} className="flex-1 h-1 bg-white/30 rounded overflow-hidden">
            <div className="h-full bg-white" style={{ width: i === current ? `${progress}%` : i < current ? "100%" : "0%" }} />
          </div>
        ))}
      </div>
      <div className="absolute top-4 left-0 right-0 z-20 p-3 flex items-center justify-between text-white">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-rose-400 to-pink-600 p-0.5">
            <div className="w-full h-full rounded-full bg-cover bg-center" style={{ backgroundImage: story.user_avatar ? `url(${story.user_avatar})` : "linear-gradient(135deg, #f472b6, #db2777)" }} />
          </div>
          <div>
            <div className="font-semibold text-sm">{story.user_nickname}</div>
            <div className="text-xs text-white/70">2 soat oldin</div>
          </div>
        </div>
        <button onClick={() => history.back()} className="p-1">
          <X size={28} />
        </button>
      </div>
      <AnimatePresence mode="wait">
        <motion.div
          key={story.id}
          initial={{ opacity: 0, scale: 1.05 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="flex-1 flex items-center justify-center"
          style={{ backgroundColor: story.background_color }}
        >
          {story.media_type === "image" ? (
            <img src={story.media_url} alt="" className="max-w-full max-h-full object-contain" />
          ) : (
            <video src={story.media_url} autoPlay className="max-w-full max-h-full object-contain" />
          )}
          {story.text_overlay && (
            <div className="absolute inset-0 flex items-center justify-center p-8">
              <p className="text-white text-2xl font-bold text-center drop-shadow-2xl">{story.text_overlay}</p>
            </div>
          )}
        </motion.div>
      </AnimatePresence>
      <div className="absolute bottom-0 left-0 right-0 z-20 p-4 space-y-3">
        {!story.is_mine && (
          <div className="flex items-center gap-2">
            <input
              value={replyText}
              onChange={(e) => setReplyText(e.target.value)}
              placeholder={t("stories.reply_placeholder")}
              className="flex-1 bg-white/10 backdrop-blur-md text-white placeholder-white/60 rounded-full px-4 py-2 outline-none border border-white/20"
            />
            <button onClick={handleReply} className="p-2 bg-rose-500 rounded-full">
              <Send size={20} className="text-white" />
            </button>
          </div>
        )}
        <div className="flex justify-around text-white/80 text-xs">
          <button onClick={prev} className="flex flex-col items-center gap-1">
            <ChevronLeft size={24} />
          </button>
          <div className="flex gap-4">
            {["❤️", "😍", "🔥", "👏", "😢", "😮"].map((e) => (
              <button key={e} onClick={() => handleReact(e)} className="text-2xl hover:scale-125 transition">
                {e}
              </button>
            ))}
          </div>
          <button onClick={next} className="flex flex-col items-center gap-1">
            <ChevronRight size={24} />
          </button>
        </div>
      </div>
    </div>
  );
}
