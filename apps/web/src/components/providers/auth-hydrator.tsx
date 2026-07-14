"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/store/auth";

export function AuthHydrator() {
  const initialize = useAuthStore((s) => s.initialize);
  useEffect(() => {
    initialize();
  }, [initialize]);
  return null;
}
