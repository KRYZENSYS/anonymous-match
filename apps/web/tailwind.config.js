/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Brand
        brand: {
          50: "#fef2f2",
          100: "#fee2e2",
          500: "#ef4444",
          600: "#dc2626",
          700: "#b91c1c",
        },
        rose: {
          400: "#fb7185",
          500: "#f43f5e",
          600: "#e11d48",
        },
        pink: {
          400: "#f472b6",
          500: "#ec4899",
          600: "#db2777",
        },
        // Dark mode base
        dark: {
          50: "#f8fafc",
          100: "#f1f5f9",
          200: "#e2e8f0",
          300: "#cbd5e1",
          400: "#94a3b8",
          500: "#64748b",
          600: "#475569",
          700: "#334155",
          800: "#1e293b",
          900: "#0f172a",
          950: "#020617",
        },
        // Premium tiers
        gold: "#fbbf24",
        platinum: "#cbd5e1",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["SF Pro Display", "system-ui", "sans-serif"],
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-in-out",
        "slide-up": "slideUp 0.3s ease-out",
        "slide-down": "slideDown 0.3s ease-out",
        "scale-in": "scaleIn 0.2s ease-out",
        "pulse-glow": "pulseGlow 2s ease-in-out infinite",
        "shimmer": "shimmer 2s linear infinite",
        "swipe-right": "swipeRight 0.5s ease-out",
        "swipe-left": "swipeLeft 0.5s ease-out",
        "match-burst": "matchBurst 0.8s ease-out",
        "heart-beat": "heartBeat 1.3s ease-in-out infinite",
      },
      keyframes: {
        fadeIn: { "0%": { opacity: "0" }, "100%": { opacity: "1" } },
        slideUp: { "0%": { transform: "translateY(20px)", opacity: "0" }, "100%": { transform: "translateY(0)", opacity: "1" } },
        slideDown: { "0%": { transform: "translateY(-20px)", opacity: "0" }, "100%": { transform: "translateY(0)", opacity: "1" } },
        scaleIn: { "0%": { transform: "scale(0.9)", opacity: "0" }, "100%": { transform: "scale(1)", opacity: "1" } },
        pulseGlow: { "0%, 100%": { boxShadow: "0 0 0 0 rgba(239, 68, 68, 0.7)" }, "50%": { boxShadow: "0 0 0 20px rgba(239, 68, 68, 0)" } },
        shimmer: { "0%": { backgroundPosition: "-1000px 0" }, "100%": { backgroundPosition: "1000px 0" } },
        swipeRight: { "0%": { transform: "translateX(0) rotate(0deg)" }, "100%": { transform: "translateX(150%) rotate(30deg)", opacity: "0" } },
        swipeLeft: { "0%": { transform: "translateX(0) rotate(0deg)" }, "100%": { transform: "translateX(-150%) rotate(-30deg)", opacity: "0" } },
        matchBurst: { "0%": { transform: "scale(0)", opacity: "0" }, "50%": { transform: "scale(1.2)" }, "100%": { transform: "scale(1)", opacity: "1" } },
        heartBeat: { "0%, 100%": { transform: "scale(1)" }, "25%": { transform: "scale(1.1)" }, "50%": { transform: "scale(1)" }, "75%": { transform: "scale(1.1)" } },
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic": "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
        "hero-pattern": "linear-gradient(135deg, #ef4444 0%, #ec4899 50%, #f43f5e 100%)",
      },
    },
  },
  plugins: [],
};
