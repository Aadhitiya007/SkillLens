# SkillLens — AI Career Intelligence Platform

Upload resume → GitHub + LinkedIn verification → 30Q skill test → certified learning plan → company mock interviews

## ✅ Quick Start (VS Code)

### 1. Get your Anthropic API key
Go to [console.anthropic.com](https://console.anthropic.com) → API Keys → Create Key

### 2. Add your API key
Open `.env.local` and replace the placeholder with your real key:
```
VITE_ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxx
```

### 3. Install and run
```bash
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

## How it works (no backend needed)
The Vite dev server proxies `/api/v1/messages` → `https://api.anthropic.com/v1/messages`.
Your API key stays in `.env.local` and is injected at the proxy level — it never goes to the browser.

## Features
- **Resume Upload** — PDF, PNG, JPG, WEBP or paste text
- **GitHub Verification** — Live API checks repos, languages, activity
- **LinkedIn AI Check** — NLP analysis of profile credibility
- **30Q Skill Test** — Auto-generated from YOUR resume skills
- **Company Mock Test** — Styled like Google/Amazon/TCS real interviews (year-specific)
- **Certified Learning Path** — Coursera, Udemy, edX + YouTube tutorials

## ⚠️ Security
- Never commit `.env.local` to GitHub — it's already in `.gitignore`
- The API key is injected by the Vite proxy (server-side), NOT exposed to the browser
- Auth and user data are stored in `localStorage` (local only, no external database)

## Bugs fixed in this version
- Timer expiry now correctly captures all answered questions (stale closure fix)
- Submit button passes current answer state correctly
- YouTube playlist URL generation in learning plan fixed
- Double-submission of quiz results prevented with `finishedRef`
