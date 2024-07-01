/** @type {import('tailwindcss').Config} */
const defaultThemere = require('tailwindcss/defaultTheme');

module.exports = {
    darkMode: 'class',
    content: ['./app/templates/**/*.html.j2', './src/**/*.js'],
    theme: {
        screens: {
            xs: '475px',
            'lg-max': { max: defaultThemere.screens.lg },
            'md-max': { max: defaultThemere.screens.md },
            ...defaultThemere.screens,
        },
        container: {
            center: true,
            padding: {
                DEFAULT: '0.5rem',
            },
        },
        extend: {
            gridTemplateColumns: {
                'autofill-500': 'repeat(auto-fill, minmax(500px, 1fr))',
                'autofill-400': 'repeat(auto-fill, minmax(400px, 1fr))',
                'autofill-300': 'repeat(auto-fill, minmax(300px, 1fr))',
                'autofill-200': 'repeat(auto-fill, minmax(200px, 1fr))',
                'autofit-200': 'repeat(auto-fit, minmax(200px, 1fr))',
            },
            boxShadow: {
                md: 'rgba(0, 0, 0, 0.35) 0px 2px 5px',
            },
        },
    },
    plugins: [],
};
