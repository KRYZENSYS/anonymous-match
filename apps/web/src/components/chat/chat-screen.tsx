"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Send, MoreVertical, Smile, Image as ImageIcon, Mic, Heart } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { chatAPI } from "@/lib/api";
import { useWebSocket } from "@/hooks/useWebSocket";
import { formatTime } from "@/lib/utils";
import { SmartImage } from "@/components/ui/image";
import { useAuthStore } from "@/store/auth";
import { Spinner } from "@/components/ui/spinner";

export default function ChatScreen() {
  const router = useRouter();
  const params = useParams();
  const chatId = parseInt(params.id as string);
  const myUserId = useAuthStore((s) => s.userId);
  const qc = useQueryClient();
  const [text, setText] = useState("");
  const [messages, setMessages] = useState<any[]>([]);
  const [otherTyping, setOtherTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout>();

  const { isConnected, lastMessage, send } = useWebSocket(`/ws/connect`);

  const { data: chatData, isLoading } = useQuery({
    queryKey: ["chat", chatId],
    queryFn: () => chatAPI.getMessages(chatId, undefined, 100),
  });

  // Load initial messages
  useEffect(() => {
    if (chatData?.messages) {
      setMessages(chatData.messages);
    }
  }, [chatData]);

  // WebSocket messages
  useEffect(() => {
    if (!lastMessage) return;
    if (lastMessage.type === "message" && lastMessage.data?.chat_id === chatId) {
      setMessages((prev) => {
        const exists = prev.find((m) => m.id === lastMessage.data.id);
        if (exists) return prev;
        return [...prev, lastMessage.data];
      });
      // Mark as read
      send({ type: "read", chat_id: chatId });
    } else if (lastMessage.type === "typing" && lastMessage.data?.chat_id === chatId) {
      if (lastMessage.data.user_id !== myUserId) {
        setOtherTyping(lastMessage.data.is_typing);
        if (lastMessage.data.is_typing) {
          if (typingTimeoutRef.current) clearTimeout(typingTimeoutRef.current);
          typingTimeoutRef.current = setTimeout(() => setOtherTyping(false), 3000);
        }
      }
    }
  }, [lastMessage, chatId, myUserId, send]);

  // Auto-scroll
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const sendMutation = useMutation({
    mutationFn: (data: { type: string; content?: string }) => chatAPI.sendMessage(chatId, data),
    onSuccess: (newMsg) => {
      setMessages((prev) => [...prev, newMsg]);
      setText("");
    },
  });

  const handleSend = () => {
    if (!text.trim()) return;
    sendMutation.mutate({ type: "text", content: text.trim() });
  };

  const handleTyping = (value: string) => {
    setText(value);
    send({ type: "typing", chat_id: chatId, is_typing: value.length > 0 });
  };

  if (isLoading) {
    return <div className="flex h-screen items-center justify-center"><Spinner size="lg" /></div>;
  }

  const otherUser = chatData?.messages?.[0]?.sender_public_id ? null : null; // TODO

  return (
    <div className="flex h-screen flex-col bg-gradient-to-b from-rose-500/5 to-pink-500/5">
      {/* Header */}
      <header className="flex items-center gap-3 px-4 py-3 border-b border-dark-200 dark:border-dark-800 bg-white/80 dark:bg-dark-950/80 backdrop-blur-xl safe-top">
        <button onClick={() => router.back()} className="p-2 -ml-2">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="relative w-10 h-10 rounded-full overflow-hidden bg-dark-200">
          <SmartImage className="h-full w-full" fallback="👤" />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-sm">Match</h3>
          <p className="text-xs text-green-500">
            {isConnected ? (otherTyping ? "yozmoqda..." : "online") : "ulanmoqda..."}
          </p>
        </div>
        <button className="p-2">
          <MoreVertical className="w-5 h-5" />
        </button>
      </header>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-2 no-scrollbar">
        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} myUserId={myUserId} />
          ))}
        </AnimatePresence>

        {otherTyping && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex justify-start">
            <div className="bg-white dark:bg-dark-800 rounded-2xl px-4 py-2 flex gap-1">
              <span className="w-2 h-2 bg-dark-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
              <span className="w-2 h-2 bg-dark-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
              <span className="w-2 h-2 bg-dark-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
            </div>
          </motion.div>
        )}
      </div>

      {/* Quick replies */}
      <div className="px-4 py-2 flex gap-2 overflow-x-auto no-scrollbar">
        {["Salom! 👋", "Qanday?", "😊", "Qayerdansan?"].map((q) => (
          <button
            key={q}
            onClick={() => setText(q)}
            className="flex-shrink-0 px-4 py-2 bg-white dark:bg-dark-800 rounded-full text-sm border border-dark-200 dark:border-dark-700"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input */}
      <div className="border-t border-dark-200 dark:border-dark-800 bg-white dark:bg-dark-950 p-2 flex items-center gap-2 safe-bottom">
        <button className="p-2 text-dark-500">
          <ImageIcon className="w-5 h-5" />
        </button>
        <input
          value={text}
          onChange={(e) => handleTyping(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Xabar yozing..."
          className="flex-1 bg-dark-100 dark:bg-dark-900 rounded-full px-4 py-2 outline-none"
        />
        <button className="p-2 text-dark-500">
          <Mic className="w-5 h-5" />
        </button>
        <button
          onClick={handleSend}
          disabled={!text.trim() || sendMutation.isPending}
          className="p-2 bg-gradient-to-r from-rose-500 to-pink-500 text-white rounded-full disabled:opacity-50"
        >
          <Send className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}

function MessageBubble({ message, myUserId }: { message: any; myUserId: number | null }) {
  const isMine = message.is_mine || message.sender_id === myUserId;
  return (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className={`flex ${isMine ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`max-w-[75%] px-4 py-2 rounded-2xl ${
          isMine
            ? "bg-gradient-to-r from-rose-500 to-pink-500 text-white rounded-br-sm"
            : "bg-white dark:bg-dark-800 rounded-bl-sm"
        }`}
      >
        {message.type === "text" && <p className="text-sm break-words">{message.content}</p>}
        {message.type === "image" && message.media && (
          <SmartImage src={message.media.url} className="rounded-lg max-w-full" />
        )}
        {message.is_edited && <span className="text-[10px] opacity-60">(tahrirlangan)</span>}
        <div className={`text-[10px] mt-1 ${isMine ? "text-white/70" : "text-dark-500"} text-right`}>
          {formatTime(message.created_at)}
          {isMine && (message.read_at ? " ✓✓" : " ✓")}
        </div>
      </div>
    </motion.div>
  );
}
