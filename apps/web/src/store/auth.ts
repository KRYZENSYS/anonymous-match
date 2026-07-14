"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AuthState {
  token: string | null;
  userId: number | null;
  publicId: string | null;
  isProfileComplete: boolean;
  needsProfileSetup: boolean;
  isInitialized: boolean;
  setAuth: (token: string, userId: number, publicId: string, isComplete: boolean, needsSetup: boolean) => void;
  setProfileComplete: (isComplete: boolean) => void;
  clear: () => void;
  initialize: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      userId: null,
      publicId: null,
      isProfileComplete: false,
      needsProfileSetup: true,
      isInitialized: false,
      setAuth: (token, userId, publicId, isComplete, needsSetup) =>
        set({ token, userId, publicId, isProfileComplete: isComplete, needsProfileSetup: needsSetup, isInitialized: true }),
      setProfileComplete: (isComplete) => set({ isProfileComplete: isComplete, needsProfileSetup: !isComplete }),
      clear: () => set({ token: null, userId: null, publicId: null, isProfileComplete: false, needsProfileSetup: true, isInitialized: true }),
      initialize: () => set({ isInitialized: true }),
    }),
    { name: "anonymous-match-auth" }
  )
);
