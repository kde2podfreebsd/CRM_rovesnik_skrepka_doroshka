import withMT from "@material-tailwind/react/utils/withMT.js";
import colors from "tailwindcss/colors.js";
import typography from '@tailwindcss/typography';

/** @type {import('tailwindcss').Config} */
export default withMT({
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {...colors}
    },
  },
  plugins: [
    typography,
  ],
})