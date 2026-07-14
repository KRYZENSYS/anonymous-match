"use client";

import { useEffect, useState } from "react";
import { useTelegram } from "@/hooks/useTelegram";
import { useAuthStore } from "@/store/auth";
import { authAPI } from "@/lib/api";
import { Spinner } from "@/components/ui/spinner";
import OnboardingScreen from "@/components/screens/onboarding";
import MainScreen from "@/components/screens/main";
import ProfileSetupScreen from "@/components/screens/profile-setup";

export default function Home() {
  const { tg, isReady, initData, user: tgUser } = useTelegram();
  const { token, setAuth, isProfileComplete, isInitialized } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isReady) return;
    if (!initData) {
      setError("Telegram WebApp ochilmadi. Iltimos bot orqali kiring.");
      setLoading(false);
      return;
    }

    // Auto-auth via Telegram initData
    authAPI.telegram(initData)
      .then((res) => {
        setAuth(res.access_token, res.user_id, res.public_id, res.is_profile_complete, res.needs_profile_setup);
      })
      .catch((err) => {
        console.error("Auth error", err);
        setError("Autentifikatsiya xatosi: " + (err.response?.data?.detail || err.message));
      })
      .finally(() => setLoading(false));
  }, [isReady, initData, setAuth]);

  useEffect(() => {
    // Telegram WebApp sozlamalari
    if (tg) {
      tg.ready();
      tg.expand();
      tg.setHeaderColor(tg.colorScheme === "dark" ? "#020617" : "#ffffff");
      tg.setBottomBarColor(tg.colorScheme === "dark" ? "#020617" : "#ffffff");
    }
  }, [tg]);

  if (loading || !isInitialized) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center p-6 text-center">
        <div className="space-y-4">
          <div className="text-6xl">😔</div>
          <p className="text-lg">{error}</p>
          <p className="text-sm text-dark-500">Telegram bot orqali qayta kiring: @AnonymousMatchBot</p>
        </div>
      </div>
    );
  }

  if (!token) {
    return <OnboardingScreen />;
  }

  if (!isProfileComplete) {
    return <ProfileSetupScreen />;
  }

  return <MainScreen />;
}
