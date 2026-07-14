"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, ArrowLeft, Camera } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { userAPI, mediaAPI } from "@/lib/api";
import { useAuthStore } from "@/store/auth";
import { SmartImage } from "@/components/ui/image";
import { Spinner } from "@/components/ui/spinner";
import { calculateAge } from "@/lib/utils";

const INTERESTS = ["Musiqa", "Sport", "O'yinlar", "Kitob", "Sayohat", "Ovqat", "Kino", "Foto", "Texnologiya", "Hayvonlar", "San'at", "Raqs", "Tabiat", "Pishiriq", "Fitnes", "Teatr", "Avtomobil", "Biznes", "Tillar"];

const REGIONS = ["Toshkent", "Samarqand", "Buxoro", "Andijon", "Farg'ona", "Namangan", "Qashqadaryo", "Surxondaryo", "Jizzax", "Sirdaryo", "Navoiy", "Xorazm", "Qoraqalpog'iston"];

export default function ProfileSetupScreen() {
  const { setProfileComplete } = useAuthStore();
  const [step, setStep] = useState(0);
  const [data, setData] = useState({
    nickname: "",
    birth_date: "",
    gender: "",
    looking_for: "everyone",
    region: "",
    city: "",
    bio: "",
    interests: [] as string[],
    photos: [] as string[],
  });
  const [uploading, setUploading] = useState(false);

  const updateMutation = useMutation({
    mutationFn: (payload: any) => userAPI.updateMe(payload),
    onSuccess: () => {
      toast.success("Profil saqlandi!");
      setProfileComplete(true);
    },
    onError: (e: any) => toast.error(e.response?.data?.detail || "Xatolik"),
  });

  const totalSteps = 5;
  const canNext = () => {
    if (step === 0) return data.nickname.length >= 3;
    if (step === 1) return data.birth_date && data.gender;
    if (step === 2) return data.region;
    if (step === 3) return data.interests.length >= 3;
    if (step === 4) return data.photos.length >= 1;
    return true;
  };

  const handleNext = () => {
    if (step < totalSteps - 1) {
      setStep(step + 1);
    } else {
      updateMutation.mutate({ ...data, birth_date: new Date(data.birth_date).toISOString().split("T")[0] });
    }
  };

  const handlePhotoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const res = await mediaAPI.upload(file, "photo");
      setData({ ...data, photos: [...data.photos, res.url] });
    } catch {
      toast.error("Yuklashda xatolik");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="flex h-screen flex-col safe-top safe-bottom">
      <div className="px-6 pt-4">
        <div className="flex gap-1">
          {Array.from({ length: totalSteps }).map((_, i) => (
            <div key={i} className={`flex-1 h-1 rounded-full transition ${i <= step ? "bg-rose-500" : "bg-dark-200 dark:bg-dark-800"}`} />
          ))}
        </div>
        <p className="text-xs text-dark-500 mt-2">Qadam {step + 1}/{totalSteps}</p>
      </div>

      <div className="flex-1 overflow-y-auto no-scrollbar p-6">
        <AnimatePresence mode="wait">
          <motion.div key={step} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} transition={{ duration: 0.2 }} className="h-full">
            {step === 0 && (
              <div className="space-y-4">
                <h2 className="text-2xl font-bold">Sizni tanishtiring 👋</h2>
                <p className="text-sm text-dark-500">Anonim nickname tanlang</p>
                <input value={data.nickname} onChange={(e) => setData({ ...data, nickname: e.target.value })} placeholder="CoolCat42" maxLength={32} className="input text-lg" />
                <p className="text-xs text-dark-500">{data.nickname.length}/32</p>
              </div>
            )}

            {step === 1 && (
              <div className="space-y-4">
                <h2 className="text-2xl font-bold">Yoshingiz va jinsingiz</h2>
                <div>
                  <label className="text-sm text-dark-500 block mb-2">Tug'ilgan sana</label>
                  <input type="date" value={data.birth_date} onChange={(e) => setData({ ...data, birth_date: e.target.value })} max={new Date(new Date().setFullYear(new Date().getFullYear() - 18)).toISOString().split("T")[0]} className="input" />
                  {data.birth_date && <p className="text-xs text-dark-500 mt-1">{calculateAge(data.birth_date)} yosh</p>}
                </div>
                <div>
                  <label className="text-sm text-dark-500 block mb-2">Jins</label>
                  <div className="grid grid-cols-3 gap-2">
                    {[{ k: "male", l: "Erkak" }, { k: "female", l: "Ayol" }, { k: "other", l: "Boshqa" }].map((g) => (
                      <button key={g.k} onClick={() => setData({ ...data, gender: g.k })} className={`py-3 rounded-xl font-semibold ${data.gender === g.k ? "bg-rose-500 text-white" : "bg-dark-100 dark:bg-dark-800"}`}>{g.l}</button>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="text-sm text-dark-500 block mb-2">Kimni qidiryapsiz?</label>
                  <div className="grid grid-cols-3 gap-2">
                    {[{ k: "male", l: "Erkak" }, { k: "female", l: "Ayol" }, { k: "everyone", l: "Hamma" }].map((o) => (
                      <button key={o.k} onClick={() => setData({ ...data, looking_for: o.k })} className={`py-3 rounded-xl font-semibold ${data.looking_for === o.k ? "bg-pink-500 text-white" : "bg-dark-100 dark:bg-dark-800"}`}>{o.l}</button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-4">
                <h2 className="text-2xl font-bold">Qayerdansiz? 📍</h2>
                <div className="grid grid-cols-2 gap-2 max-h-64 overflow-y-auto">
                  {REGIONS.map((r) => (
                    <button key={r} onClick={() => setData({ ...data, region: r })} className={`p-3 rounded-xl text-sm font-semibold ${data.region === r ? "bg-rose-500 text-white" : "bg-dark-100 dark:bg-dark-800"}`}>{r}</button>
                  ))}
                </div>
                <input value={data.city} onChange={(e) => setData({ ...data, city: e.target.value })} placeholder="Shahar (ixtiyoriy)" className="input" />
              </div>
            )}

            {step === 3 && (
              <div className="space-y-4">
                <h2 className="text-2xl font-bold">Qiziqishlaringiz 🎯</h2>
                <p className="text-sm text-dark-500">Kamida 3 ta tanlang</p>
                <div className="flex flex-wrap gap-2">
                  {INTERESTS.map((tag) => (
                    <button key={tag} onClick={() => { const next = data.interests.includes(tag) ? data.interests.filter((t) => t !== tag) : [...data.interests, tag]; setData({ ...data, interests: next }); }} className={`px-3 py-2 rounded-full text-sm font-medium ${data.interests.includes(tag) ? "bg-rose-500 text-white" : "bg-dark-100 dark:bg-dark-800"}`}>{tag}</button>
                  ))}
                </div>
                <textarea value={data.bio} onChange={(e) => setData({ ...data, bio: e.target.value })} placeholder="Bio (ixtiyoriy)" maxLength={500} className="input min-h-[100px]" />
              </div>
            )}

            {step === 4 && (
              <div className="space-y-4">
                <h2 className="text-2xl font-bold">Rasmlar 📸</h2>
                <p className="text-sm text-dark-500">Kamida 1 ta rasm qo'shing</p>
                <div className="grid grid-cols-3 gap-2">
                  {data.photos.map((p, i) => (
                    <div key={i} className="relative aspect-square rounded-xl overflow-hidden">
                      <SmartImage src={p} className="h-full w-full" />
                      <button onClick={() => setData({ ...data, photos: data.photos.filter((_, idx) => idx !== i) })} className="absolute top-1 right-1 w-6 h-6 bg-black/50 text-white rounded-full text-xs">✕</button>
                    </div>
                  ))}
                  {data.photos.length < 6 && (
                    <label className="aspect-square rounded-xl border-2 border-dashed border-dark-300 dark:border-dark-700 flex flex-col items-center justify-center gap-1 cursor-pointer">
                      {uploading ? <Spinner size="md" /> : <Camera className="w-6 h-6" />}
                      <span className="text-xs">Qo'shish</span>
                      <input type="file" accept="image/*" onChange={handlePhotoUpload} className="hidden" />
                    </label>
                  )}
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="px-6 pb-6 flex gap-3 safe-bottom">
        {step > 0 && <button onClick={() => setStep(step - 1)} className="btn-secondary px-6"><ArrowLeft className="w-4 h-4" /></button>}
        <button onClick={handleNext} disabled={!canNext() || updateMutation.isPending} className="btn-primary flex-1">
          {updateMutation.isPending ? <Spinner size="sm" /> : step === totalSteps - 1 ? "Tayyor ✓" : "Davom etish"}
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
