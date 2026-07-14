import axios, { AxiosInstance } from "axios";
import { useAuthStore } from "@/store/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api: AxiosInstance = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  if (typeof window !== "undefined" && (window as any).Telegram?.WebApp?.initData) {
    config.headers["X-Telegram-Init-Data"] = (window as any).Telegram.WebApp.initData;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().clear();
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  telegram: (init_data: string, device_id?: string) =>
    api.post("/auth/telegram", { init_data, device_id, webapp_version: "1.0.0" }).then((r) => r.data),
  me: () => api.get("/auth/me").then((r) => r.data),
  logout: () => api.post("/auth/logout").then((r) => r.data),
};

export const userAPI = {
  getMe: () => api.get("/users/me").then((r) => r.data),
  updateMe: (data: any) => api.patch("/users/me", data).then((r) => r.data),
  updateLocation: (latitude: number, longitude: number) =>
    api.post("/users/me/location", { latitude, longitude }).then((r) => r.data),
  setLanguage: (language: string) => api.post(`/users/me/language?language=${language}`).then((r) => r.data),
  setTheme: (theme: string) => api.post(`/users/me/theme?theme=${theme}`).then((r) => r.data),
  getUser: (public_id: string) => api.get(`/users/${public_id}`).then((r) => r.data),
  block: (data: { blocked_id: number; reason?: string }) => api.post("/users/block", data).then((r) => r.data),
  unblock: (user_id: number) => api.delete(`/users/block/${user_id}`).then((r) => r.data),
};

export const discoverAPI = {
  list: (params: any) => api.get("/discover", { params }).then((r) => r.data),
  swipe: (target_user_id: number, action: "like" | "pass" | "superlike") =>
    api.post("/discover/swipe", { target_user_id, action }).then((r) => r.data),
  getMatches: () => api.get("/discover/matches").then((r) => r.data),
  unmatch: (match_id: number) => api.delete(`/discover/matches/${match_id}`).then((r) => r.data),
};

export const chatAPI = {
  list: () => api.get("/chats").then((r) => r.data),
  create: (other_user_id: number) => api.post(`/chats/${other_user_id}`).then((r) => r.data),
  getMessages: (chat_id: number, before?: string, limit = 50) =>
    api.get(`/chats/${chat_id}/messages`, { params: { before, limit } }).then((r) => r.data),
  sendMessage: (chat_id: number, data: any) => api.post(`/chats/${chat_id}/messages`, data).then((r) => r.data),
  markRead: (chat_id: number) => api.post(`/chats/${chat_id}/read`).then((r) => r.data),
  typing: (chat_id: number, is_typing: boolean) => api.post(`/chats/${chat_id}/typing`, null, { params: { is_typing } }).then((r) => r.data),
  editMessage: (message_id: number, content: string) => api.patch(`/chats/messages/${message_id}`, { content }).then((r) => r.data),
  deleteMessage: (message_id: number, for_everyone = false) => api.delete(`/chats/messages/${message_id}`, { params: { for_everyone } }).then((r) => r.data),
};

export const notificationAPI = {
  list: (params: { limit?: number; offset?: number } = {}) => api.get("/notifications", { params }).then((r) => r.data),
  unreadCount: () => api.get("/notifications/unread-count").then((r) => r.data),
  markRead: (ids?: number[]) => api.post("/notifications/read", ids || []).then((r) => r.data),
  markAllRead: () => api.post("/notifications/read-all").then((r) => r.data),
};

export const premiumAPI = {
  status: () => api.get("/premium/status").then((r) => r.data),
  plans: () => api.get("/premium/plans").then((r) => r.data),
  boost: () => api.post("/premium/boost").then((r) => r.data),
  verifyPayment: (data: { tier: string; duration_days: number; price_stars: number; payment_id: string }) =>
    api.post("/premium/verify-payment", null, { params: data }).then((r) => r.data),
};

export const reportAPI = {
  create: (data: any) => api.post("/reports", data).then((r) => r.data),
  my: () => api.get("/reports/my").then((r) => r.data),
};

export const mediaAPI = {
  upload: (file: File, type: string, onProgress?: (e: ProgressEvent) => void) => {
    const form = new FormData();
    form.append("file", file);
    form.append("type", type);
    return api.post("/media/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (e) => onProgress && e.total && onProgress(e),
    }).then((r) => r.data);
  },
  delete: (id: number) => api.delete(`/media/${id}`).then((r) => r.data),
};
