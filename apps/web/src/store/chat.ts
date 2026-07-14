"use client";

import { create } from "zustand";

interface Message {
  id: number;
  chat_id: number;
  sender_id: number;
  sender_public_id: string;
  type: string;
  content: string | null;
  media?: any;
  reply_to?: any;
  is_edited: boolean;
  is_deleted: boolean;
  is_mine: boolean;
  read_at: string | null;
  delivered_at: string | null;
  created_at: string;
}

interface ChatState {
  onlineUsers: Set<number>;
  typingUsers: Map<number, Set<number>>; // chat_id -> set of user_ids
  setOnline: (userId: number, online: boolean) => void;
  setTyping: (chatId: number, userId: number, isTyping: boolean) => void;
  reset: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  onlineUsers: new Set(),
  typingUsers: new Map(),
  setOnline: (userId, online) =>
    set((s) => {
      const next = new Set(s.onlineUsers);
      if (online) next.add(userId);
      else next.delete(userId);
      return { onlineUsers: next };
    }),
  setTyping: (chatId, userId, isTyping) =>
    set((s) => {
      const next = new Map(s.typingUsers);
      const set = new Set(next.get(chatId) || []);
      if (isTyping) set.add(userId);
      else set.delete(userId);
      if (set.size === 0) next.delete(chatId);
      else next.set(chatId, set);
      return { typingUsers: next };
    }),
  reset: () => set({ onlineUsers: new Set(), typingUsers: new Map() }),
}));
