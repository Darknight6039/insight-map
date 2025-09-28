/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'glass': {
          'light': 'rgba(255, 255, 255, 0.1)',
          'medium': 'rgba(255, 255, 255, 0.2)',
          'dark': 'rgba(0, 0, 0, 0.1)',
        },
        'primary': '#1a202c',
        'secondary': '#2d3748',
        'accent': '#00a3ff',
        'surface': '#f7fafc',
        'text-primary': '#2d3748',
        'text-secondary': '#718096',
        'text-white': '#ffffff',
        'success': '#38a169',
        'warning': '#ed8936',
        'error': '#e53e3e',
        'axial': {
          'blue': '#1a202c',
          'light-blue': '#2d3748',
          'accent': '#00c2b2',
        }
      },
      backdropBlur: {
        'xs': '2px',
        'glass': '12px',
        'liquid': '24px',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'liquid': 'liquid 8s ease-in-out infinite',
        'slide-up': 'slideUp 0.5s ease-out',
        'fade-in': 'fadeIn 0.3s ease-out',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px #00d4aa, 0 0 10px #00d4aa, 0 0 15px #00d4aa' },
          '100%': { boxShadow: '0 0 10px #00d4aa, 0 0 20px #00d4aa, 0 0 30px #00d4aa' },
        },
        liquid: {
          '0%, 100%': { borderRadius: '30% 70% 70% 30% / 30% 30% 70% 70%' },
          '25%': { borderRadius: '58% 42% 75% 25% / 76% 46% 54% 24%' },
          '50%': { borderRadius: '50% 50% 33% 67% / 55% 27% 73% 45%' },
          '75%': { borderRadius: '33% 67% 58% 42% / 63% 68% 32% 37%' },
        },
        slideUp: {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
