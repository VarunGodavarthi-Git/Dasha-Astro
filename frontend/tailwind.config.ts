import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./pages/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#18211f",
        brass: "#a16b2d",
        river: "#1f7a8c",
        leaf: "#2f6f4e"
      },
      boxShadow: {
        soft: "0 12px 35px rgba(24, 33, 31, 0.10)"
      }
    }
  },
  plugins: []
};

export default config;

