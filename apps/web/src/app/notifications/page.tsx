"use client";

import { useQuery, useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Heart, MessageCircle, Star, Crown, Bell, Sparkles } from "lucide-react";
import { notificationAPI } from "@/lib/api";
import { timeAgo } from "@/lib/utils";
import { Spinner } from "@/components/ui/spinner";

export default function NotificationsPage() {
  const router = useRouter();
  const { data, isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => notificationAPI.list({ limit: 50 }),
  });

  const markAllRead = useMutation({
    mutationFn: notificationAPI.markAllRead,
    onSuccess: () => {
      // Invalidate
    },
  });

  if (isLoading) return <div className="flex h-screen items-center justify-center"><Spinner size="lg" /></div>;

  const notifs = data?.notifications || [];
  const unread = data?.unread_count || 0;

  const getIcon = (type: string) => {
    if (type.includes("match")) return { icon: Heart, color: "from-rose-500 to-pink-500" };
    if (type.includes("message")) return { icon: MessageCircle, color: "from-blue-500 to-cyan-500" };
    if (type.includes("super_like")) return { icon: Star, color: "from-blue-400 to-blue-600" };
    if (type.includes("premium")) return { icon: Crown, color: "from-yellow-400 to-yellow-600" };
    if (type.includes("boost")) return { icon: Sparkles, color: "from-purple-500 to-pink-500" };
    return { icon: Bell, color: "from-dark-400 to-dark-600" };
  };

  return (
    <div className="min-h-screen safe-top safe-bottom">
      <div className="sticky top-0 z-10 bg-white/80 dark:bg-dark-950/80 backdrop-blur-xl border-b border-dark-200 dark:border-dark-800 px-4 py-3 flex items-center gap-3">
        <button onClick={() => router.back()}>←</button>
        <h1 className="font-bold flex-1 text-center">Bildirishnomalar</h1>
        {unread > 0 && (
          <button
            onClick={() => markAllRead.mutate()}
            className="text-xs text-rose-500 font-semibold"
          >
            Hammasini o'qish
          </button>
        )}
      </div>

      {notifs.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-[60vh] text-center p-8">
          <Bell className="w-16 h-16 text-dark-300 mb-4" />
          <h2 className="text-xl font-bold mb-2">Hali bildirishnoma yo'q</h2>
          <p className="text-sm text-dark-500">Yangi match va xabarlar bu yerda ko'rinadi</p>
        </div>
      ) : (
        <div className="divide-y divide-dark-200 dark:divide-dark-800">
          {notifs.map((n: any, i: number) => {
            const { icon: Icon, color } = getIcon(n.type);
            return (
              <motion.div
                key={n.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className={`p-4 flex gap-3 ${!n.is_read ? "bg-rose-500/5" : ""}`}
              >
                <div className={`w-10 h-10 rounded-full bg-gradient-to-r ${color} flex items-center justify-center flex-shrink-0`}>
                  <Icon className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <h3 className="font-semibold text-sm">{n.title}</h3>
                    <span className="text-xs text-dark-500 flex-shrink-0">{timeAgo(n.created_at)}</span>
                  </div>
                  <p className="text-sm text-dark-500 truncate">{n.body}</p>
                </div>
                {!n.is_read && <div className="w-2 h-2 rounded-full bg-rose-500 mt-2" />}
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
