# Project Guidelines & UI Standards

## HTML Tools & Generative UI Standard
Whenever generating interactive HTML tools, tutorials, or UI widgets in this project:
1. **Mandatory Dark / Light Mode Toggle**: Must include a manual `☀️ / 🌙` theme toggle button with local fallback CSS variables, ensuring the tool works seamlessly both in the Antigravity preview iframe and in standalone browsers (Chrome/Edge).
2. **Mandatory Bilingual Support (EN & 繁體中文)**: Must provide an instant language switch button (`🌐 EN / 中文`) with a complete translation dictionary (`i18nData`) covering all labels, descriptions, and interactive elements.
3. **Standalone Resiliency**: Never rely solely on host iframe theme injection; always include resilient standalone tokens and state handling.
