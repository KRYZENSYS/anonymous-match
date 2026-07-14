"use client";

import { useState } from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";

interface SmartImageProps {
  src?: string | null;
  alt?: string;
  className?: string;
  fallback?: React.ReactNode;
}

export function SmartImage({ src, alt = "", className, fallback }: SmartImageProps) {
  const [errored, setErrored] = useState(false);

  if (!src || errored) {
    return (
      <div className={cn("flex items-center justify-center bg-gradient-to-br from-rose-500/20 to-pink-500/20 text-4xl", className)}>
        {fallback || "👤"}
      </div>
    );
  }

  return (
    <Image
      src={src}
      alt={alt}
      fill
      className={cn("object-cover", className)}
      onError={() => setErrored(true)}
      unoptimized
    />
  );
}
