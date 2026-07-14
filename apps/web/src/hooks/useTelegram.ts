"use client";

import { useEffect, useState } from "react";

interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  language_code?: string;
  is_premium?: boolean;
}

export function useTelegram() {
  const [tg, setTg] = useState<any>(null);
  const [isReady, setIsReady] = useState(false);
  const [initData, setInitData] = useState<string>("");
  const [user, setUser] = useState<TelegramUser | null>(null);
  const [colorScheme, setColorScheme] = useState<"light" | "dark">("dark");

  useEffect(() => {
    const t = (window as any).Telegram?.WebApp;
    if (!t) {
      // Development uchun mock
      if (process.env.NODE_ENV === "development") {
        const mockInitData = btoa(JSON.stringify({
          user: { id: 123456789, first_name: "Test", username: "test_user", language_code: "uz", is_premium: false },
          auth_date: Math.floor(Date.now() / 1000),
          hash: "mock",
        }));
        setInitData(`user=${encodeURIComponent(JSON.stringify({ id: 123456789, first_name: "Test" }))}&auth_date=${Math.floor(Date.now() / 1000)}&hash=mock`);
        setUser({ id: 123456789, first_name: "Test", username: "test_user", language_code: "uz", is_premium: false });
      }
      setIsReady(true);
      return;
    }

    t.ready();
    t.expand();
    setTg(t);
    setInitData(t.initData || "");
    setUser(t.initDataUnsafe?.user || null);
    setColorScheme(t.colorScheme || "dark");
    setIsReady(true);

    // ColorScheme change listener
    t.onEvent("themeChanged", () => {
      setColorScheme(t.colorScheme || "dark");
    });
  }, []);

  return { tg, isReady, initData, user, colorScheme };
}

export function hapticFeedback(style: "light" | "medium" | "heavy" | "rigid" | "soft" = "medium") {
  if (typeof window === "undefined") return;
  const tg = (window as any).Telegram?.WebApp;
  if (tg?.HapticFeedback) {
    tg.HapticFeedback.impactOccurred(style);
  }
}

export function showAlert(message: string) {
  if (typeof window === "undefined") return;
  const tg = (window as any).Telegram?.WebApp;
  if (tg?.showAlert) tg.showAlert(message);
  else alert(message);
}

export function showConfirm(message: string, callback: (ok: boolean) => void) {
  if (typeof window === "undefined") return;
  const tg = (window as any).Telegram?.WebApp;
  if (tg?.showConfirm) tg.showConfirm(message, callback);
  else callback(confirm(message));
}

export function closeApp() {
  if (typeof window === "undefined") return;
  const tg = (window as any).Telegram?.WebApp;
  if (tg?.close) tg.close();
}

export function openLink(url: string) {
  if (typeof window === "undefined") return;
  const tg = (window as any).Telegram?.WebApp;
  if (tg?.openLink) tg.openLink(url);
  else window.open(url, "_blank");
}
