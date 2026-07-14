"use client";

import { createContext, useContext, useEffect, useState } from "react";

interface TelegramContextType {
  tg: any;
  initData: string;
  user: any;
  colorScheme: "light" | "dark";
  isReady: boolean;
}

const Ctx = createContext<TelegramContextType>({
  tg: null, initData: "", user: null, colorScheme: "dark", isReady: false,
});

export function TelegramProvider({ children }: { children: React.ReactNode }) {
  const [tg, setTg] = useState<any>(null);
  const [initData, setInitData] = useState("");
  const [user, setUser] = useState<any>(null);
  const [colorScheme, setColorScheme] = useState<"light" | "dark">("dark");
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const t = (window as any).Telegram?.WebApp;
    if (t) {
      t.ready();
      t.expand();
      setTg(t);
      setInitData(t.initData || "");
      setUser(t.initDataUnsafe?.user || null);
      setColorScheme(t.colorScheme || "dark");
      t.onEvent("themeChanged", () => setColorScheme(t.colorScheme || "dark"));
    } else if (process.env.NODE_ENV === "development") {
      setInitData("user=" + encodeURIComponent(JSON.stringify({ id: 123456789, first_name: "Dev" })) + "&auth_date=" + Math.floor(Date.now() / 1000) + "&hash=mock");
      setUser({ id: 123456789, first_name: "Dev", username: "dev_user", language_code: "uz" });
    }
    setIsReady(true);
  }, []);

  return <Ctx.Provider value={{ tg, initData, user, colorScheme, isReady }}>{children}</Ctx.Provider>;
}

export const useTg = () => useContext(Ctx);
