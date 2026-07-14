"use client";

import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import toast from "react-hot-toast";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (typeof window !== "undefined") {
    const tg = (window as any).Telegram?.WebApp;
    const initData = tg?.initData || "";
    config.headers["X-Telegram-Init-Data"] = initData;
    const token = localStorage.getItem("am_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err: AxiosError<{ detail: string }>) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("am_token");
    } else if (err.response?.status === 429) {
      toast.error("Juda ko'p so'rov");
    }
    return Promise.reject(err);
  }
);

export const authAPI = {
  telegram: (initData: string) => api.post("/auth/telegram", { init_data: initData }).then((r) => r.data),
  me: () => api.get("/auth/me").then((r) => r.data),
  logout: () => api.post("/auth/logout").then((r) => r.data),
};

export const userAPI = {
  getMe: () => api.get("/users/me").then((r) => r.data),
  updateMe: (data: any) => api.patch("/users/me", data).then((r) => r.data),
  updateLocation: (lat: number, lon: number) => api.post("/users/me/location", { lat, lon }).then((r) => r.data),
  setLanguage: (lang: string) => api.post("/users/me/language", { language_code: lang }).then((r) => r.data),
};

export const discoverAPI = {
  list: (params?: any) => api.get("/discover", { params }).then((r) => r.data),
  swipe: (target_user_id: number, action: "like" | "pass" | "superlike") => api.post("/discover/swipe", { target_user_id, action }).then((r) => r.data),
  matches: () => api.get("/discover/matches").then((r) => r.data),
};

export const chatAPI = {
  list: () => api.get("/chats").then((r) => r.data),
  get: (id: number) => api.get(`/chats/${id}`).then((r) => r.data),
  getMessages: (id: number, before_id?: number, limit = 50) => api.get(`/chats/${id}/messages`, { params: { before_id, limit } }).then((r) => r.data),
  sendMessage: (id: number, data: { type: string; content?: string; media_url?: string }) => api.post(`/chats/${id}/messages`, data).then((r) => r.data),
  markRead: (id: number) => api.post(`/chats/${id}/read`).then((r) => r.data),
};

export const mediaAPI = {
  upload: async (file: File, type: "photo" | "video" | "audio" = "photo") => {
    const form = new FormData();
    form.append("file", file);
    form.append("type", type);
    const { data } = await api.post("/media/upload", form, { headers: { "Content-Type": "multipart/form-data" } });
    return data;
  },
};

export const notificationAPI = {
  list: (params?: any) => api.get("/notifications", { params }).then((r) => r.data),
  markAllRead: () => api.post("/notifications/read-all").then((r) => r.data),
};

export const premiumAPI = {
  plans: () => api.get("/premium/plans").then((r) => r.data),
  status: () => api.get("/premium/status").then((r) => r.data),
  boost: () => api.post("/premium/boost").then((r) => r.data),
};

export const reportAPI = {
  create: (data: { reported_id: number; reason: string; description?: string }) => api.post("/reports", data).then((r) => r.data),
  block: (user_id: number) => api.post(`/users/${user_id}/block`).then((r) => r.data),
};
