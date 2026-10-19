# SatyaSutra — Frontend

React + Vite frontend for the SatyaSutra AI Investigation Platform. Premium dark-themed UI with glassmorphism, micro-animations, and client-side routing.

## Tech Stack

| Technology | Version | Purpose |
| --- | --- | --- |
| React | 19 | UI library |
| Vite | 8 | Build tool & dev server |
| React Router DOM | 7 | Client-side routing |
| Inter (Google Fonts) | — | Typography |

## Getting Started

```bash
# Install dependencies
npm install

# Start dev server (http://localhost:5173)
npm run dev

# Production build
npm run build
```

> The frontend expects the backend API at `http://localhost:8000/api`. Override by setting `VITE_API_URL` in a `.env` file.

---

## File Structure & What Each File Does

```
frontend/
├── index.html              # HTML entry point
├── vite.config.js          # Vite configuration
├── package.json            # Dependencies & scripts
│
└── src/
    ├── main.jsx            # React entry point
    ├── index.css           # Global design system (tokens & reset)
    ├── App.jsx             # Root component (routing & layout)
    ├── App.css             # Component-level styles
    │
    ├── api/
    │   └── client.js       # Backend API client
    │
    ├── components/
    │   ├── Navbar.jsx      # Top navigation bar
    │   └── Footer.jsx      # Page footer
    │
    └── pages/
        ├── Dashboard.jsx   # Landing page with hero & features
        ├── EvidenceUpload.jsx  # File upload with drag-and-drop
        ├── GraphView.jsx   # Knowledge graph (stub)
        ├── Timeline.jsx    # Timeline reconstruction (stub)
        └── Report.jsx      # Case report generator (stub)
```

---

## File-by-File Breakdown

### Entry & Configuration

#### `index.html`
The single HTML page that bootstraps the React app. Loads the Inter font from Google Fonts, sets the page title and meta description for SEO, and mounts the app into `<div id="root">`.

#### `vite.config.js`
Vite build configuration with the React plugin for JSX/fast refresh support.

#### `package.json`
Declares project dependencies (`react`, `react-dom`, `react-router-dom`) and dev dependencies (`vite`, `@vitejs/plugin-react`). Defines scripts: `dev`, `build`, `preview`.

---

### Core App Files

#### `src/main.jsx`
React entry point. Imports global styles from `index.css`, wraps the `App` component in `StrictMode`, and renders it into the DOM root.

#### `src/index.css`
**Global design system.** Defines all CSS custom properties (design tokens) used across the app:
- **Color palette** — background, text, accent, semantic (success/warning/danger/info)
- **Gradients** — accent gradient, card gradient, hero ambient glow
- **Typography** — font sizes from `xs` to `5xl` using Inter
- **Spacing scale** — consistent spacing from `sp-1` to `sp-20`
- **Border radius** — `r-sm` through `r-full`
- **Shadows** — including glow effects for accent elements
- **Transitions** — fast/base/slow easing curves

Also includes the CSS reset, ambient background radial gradients, and base element styles.

#### `src/App.jsx`
Root React component. Sets up:
- `BrowserRouter` for client-side routing
- App layout: `Navbar` → `<main>` → `Footer`
- Five routes: `/`, `/evidence`, `/graph`, `/timeline`, `/report`

#### `src/App.css`
**Component-level styles.** Contains all UI component classes used across the app:
- **Navbar** — sticky glassmorphic blur, gradient brand text, active link indicators
- **Footer** — subtle top border, muted text
- **Hero section** — centered layout, ambient glow behind heading, badge pill
- **Cards** — gradient background, hover lift animation, top shimmer line
- **Buttons** — primary (gradient + glow) and ghost (glass + border) variants
- **Badges** — semantic color-coded status pills (success, warning, danger, info)
- **Grid** — responsive 2/3-column layouts
- **Upload zone** — dashed border, drag-active glow state, format tags
- **Stub pages** — centered placeholders with feature lists
- **Animations** — fadeInUp, fadeIn, slideDown with staggered delay classes

---

### API Layer

#### `src/api/client.js`
Centralized HTTP client for communicating with the FastAPI backend. Features:
- Base URL configurable via `VITE_API_URL` environment variable
- Generic `request()` function with JSON parsing and error handling
- Automatic `Content-Type` removal for `FormData` (file uploads)
- Exported `api` object with namespaced methods:
  - `api.health()` — health check
  - `api.evidence.upload(file)` — upload evidence file
  - `api.evidence.list()` — list all evidence

---

### Components

#### `src/components/Navbar.jsx`
Sticky top navigation bar with:
- ⚖️ SatyaSutra brand logo with gradient accent text
- Five navigation links using React Router's `NavLink` (auto-applies `.active` class)
- Glassmorphic blur background with bottom border
- Active page indicated by accent color + bottom bar

#### `src/components/Footer.jsx`
Minimal page footer with:
- Project name and tagline
- GitHub repo link
- License info with dynamic year

---

### Pages

#### `src/pages/Dashboard.jsx`
The landing page (route: `/`). Contains:
- **Hero section** — "AI-Powered Investigation" badge, "Connect the Evidence" heading with gradient accent, description, and CTA buttons
- **Stats bar** — 4 metric cards (Modules, Week Plan, MVP Features, Evidence)
- **Feature grid** — 6 cards showcasing core capabilities, each linking to its respective page, with MVP/Stretch scope badges
- Staggered entrance animations on all elements

#### `src/pages/EvidenceUpload.jsx`
Evidence upload page (route: `/evidence`). Features:
- Page header with description
- **Drag-and-drop upload zone** — responds to dragenter/dragover/dragleave/drop events, visual glow on drag-active state
- **File format tags** — PDF, PNG, JPG, TIFF, TXT, BMP
- Hidden `<input type="file">` triggered by click on the zone
- Upload state management (uploading spinner, result card, error card)
- Calls `api.evidence.upload()` on file selection/drop

#### `src/pages/GraphView.jsx`
Knowledge graph stub page (route: `/graph`). Displays:
- 🕸️ icon with "Coming in Week 3–4" badge
- Planned feature list (force-directed layout, edge evidence, node filtering, contradiction highlighting, search/zoom, export)

#### `src/pages/Timeline.jsx`
Timeline reconstruction stub page (route: `/timeline`). Displays:
- 📅 icon with "Coming in Week 5" badge
- Planned feature list (vertical timeline, gap detection, event filtering, time range zoom)

#### `src/pages/Report.jsx`
Case report generator stub page (route: `/report`). Displays:
- 📄 icon with "Coming in Week 7" badge
- Planned feature list (markdown rendering, inline citations, section structure, PDF export)

---

## Design System

The UI follows a premium dark theme with these key design principles:

| Principle | Implementation |
| --- | --- |
| **Dark mode** | Near-black backgrounds (`#06080f`) with subtle blue-violet ambient glows |
| **Glassmorphism** | `backdrop-filter: blur()` on navbar and cards |
| **Gradient accents** | Indigo → Violet → Lavender gradient on primary buttons and brand text |
| **Micro-animations** | Staggered `fadeInUp` on page load, hover lifts on cards, glow on buttons |
| **Typography** | Inter font family with 8 weight levels and 10 size tokens |
| **Responsive** | Fluid grid that collapses from 3-col → 2-col → 1-col on smaller screens |

## Adding New Pages

1. Create a new component in `src/pages/NewPage.jsx`
2. Add a route in `src/App.jsx` inside `<Routes>`
3. Add a nav link in `src/components/Navbar.jsx`
4. Use existing CSS classes (`card`, `page-header`, `btn`, `badge`, etc.) for consistency
