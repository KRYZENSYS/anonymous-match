"use client";

import { useEffect, useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import { TelegramProvider } from "@/components/providers/telegram-provider";
import { AuthHydrator } from "@/components/providers/auth-hydrator";
import { ThemeProvider } from "@/components/providers/theme-provider";

export function Providers({ children }: { children: React.ReactNode }) {
  const [client] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60_000,
        refetchOnWindowFocus: false,
        retry: 1,
      },
    },
  }));

  return (
    <QueryClientProvider client={client}>
      <ThemeProvider>
        <TelegramProvider>
          <AuthHydrator />
          {children}
          <Toaster
            position="top-center"
            toastOptions={{
              duration: 3000,
              style: {
                background: "rgb(var(--color-card))",
                color: "rgb(var(--color-fg))",
                border: "1px solid rgb(var(--color-border))",
                borderRadius: "12px",
                fontSize: "14px",
              },
            }}
          />
        </TelegramProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
