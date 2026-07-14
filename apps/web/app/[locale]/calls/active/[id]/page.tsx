"use client";
import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Mic, MicOff, Video, VideoOff, PhoneOff, Volume2, VolumeX } from "lucide-react";
import { useTelegram } from "@/hooks/useTelegram";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useTranslation } from "@/i18n";

export default function CallActivePage({ params }: { params: { id: string } }) {
  const [muted, setMuted] = useState(false);
  const [video, setVideo] = useState(true);
  const [speaker, setSpeaker] = useState(true);
  const [duration, setDuration] = useState(0);
  const [status, setStatus] = useState<"connecting" | "ongoing" | "ended">("connecting");
  const t = useTranslation();
  const { haptic } = useTelegram();
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const ws = useWebSocket();

  useEffect(() => {
    // Get user media
    navigator.mediaDevices
      .getUserMedia({ video: true, audio: true })
      .then((stream) => {
        if (localVideoRef.current) {
          localVideoRef.current.srcObject = stream;
        }
        setStatus("ongoing");
      })
      .catch((err) => {
        console.error("Media access denied:", err);
        setStatus("ended");
      });

    const timer = setInterval(() => setDuration((d) => d + 1), 1000);
    return () => clearInterval(timer);
  }, []);

  const endCall = () => {
    haptic.impact("heavy");
    const stream = localVideoRef.current?.srcObject as MediaStream;
    stream?.getTracks().forEach((track) => track.stop());
    setStatus("ended");
    setTimeout(() => history.back(), 500);
  };

  const toggleMute = () => {
    setMuted(!muted);
    const stream = localVideoRef.current?.srcObject as MediaStream;
    stream?.getAudioTracks().forEach((t) => (t.enabled = muted));
    haptic.impact("light");
  };

  const toggleVideo = () => {
    setVideo(!video);
    const stream = localVideoRef.current?.srcObject as MediaStream;
    stream?.getVideoTracks().forEach((t) => (t.enabled = video));
    haptic.impact("light");
  };

  const formatTime = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m.toString().padStart(2, "0")}:${sec.toString().padStart(2, "0")}`;
  };

  if (status === "ended") {
    return (
      <div className="h-screen flex items-center justify-center bg-slate-900 text-white">
        <div className="text-center">
          <h2 className="text-2xl mb-4">Qo'ng'iroq tugadi</h2>
          <button onClick={() => history.back()} className="px-6 py-2 bg-rose-500 rounded-full">
            Ortga
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-slate-900 relative overflow-hidden">
      <video ref={localVideoRef} autoPlay muted playsInline className="absolute inset-0 w-full h-full object-cover" />
      <div className="absolute top-4 left-4 right-4 flex justify-between items-center text-white z-10">
        <div className="px-3 py-1.5 bg-black/30 backdrop-blur rounded-full text-sm">
          {status === "ongoing" ? formatTime(duration) : "Ulanmoqda..."}
        </div>
        <div className="px-3 py-1.5 bg-red-500 rounded-full text-sm flex items-center gap-1">
          <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
          LIVE
        </div>
      </div>
      <div className="absolute bottom-0 left-0 right-0 pb-8 pt-12 bg-gradient-to-t from-black/80 to-transparent">
        <div className="flex justify-center items-center gap-4 px-4">
          <motion.button
            whileTap={{ scale: 0.9 }}
            onClick={toggleMute}
            className={`w-14 h-14 rounded-full flex items-center justify-center ${
              muted ? "bg-white text-slate-900" : "bg-white/20 backdrop-blur text-white"
            }`}
          >
            {muted ? <MicOff size={24} /> : <Mic size={24} />}
          </motion.button>
          <motion.button
            whileTap={{ scale: 0.9 }}
            onClick={toggleVideo}
            className={`w-14 h-14 rounded-full flex items-center justify-center ${
              !video ? "bg-white text-slate-900" : "bg-white/20 backdrop-blur text-white"
            }`}
          >
            {video ? <Video size={24} /> : <VideoOff size={24} />}
          </motion.button>
          <motion.button
            whileTap={{ scale: 0.9 }}
            onClick={endCall}
            className="w-16 h-16 rounded-full bg-red-500 flex items-center justify-center"
          >
            <PhoneOff size={28} className="text-white" />
          </motion.button>
          <motion.button
            whileTap={{ scale: 0.9 }}
            onClick={() => setSpeaker(!speaker)}
            className={`w-14 h-14 rounded-full flex items-center justify-center ${
              !speaker ? "bg-white text-slate-900" : "bg-white/20 backdrop-blur text-white"
            }`}
          >
            {speaker ? <Volume2 size={24} /> : <VolumeX size={24} />}
          </motion.button>
        </div>
      </div>
    </div>
  );
}
