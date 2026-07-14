"use client";

import { useEffect, useState } from "react";
import { userAPI } from "@/lib/api";

export function useLocation() {
  const [coords, setCoords] = useState<{ lat: number; lon: number } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const requestLocation = async () => {
    if (!navigator.geolocation) {
      setError("Geolocation qo'llab-quvvatlanmaydi");
      return;
    }
    setLoading(true);
    setError(null);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        setCoords({ lat, lon });
        try {
          await userAPI.updateLocation(lat, lon);
        } catch (e) {
          console.error("Location update failed", e);
        }
        setLoading(false);
      },
      (err) => {
        setError(err.message);
        setLoading(false);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
    );
  };

  useEffect(() => {
    requestLocation();
  }, []);

  return { coords, error, loading, requestLocation };
}
