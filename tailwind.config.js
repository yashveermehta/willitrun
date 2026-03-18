import forms from '@tailwindcss/forms';
import containerQueries from '@tailwindcss/container-queries';

/** @type {import('tailwindcss').Config} */
export default {
    content: ['./src/**/*.{html,js,svelte,ts}'],
    theme: {
      extend: {
        colors: {
          pageBg: '#080810',
          cardSurface: '#0f0f1a',
          cardHover: '#13131f',
          elevated: '#1a1a28',
          borderDefault: 'rgba(255,255,255,0.06)',
          borderHover: 'rgba(255,255,255,0.12)',
          primaryText: '#f4f4ff',
          secondaryText: '#7c7c9e',
          tertiaryText: '#4a4a6a',
          accentViolet: '#7c6af7',
          accentGreen: '#1db954',
          accentAmber: '#f0a429',
        },
        fontFamily: {
          sans: ['Inter', 'sans-serif'],
        }
      }
    },
    plugins: [
        forms,
        containerQueries
    ]
};
