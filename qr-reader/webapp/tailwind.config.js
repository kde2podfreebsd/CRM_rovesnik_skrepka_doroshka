/** @type {(tailwindConfig: object) => object} */
// eslint-disable-next-line @typescript-eslint/no-var-requires,no-undef
const withMT = require("@material-tailwind/react/utils/withMT");

// eslint-disable-next-line @typescript-eslint/no-var-requires,no-undef
const colors = require("tailwindcss/colors");

// eslint-disable-next-line no-undef
module.exports = withMT({
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        telegram: {
          'bg-color': 'var(--tg-color-scheme-bg-color)',
          'text-color': 'var(--tg-color-scheme-text-color)',
          'hint-color': 'var(--tg-color-scheme-hint-color)',
          'link-color': 'var(--tg-color-scheme-link-color)',
          'button-color': 'var(--tg-color-scheme-button-color)',
          'button-text-color': 'var(--tg-color-scheme-button-text-color)',
          'secondary-bg-color': 'var(--tg-color-scheme-secondary-bg-color)',
          'header-bg-color': 'var(--tg-color-scheme-header-bg-color)',
          'accent-text-color': 'var(--tg-color-scheme-accent-text-color)',
          'section-bg-color': 'var(--tg-color-scheme-section-bg-color)',
          'section-header-text-color': 'var(--tg-color-scheme-section-header-text-color)',
          'subtitle-text-color': 'var(--tg-color-scheme-subtitle-text-color)',
          'destructive-text-color': 'var(--tg-color-scheme-destructive-text-color)',
        },
        ...colors
      },

      textColor: {
        'black': 'var(--tg-color-scheme-text-color)',
      }
    },
  },
  plugins: [],
})