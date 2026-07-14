"use client";
import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Phone, PhoneOff, Video, VideoOff, Mic, MicOff } from "lucide-react";
import { api } from "@/lib/api";
import { useTranslation } from "@/i18n";

export default function CallsPage() {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const t = useTranslation();

  useEffect(() => {
    api.get("/advanced/calls/history").then((d) => {
      setHistory(d);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="h-screen flex items-center justify-center">{t("common.loading")}</div>;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 p-4">
      <h1 className="text-2xl font-bold mb-4">📞 {t("calls.title")}</h1>
      {history.length === 0 ? (
        <div className="text-center py-20 text-slate-400">{t("calls.empty")}</div>
      ) : (
        <div className="space-y-2">
          {history.map((c) => (
            <motion.div
              key={c.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white dark:bg-slate-900 rounded-2xl p-4 flex items-center gap-3"
            >
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                c.status === "ended" ? "bg-green-100 text-green-600" :
                c.status === "missed" ? "bg-red-100 text-red-600" :
                "bg-slate-100 text-slate-600"
              }`}>
                {c.type === "video" ? <Video size={20} /> : <Phone size={20} />}
              </div>
              <div className="flex-1">
                <div className="font-medium">{c.type === "video" ? "Video call" : "Voice call"}</div>
                <div className="text-xs text-slate-500">
                  {new Date(c.started_at).toLocaleString()} · {c.duration > 0 ? `${Math.floor(c.duration / 60)}m ${c.duration % 60}s` : t("calls.missed")}
                </div>
              </div>
              <span className={`text-xs px-2 py-1 rounded-full ${
                c.status === "ended" ? "bg-green-100 text-green-700" :
                c.status === "missed" ? "bg-red-100 text-red-700" :
                "bg-slate-100 text-slate-700"
              }`}>
                {c.status}
              </span>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
