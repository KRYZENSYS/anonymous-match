"use client";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Calendar, MapPin, Users, Ticket, Video, Heart } from "lucide-react";
import { api } from "@/lib/api";
import { useTranslation } from "@/i18n";
import { useTelegram } from "@/hooks/useTelegram";

interface Event {
  id: number;
  title: string;
  description: string;
  cover_url?: string;
  category: string;
  location_name: string;
  starts_at: string;
  capacity: number;
  attendees_count: number;
  ticket_price: number;
  is_online: boolean;
  meeting_url?: string;
}

export default function EventsPage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [groups, setGroups] = useState<any[]>([]);
  const [tab, setTab] = useState<"events" | "groups">("events");
  const [loading, setLoading] = useState(true);
  const t = useTranslation();
  const { haptic } = useTelegram();

  useEffect(() => {
    Promise.all([
      api.get("/community/events"),
      api.get("/community/groups"),
    ]).then(([e, g]) => {
      setEvents(e);
      setGroups(g);
      setLoading(false);
    });
  }, []);

  const joinEvent = async (id: number) => {
    try {
      await api.post(`/community/events/${id}/join`);
      haptic.notification("success");
      setEvents(events.map((e) => e.id === id ? { ...e, attendees_count: e.attendees_count + 1 } : e));
    } catch (err: any) {
      alert(err.response?.data?.detail || t("events.join_error"));
    }
  };

  const joinGroup = async (id: number) => {
    try {
      await api.post(`/community/groups/${id}/join`);
      haptic.notification("success");
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) return <div className="h-screen flex items-center justify-center">{t("common.loading")}</div>;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <div className="bg-white dark:bg-slate-900 sticky top-0 z-10 border-b border-slate-200 dark:border-slate-800">
        <h1 className="text-2xl font-bold p-4">{t("community.title")}</h1>
        <div className="flex">
          {(["events", "groups"] as const).map((tt) => (
            <button
              key={tt}
              onClick={() => setTab(tt)}
              className={`flex-1 py-3 font-medium transition ${
                tab === tt
                  ? "text-rose-500 border-b-2 border-rose-500"
                  : "text-slate-500 border-b-2 border-transparent"
              }`}
            >
              {t(`community.${tt}`)}
            </button>
          ))}
        </div>
      </div>
      <div className="p-4 space-y-4">
        {tab === "events" ? (
          events.length === 0 ? (
            <div className="text-center py-20 text-slate-400">{t("events.empty")}</div>
          ) : (
            events.map((e, i) => (
              <motion.div
                key={e.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="bg-white dark:bg-slate-900 rounded-2xl overflow-hidden shadow-sm"
              >
                {e.cover_url && (
                  <div className="h-40 bg-cover bg-center" style={{ backgroundImage: `url(${e.cover_url})` }} />
                )}
                <div className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-bold text-lg flex-1">{e.title}</h3>
                    {e.is_online && <Video className="w-5 h-5 text-blue-500" />}
                  </div>
                  {e.description && <p className="text-sm text-slate-600 dark:text-slate-300 mb-3">{e.description}</p>}
                  <div className="space-y-1 text-sm text-slate-500 mb-3">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      {new Date(e.starts_at).toLocaleString()}
                    </div>
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4" />
                      {e.location_name}
                    </div>
                    <div className="flex items-center gap-2">
                      <Users className="w-4 h-4" />
                      {e.attendees_count} / {e.capacity || "∞"} {t("events.attendees")}
                    </div>
                  </div>
                  <button
                    onClick={() => joinEvent(e.id)}
                    className="w-full py-3 bg-gradient-to-r from-rose-500 to-pink-500 text-white rounded-full font-medium hover:opacity-90"
                  >
                    {e.ticket_price > 0 ? (
                      <span className="flex items-center justify-center gap-2">
                        <Ticket className="w-4 h-4" /> {e.ticket_price} 🪙
                      </span>
                    ) : (
                      t("events.join")
                    )}
                  </button>
                </div>
              </motion.div>
            ))
          )
        ) : (
          groups.length === 0 ? (
            <div className="text-center py-20 text-slate-400">{t("groups.empty")}</div>
          ) : (
            groups.map((g, i) => (
              <motion.div
                key={g.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="bg-white dark:bg-slate-900 rounded-2xl p-4 shadow-sm"
              >
                <div className="flex items-start gap-3">
                  <div className="text-4xl">{g.icon || "👥"}</div>
                  <div className="flex-1">
                    <h3 className="font-bold text-lg flex items-center gap-2">
                      {g.name}
                      {g.is_verified && <span className="text-blue-500">✓</span>}
                    </h3>
                    <p className="text-sm text-slate-500 mt-1">{g.description}</p>
                    <div className="flex items-center justify-between mt-3">
                      <div className="text-xs text-slate-500">
                        👥 {g.member_count} {t("groups.members")}
                      </div>
                      <button
                        onClick={() => joinGroup(g.id)}
                        className="px-4 py-1.5 bg-rose-500 text-white rounded-full text-sm"
                      >
                        {t("groups.join")}
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))
          )
        )}
      </div>
    </div>
  );
}
