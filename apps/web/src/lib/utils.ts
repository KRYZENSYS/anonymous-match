import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatTime(date: string | Date) {
  const d = new Date(date);
  return d.toLocaleTimeString("uz-UZ", { hour: "2-digit", minute: "2-digit" });
}

export function formatDate(date: string | Date) {
  const d = new Date(date);
  return d.toLocaleDateString("uz-UZ", { day: "2-digit", month: "short" });
}

export function timeAgo(date: string | Date) {
  const d = new Date(date).getTime();
  const now = Date.now();
  const diff = Math.floor((now - d) / 1000);
  if (diff < 60) return "hozir";
  if (diff < 3600) return `${Math.floor(diff / 60)} daq`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} soat`;
  if (diff < 604800) return `${Math.floor(diff / 86400)} kun`;
  return formatDate(date);
}

export function calculateAge(birthDate: string | Date) {
  const birth = new Date(birthDate);
  const now = new Date();
  let age = now.getFullYear() - birth.getFullYear();
  const m = now.getMonth() - birth.getMonth();
  if (m < 0 || (m === 0 && now.getDate() < birth.getDate())) age--;
  return age;
}

export function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number) {
  if (!lat1 || !lat2) return null;
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) ** 2;
  return Math.round(R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)) * 10) / 10;
}
