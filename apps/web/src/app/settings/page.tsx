"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Moon, Sun, Globe, Bell, Shield, ChevronRight } from "lucide-react";
import { useThemeStore } from "@/store/theme";
import { userAPI } from "@/lib/api";
import toast from "react-hot-toast";

export default function SettingsPage() {
  const router = useRouter();
  const { theme, setTheme } = useThemeStore();
  const [lang, setLang] = useState("uz");

  const handleLangChange = async (l: string) => {
    setLang(l);
    try {
      await userAPI.setLanguage(l);
      toast.success("Til o'zgartirildi");
    } catch {
      toast.error("Xatolik");
    }
  };

  return (
    <div className="min-h-screen safe-top safe-bottom">
      <div className="sticky top-0 z-10 bg-white/80 dark:bg-dark-950/80 backdrop-blur-xl border-b border-dark-200 dark:border-dark-800 px-4 py-3 flex items-center gap-3">
        <button onClick={() => router.back()}>←</button>
        <h1 className="font-bold flex-1 text-center">Sozlamalar</h1>
      </div>

      <div className="p-4 space-y-2">
        <Section title="Mavzu">
          <div className="grid grid-cols-3 gap-2 p-3">
            {[{ k: "dark", l: "Qorong'i", I: Moon }, { k: "light", l: "Yorug'", I: Sun }, { k: "auto", l: "Auto", I: Globe }].map((t) => (
              <button key={t.k} onClick={() => setTheme(t.k as any)} className={`py-3 rounded-xl font-semibold text-sm ${theme === t.k ? "bg-rose-500 text-white" : "bg-dark-100 dark:bg-dark-800"}`}>
                <t.I className="w-4 h-4 inline mr-1" />{t.l}
              </button>
            ))}
          </div>
        </Section>

        <Section title="Til">
          <div className="grid grid-cols-3 gap-2 p-3">
            {[{ k: "uz", l: "O'zbek" }, { k: "ru", l: "Русский" }, { k: "en", l: "English" }].map((l) => (
              <button key={l.k} onClick={() => handleLangChange(l.k)} className={`py-3 rounded-xl font-semibold text-sm ${lang === l.k ? "bg-rose-500 text-white" : "bg-dark-100 dark:bg-dark-800"}`}>{l.l}</button>
            ))}
          </div>
        </Section>

        <Item icon={Bell} title="Bildirishnomalar" onClick={() => toast("Tez kunda")} />
        <Item icon={Shield} title="Maxfiylik" onClick={() => toast("Tez kunda")} />
        <Item icon={Globe} title="Yordam" onClick={() => toast("Tez kunda")} />
      </div>
    </div>
  );
}

function Section({ title, children }: any) {
  return (
    <div className="card overflow-hidden">
      <div className="px-4 py-2 text-xs font-bold text-dark-500 uppercase border-b border-dark-200 dark:border-dark-800">{title}</div>
      {children}
    </div>
  );
}

function Item({ icon: Icon, title, onClick }: any) {
  return (
    <button onClick={onClick} className="w-full card p-4 flex items-center gap-3 active:scale-[0.98]">
      <Icon className="w-5 h-5 text-dark-500" />
      <span className="flex-1 text-left font-semibold text-sm">{title}</span>
      <ChevronRight className="w-4 h-4 text-dark-400" />
    </button>
  );
}
