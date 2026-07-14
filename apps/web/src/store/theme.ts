"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

type Theme = "dark" | "light" | "auto";

interface ThemeState {
  theme: Theme;
  setTheme: (t: Theme) => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: "dark",
      setTheme: (theme) => {
        set({ theme });
        applyTheme(theme);
      },
    }),
    { name: "anonymous-match-theme" }
  )
);

function applyTheme(t: Theme) {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  if (t === "auto") {
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    root.classList.toggle("dark", prefersDark);
  } else {
    root.classList.toggle("dark", t === "dark");
  }
}

export function initTheme() {
  if (typeof window === "undefined") return;
  const stored = localStorage.getItem("anonymous-match-theme");
  let theme: Theme = "dark";
  if (stored) {
    try {
      theme = JSON.parse(stored).state?.theme || "dark";
    } catch {}
  }
  applyTheme(theme);
}
