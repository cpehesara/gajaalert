/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        panel: '#0f1613',
        panelBorder: '#22302a',
        base: '#0a0f0d',
        accent: '#f5b942',
        accentSoft: '#e0a93c',
        risk: {
          critical: '#e05a4f',
          high: '#e0a93c',
          moderate: '#e0c93c',
          low: '#5fbf82'
        },
        textPrimary: '#eaf2ee',
        textMuted: '#8fa39a'
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace']
      }
    }
  },
  plugins: []
}
