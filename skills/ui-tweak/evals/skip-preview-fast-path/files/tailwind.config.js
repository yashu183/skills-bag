export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: { brand: { 50: "#eef4ff", 500: "#3b5bfd", 600: "#2b45e0", 900: "#141b4d" }, ink: "#0f172a" },
      borderRadius: { card: "14px" },
      fontFamily: { sans: ["Inter", "system-ui", "sans-serif"] },
    },
  },
};
