/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}', './public/index.html'],
  theme: {
    extend: {
      colors: {
        base: '#0B0F10',       // deep blueprint-black background
        panel: '#12181A',      // panel surface
        line: '#232B2E',       // hairline borders / grid
        line2: '#1A2022',      // subtler internal divider
        signal: '#E8A33D',     // amber — active / CTA / attention
        'signal-dim': '#8A672C',
        patina: '#4C8C7D',     // muted teal-green — connected / success
        'patina-dim': '#2E4E45',
        ink: '#E7E9E4',        // primary text, warm off-white
        'ink-muted': '#8A938F',// secondary text
        'ink-faint': '#565F5C',
        danger: '#C1543C',     // air-gapped / alert amber-red
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      borderRadius: {
        sharp: '2px',
      },
      keyframes: {
        'fade-in-up': {
          '0%': { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        blink: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.35' },
        },
      },
      animation: {
        'fade-in-up': 'fade-in-up 0.28s ease-out',
        blink: 'blink 1.6s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};
