"use client";

import { cn } from "@/lib/utils";

export function Badge({
  children,
  variant = "default",
  className,
}: {
  children: React.ReactNode;
  variant?: "default" | "gold" | "platinum" | "online" | "verified" | "boost";
  className?: string;
}) {
  const variants = {
    default: "bg-dark-100 dark:bg-dark-800 text-dark-900 dark:text-white",
    gold: "bg-gradient-to-r from-yellow-400 to-yellow-600 text-yellow-900",
    platinum: "bg-gradient-to-r from-slate-300 to-slate-500 text-slate-900",
    online: "bg-green-500 text-white",
    verified: "bg-blue-500 text-white",
    boost: "bg-gradient-to-r from-purple-500 to-pink-500 text-white",
  };
  return <span className={cn("inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold", variants[variant], className)}>{children}</span>;
}
