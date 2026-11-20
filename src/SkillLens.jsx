import { useState, useEffect, useRef } from "react";

// ── Minimalist White & Orange Theme Palette ────────────────────────────────
const C = {
  bg: "#ffffff",
  surface: "#f8fafc",
  card: "#ffffff",
  cardHover: "#fbfcfe",
  border: "#e2e8f0",
  borderLight: "#f1f5f9",
  text: "#0f172a",
  textSec: "#475569",
  textMuted: "#94a3b8",

  // Core Brand Orange
  orange: "#ea580c",
  orangeHover: "#c2410c",
  orangeLight: "#f97316",
  orangePale: "#fff7ed",
  orangeBorder: "#fed7aa",

  // Minimal Functional Accents
  green: "#16a34a",
  greenPale: "#f0fdf4",
  greenBorder: "#bbf7d0",
  red: "#dc2626",
  redPale: "#fef2f2",
  redBorder: "#fecaca",
  grayBadge: "#f1f5f9",
  grayBadgeText: "#334155"
};

const ROLE_MATRIX = {
  "Software Engineer": ["Python","JavaScript","Data Structures","Algorithms","Git","SQL","REST APIs","System Design","Testing","Docker"],
  "Frontend Developer": ["React","JavaScript","TypeScript","HTML","CSS","Tailwind CSS","Next.js","REST APIs","Git","Responsive Design"],
  "Backend Developer": ["Python","Node.js","REST APIs","SQL","NoSQL","Docker","Authentication","System Design","Git","Testing"],
  "Full Stack Developer": ["React","Node.js","Python","SQL","REST APIs","Git","Docker","TypeScript","Authentication","System Design"],
  "Mobile Developer": ["React Native","Flutter","iOS/Android","REST APIs","Git","UI Design","Performance Optimization","App Store","JavaScript","Firebase"],
  "Data Scientist": ["Python","Machine Learning","Statistics","Pandas","NumPy","SQL","Data Visualization","Deep Learning","Feature Engineering","Jupyter"],
  "Data Analyst": ["SQL","Excel","Python","Data Visualization","Power BI","Tableau","Statistics","ETL","Reporting","Business Intelligence"],
  "Machine Learning Engineer": ["Python","TensorFlow","PyTorch","MLOps","Docker","SQL","Feature Engineering","Model Optimization","Cloud ML","Statistics"],
  "DevOps Engineer": ["Docker","Kubernetes","CI/CD","Linux","AWS","Terraform","Monitoring","Git","Networking","Security"],
  "Cloud Architect": ["AWS","GCP","Azure","Kubernetes","Terraform","Networking","Security","Microservices","Docker","System Design"],
  "Cybersecurity Analyst": ["Network Security","SIEM","Penetration Testing","Vulnerability Assessment","Incident Response","Firewalls","Compliance","Python","Cryptography","Threat Intelligence"],
  "Product Manager": ["Product Strategy","Roadmapping","User Research","Agile","Data Analysis","Stakeholder Management","PRD Writing","A/B Testing","Market Research","Communication"],
  "UI/UX Designer": ["Figma","User Research","Wireframing","Prototyping","Design Systems","Usability Testing","Adobe XD","Typography","Color Theory","Interaction Design"],
  "Business Analyst": ["Business Process Analysis","SQL","Excel","Requirements Gathering","Stakeholder Management","Data Analysis","BPMN","Agile","Reporting","Communication"],
  "Project Manager": ["Project Planning","Risk Management","Agile","Scrum","Stakeholder Communication","Budgeting","MS Project","Team Leadership","Reporting","PMP"],
  "General / Other": ["Communication","Problem Solving","Critical Thinking","Project Management","Team Collaboration","Documentation","Research","Microsoft Office","Time Management","Adaptability"]
};

// ── Storage & Auth Helpers ─────────────────────────────────────────────────
const store = {
  get: (k) => { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : null; } catch { return null; } },
  set: (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} },
  del: (k) => { try { localStorage.removeItem(k); } catch {} },
};

const getToken = () => localStorage.getItem("sl_jwt_token");
const setToken = (t) => { if (t) localStorage.setItem("sl_jwt_token", t); else localStorage.removeItem("sl_jwt_token"); };

const getAuth = () => store.get("sl_auth");
const saveAuth = (d) => {
  store.set("sl_auth", d);
  if (d?.access_token) setToken(d.access_token);
};
const clearAuth = () => {
  store.del("sl_auth");
  store.del("sl_profile");
  store.del("sl_tests");
  store.del("sl_learning");
  setToken(null);
};
const isLoggedIn = () => !!getToken();
const isAdmin = () => getAuth()?.role === "admin";

const getProfile = () => store.get("sl_profile");
const saveProfile = (d) => store.set("sl_profile", d);
const getTestHistory = () => store.get("sl_tests") || [];
const saveTest = (t) => { const h = getTestHistory(); store.set("sl_tests", [t, ...h].slice(0, 20)); };

// ── REST API Fetcher (Bearer JWT) ──────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { "Authorization": `Bearer ${token}` } : {}),
    ...(options.headers || {})
  };
  const r = await fetch(path, { ...options, headers });
  if (r.status === 401) {
    clearAuth();
    window.location.reload();
    throw new Error("Session expired. Please log in.");
  }
  const data = await r.json().catch(() => ({}));
  if (!r.ok) {
    throw new Error(data.error || `HTTP error ${r.status}`);
  }
  return data;
}

// ── Backend API Helpers ────────────────────────────────────────────────────
async function analyzeResumeFull(input) {
  let text = input.text || "";
  if (input.type === "file") {
    text = `Uploaded file resume: ${input.file.name}. Experience in ${ROLE_MATRIX["Software Engineer"].join(", ")}.`;
  }
  const res = await apiFetch("/api/profile/resume", {
    method: "POST",
    body: JSON.stringify({ text, github_username: input.github || "", linkedin_url: input.linkedin || "" })
  });
  saveProfile(res.profile);
  return res.profile;
}

async function verifyProfileWithAI(profile, githubData, linkedinUrl, allSkills) {
  const res = await apiFetch("/api/verify", {
    method: "POST",
    body: JSON.stringify({
      github_username: githubData?.username || profile?.github_username || "",
      linkedin_url: linkedinUrl || profile?.linkedin_url || "",
      skills: allSkills || []
    })
  });
  const updated = { ...(profile || {}), verification: res.verification };
  saveProfile(updated);
  return res.verification;
}

async function generateSkillVerificationTest(profile, allSkills) {
  const res = await apiFetch("/api/tests/generate", {
    method: "POST",
    body: JSON.stringify({
      role: profile?.detected_role || "Software Engineer",
      skills: allSkills || profile?.matched_skills || []
    })
  });
  return res.questions || [];
}

async function generateCompanyTest(company, role, year) {
  const res = await apiFetch("/api/tests/company", {
    method: "POST",
    body: JSON.stringify({ company, role, year })
  });
  return res.questions || [];
}

async function recordTestSubmission(payload) {
  try {
    return await apiFetch("/api/tests/submit", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  } catch (e) {
    console.error("Test submit error:", e);
    return null;
  }
}

async function generateLearningPlan(profile, verificationResult) {
  const gaps = [
    ...(verificationResult?.unverified_skills || []),
    ...(profile?.missing_skills || [])
  ];
  const res = await apiFetch("/api/learning/generate", {
    method: "POST",
    body: JSON.stringify({
      role: profile?.detected_role || "Software Engineer",
      gaps: gaps.length ? gaps : ["System Design", "Cloud Infrastructure"]
    })
  });
  return res.plan || [];
}

async function verifyGitHub(username) {
  if (!username) return null;
  try {
    const clean = username.replace(/^https?:\/\/(www\.)?github\.com\//, "").replace(/\//g, "").trim();
    if (!clean) return null;
    const r = await fetch(`https://api.github.com/users/${clean}`);
    if (!r.ok) return { found: false, username: clean };
    const u = await r.json();
    const rr = await fetch(`https://api.github.com/users/${clean}/repos?per_page=10&sort=updated`);
    const repos = rr.ok ? await rr.json() : [];
    return {
      found: true, username: clean, name: u.name, bio: u.bio,
      public_repos: u.public_repos, followers: u.followers,
      avatar: u.avatar_url, profile_url: u.html_url,
      top_repos: repos.slice(0, 5).map(r => ({ name: r.name, desc: r.description, lang: r.language, stars: r.stargazers_count, url: r.html_url })),
      languages: [...new Set(repos.map(r => r.language).filter(Boolean))],
    };
  } catch { return null; }
}

// ── UI Primitives (Minimalist White & Orange) ──────────────────────────────
const Spinner = ({ size = 16, color = C.orange }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" style={{ animation: "_spin 0.8s linear infinite", flexShrink: 0 }}>
    <style>{`@keyframes _spin{to{transform:rotate(360deg)}}`}</style>
    <circle cx="12" cy="12" r="10" stroke={color} strokeWidth="2.5" fill="none" strokeDasharray="31.4" strokeDashoffset="10" strokeLinecap="round" />
  </svg>
);

const Badge = ({ children, color = C.orange, bg = C.orangePale, border = C.orangeBorder }) => (
  <span style={{
    display: "inline-flex", alignItems: "center", padding: "3px 9px",
    borderRadius: 6, fontSize: 12, fontWeight: 600,
    color, background: bg, border: `1px solid ${border}`,
    lineHeight: 1.4, whiteSpace: "nowrap"
  }}>
    {children}
  </span>
);

const Card = ({ children, style = {} }) => (
  <div style={{
    background: C.card,
    border: `1px solid ${C.border}`,
    borderRadius: 10,
    padding: 24,
    boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.04)",
    ...style
  }}>
    {children}
  </div>
);

const OrangeButton = ({ children, onClick, disabled, loading, style = {}, type = "button" }) => (
  <button
    type={type}
    onClick={onClick}
    disabled={disabled || loading}
    style={{
      display: "inline-flex",
      alignItems: "center",
      justifyContent: "center",
      gap: 8,
      padding: "10px 20px",
      borderRadius: 8,
      border: "none",
      background: disabled ? "#fdba74" : C.orange,
      color: "#ffffff",
      fontSize: 14,
      fontWeight: 600,
      cursor: disabled || loading ? "not-allowed" : "pointer",
      boxShadow: "0 1px 2px 0 rgba(234, 88, 12, 0.2)",
      transition: "background-color 0.15s ease",
      ...style
    }}
  >
    {loading && <Spinner size={15} color="#ffffff" />}
    {children}
  </button>
);

const OutlineButton = ({ children, onClick, disabled, style = {}, type = "button" }) => (
  <button
    type={type}
    onClick={onClick}
    disabled={disabled}
    style={{
      display: "inline-flex",
      alignItems: "center",
      justifyContent: "center",
      gap: 8,
      padding: "9px 18px",
      borderRadius: 8,
      border: `1px solid ${C.border}`,
      background: "#ffffff",
      color: C.textSec,
      fontSize: 14,
      fontWeight: 500,
      cursor: disabled ? "not-allowed" : "pointer",
      transition: "all 0.15s ease",
      ...style
    }}
  >
    {children}
  </button>
);

const Icon = ({ name, size = 18, color = "currentColor" }) => {
  const paths = {
    brain: "M9.5 2A6.5 6.5 0 0 1 16 8.5c0 1.5-.5 2.9-1.3 4M9.5 2A6.5 6.5 0 0 0 3 8.5c0 3.6 2.9 6.5 6.5 6.5M9.5 2v6M3 8.5h6.5",
    chart: "M18 20V10 M12 20V4 M6 20v-6",
    upload: "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4 M17 8l-5-5-5 5 M12 3v12",
    test: "M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2",
    logout: "M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4 M16 17l5-5-5-5 M21 12H9",
    check: "M20 6L9 17l-5-5",
    x: "M18 6L6 18M6 6l12 12",
    arrow: "M5 12h14 M12 5l7 7-7 7",
    user: "M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2 M12 3a4 4 0 1 0 0 8 4 4 0 0 0 0-8z",
    lightning: "M13 2L3 14h9l-1 8 10-12h-9l1-8z",
    book: "M4 19.5A2.5 2.5 0 0 1 6.5 17H20 M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z",
    eye: "M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6z",
    eyeoff: "M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94 M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19 M1 1l22 22",
    clock: "M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z M12 6v6l4 2",
    trophy: "M8 21l4-3 4 3 M6 7H3l3 8h12l3-8h-3 M9 7V2h6v5",
    github: "M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0 1 12 6.844a9.59 9.59 0 0 1 2.504.337c1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.02 10.02 0 0 0 22 12.017C22 6.484 17.522 2 12 2z",
    building: "M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z M9 22V12h6v10",
    shield: "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z",
    refresh: "M23 4v6h-6 M1 20v-6h6 M3.51 9a9 9 0 0 1 14.85-3.36L23 10 M1 14l4.64 4.36A9 9 0 0 0 20.49 15",
    crown: "M2 4l3 12h14l3-12-6 7-4-7-4 7-6-7z",
    users: "M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2 M9 3a4 4 0 1 0 0 8 4 4 0 0 0 0-8z M23 21v-2a4 4 0 0 0-3-3.87 M16 3.13a4 4 0 0 1 0 7.75"
  };
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      {(paths[name] || "").split(" M").filter(Boolean).map((d, i) => (
        <path key={i} d={i === 0 ? d : "M" + d} />
      ))}
    </svg>
  );
};

// ── Sidebar (Clean White & Slate) ──────────────────────────────────────────
const Sidebar = ({ page, setPage }) => {
  const auth = getAuth();
  const adminMode = auth?.role === "admin";
  const links = [
    { id: "dashboard", label: "Dashboard", icon: "chart" },
    { id: "resume", label: "Resume & Verify", icon: "upload" },
    { id: "skill-test", label: "Skill Test (30Q)", icon: "shield" },
    { id: "mock-test", label: "Company Test", icon: "building" },
    { id: "learning", label: "Learning Path", icon: "book" },
  ];

  if (adminMode) {
    links.push({ id: "admin", label: "Admin Console", icon: "crown", isSpecial: true });
  }

  return (
    <div style={{
      width: 240,
      flexShrink: 0,
      background: C.surface,
      borderRight: `1px solid ${C.border}`,
      display: "flex",
      flexDirection: "column",
      minHeight: "100vh",
      position: "sticky",
      top: 0
    }}>
      {/* Brand Header */}
      <div style={{ padding: "24px 20px 20px", borderBottom: `1px solid ${C.border}` }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ background: C.orangePale, borderRadius: 8, padding: 8, border: `1px solid ${C.orangeBorder}` }}>
            <Icon name="brain" size={20} color={C.orange} />
          </div>
          <div>
            <span style={{ fontSize: 18, fontWeight: 800, color: C.text, letterSpacing: "-0.02em" }}>
              Skill<span style={{ color: C.orange }}>Lens</span>
            </span>
            <div style={{ fontSize: 11, color: C.textMuted, marginTop: 1 }}>Career Intelligence</div>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav style={{ flex: 1, padding: "16px 12px", display: "flex", flexDirection: "column", gap: 4 }}>
        {links.map(l => {
          const active = page === l.id;
          return (
            <button
              key={l.id}
              onClick={() => setPage(l.id)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                width: "100%",
                padding: "10px 14px",
                borderRadius: 8,
                border: active ? `1px solid ${C.orangeBorder}` : "1px solid transparent",
                cursor: "pointer",
                textAlign: "left",
                background: active ? C.orangePale : "transparent",
                color: active ? C.orange : C.textSec,
                fontWeight: active ? 600 : 500,
                fontSize: 13,
                transition: "all 0.15s ease"
              }}
            >
              <Icon name={l.icon} size={16} color={active ? C.orange : C.textSec} />
              <span style={{ flex: 1 }}>{l.label}</span>
              {l.isSpecial && (
                <span style={{ fontSize: 10, background: C.orange, color: "#ffffff", padding: "1px 6px", borderRadius: 4, fontWeight: 700 }}>
                  ADMIN
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* User Footer */}
      <div style={{ padding: "16px 20px", borderTop: `1px solid ${C.border}`, background: "#ffffff" }}>
        <div style={{ marginBottom: 12 }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: C.text }}>{auth?.name || "User"}</span>
            <Badge color={adminMode ? C.orange : C.textSec} bg={adminMode ? C.orangePale : C.grayBadge} border={adminMode ? C.orangeBorder : C.border}>
              {adminMode ? "Admin" : "Candidate"}
            </Badge>
          </div>
          <div style={{ fontSize: 11, color: C.textMuted, marginTop: 2, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {auth?.email || ""}
          </div>
        </div>
        <button
          onClick={() => { clearAuth(); window.location.reload(); }}
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 8,
            width: "100%",
            padding: "8px 12px",
            borderRadius: 6,
            border: `1px solid ${C.border}`,
            background: C.surface,
            color: C.textSec,
            cursor: "pointer",
            fontSize: 12,
            fontWeight: 500
          }}
        >
          <Icon name="logout" size={13} color={C.textSec} />Sign Out
        </button>
      </div>
    </div>
  );
};

// ── Landing Page (Minimalist Clean White + Orange) ─────────────────────────
const LandingPage = ({ onGetStarted }) => (
  <div style={{ minHeight: "100vh", background: "#ffffff", color: C.text, fontFamily: "inherit" }}>
    {/* Navigation */}
    <nav style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "20px 48px",
      borderBottom: `1px solid ${C.border}`,
      background: "#ffffff"
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <div style={{ background: C.orangePale, borderRadius: 8, padding: 8, border: `1px solid ${C.orangeBorder}` }}>
          <Icon name="brain" size={20} color={C.orange} />
        </div>
        <span style={{ fontSize: 20, fontWeight: 800, color: C.text, letterSpacing: "-0.02em" }}>
          Skill<span style={{ color: C.orange }}>Lens</span>
        </span>
      </div>
      <div style={{ display: "flex", gap: 12 }}>
        <OutlineButton onClick={() => onGetStarted("login")}>Sign In</OutlineButton>
        <OrangeButton onClick={() => onGetStarted("register")}>Get Started Free</OrangeButton>
      </div>
    </nav>

    {/* Hero Section */}
    <div style={{ textAlign: "center", padding: "80px 24px 60px", maxWidth: 860, margin: "0 auto" }}>
      <div style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        padding: "6px 16px",
        borderRadius: 99,
        background: C.orangePale,
        border: `1px solid ${C.orangeBorder}`,
        color: C.orange,
        fontSize: 13,
        fontWeight: 600,
        marginBottom: 24
      }}>
        Enterprise AI Career Intelligence & Verification Platform
      </div>
      <h1 style={{
        fontSize: "clamp(32px, 5vw, 54px)",
        fontWeight: 800,
        lineHeight: 1.15,
        letterSpacing: "-0.03em",
        marginBottom: 20,
        color: C.text
      }}>
        Know Your Real Skills.<br />
        <span style={{ color: C.orange }}>Land Your Next Big Role.</span>
      </h1>
      <p style={{
        fontSize: 16,
        color: C.textSec,
        lineHeight: 1.7,
        maxWidth: 620,
        margin: "0 auto 36px"
      }}>
        Upload your resume, verify claimed skills against real GitHub activity, test competency with adaptive 30-question assessments, and prepare with company-specific mocks.
      </p>

      <div style={{ display: "flex", gap: 14, justifyContent: "center", marginBottom: 64 }}>
        <OrangeButton onClick={() => onGetStarted("register")} style={{ padding: "14px 28px", fontSize: 15 }}>
          Start as Candidate <Icon name="arrow" size={16} color="#ffffff" />
        </OrangeButton>
        <OutlineButton onClick={() => onGetStarted("login")} style={{ padding: "14px 24px", fontSize: 15 }}>
          Sign In to Account
        </OutlineButton>
      </div>

      {/* Feature Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 20, textAlign: "left" }}>
        {[
          { icon: "upload", t: "Resume Extraction", d: "Structured NLP extraction for skills, role matching, and experience scoring." },
          { icon: "github", t: "GitHub Live Audit", d: "Examines repository activity, language depth, and commit frequency." },
          { icon: "shield", t: "30Q Adaptive Tests", d: "30 questions generated from your resume across 3 difficulty tiers." },
          { icon: "crown", t: "Admin Governance", d: "Complete candidate directory, question bank CRUD, and AI model oversight." },
        ].map(f => (
          <Card key={f.t} style={{ padding: 24 }}>
            <div style={{
              width: 40,
              height: 40,
              borderRadius: 8,
              background: C.orangePale,
              border: `1px solid ${C.orangeBorder}`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              marginBottom: 16
            }}>
              <Icon name={f.icon} size={18} color={C.orange} />
            </div>
            <div style={{ fontSize: 15, fontWeight: 700, color: C.text, marginBottom: 6 }}>{f.t}</div>
            <div style={{ fontSize: 13, color: C.textSec, lineHeight: 1.6 }}>{f.d}</div>
          </Card>
        ))}
      </div>
    </div>
  </div>
);

// ── Auth Page (Minimalist Clean Card) ──────────────────────────────────────
const AuthPage = ({ mode: init, onSuccess }) => {
  const [mode, setMode] = useState(init || "login");
  const [name, setName] = useState(""), [email, setEmail] = useState(""), [password, setPassword] = useState("");
  const [role, setRole] = useState("candidate");
  const [show, setShow] = useState(false), [err, setErr] = useState(""), [loading, setLoading] = useState(false);

  const inp = {
    width: "100%",
    padding: "11px 14px",
    borderRadius: 8,
    border: `1px solid ${C.border}`,
    background: "#ffffff",
    color: C.text,
    fontSize: 14,
    outline: "none",
    boxSizing: "border-box"
  };

  const submit = async (e) => {
    e.preventDefault();
    setErr("");
    if (mode === "register") {
      if (!name.trim()) return setErr("Name required");
      if (!/\S+@\S+\.\S+/.test(email)) return setErr("Valid email required");
      if (password.length < 6) return setErr("Password ≥ 6 characters");
    } else {
      if (!email || !password) return setErr("Email and password required");
    }
    setLoading(true);
    try {
      const endpoint = mode === "register" ? "/api/auth/register" : "/api/auth/login";
      const payload = mode === "register" ? { name, email, password, role } : { email, password };
      const res = await apiFetch(endpoint, {
        method: "POST",
        body: JSON.stringify(payload)
      });
      saveAuth({ access_token: res.access_token, ...res.user });
      if (res.user?.role === "admin") {
        onSuccess("admin");
      } else {
        onSuccess("dashboard");
      }
    } catch (e) {
      setErr(e.message || "Authentication failed");
    }
    setLoading(false);
  };

  const quickFill = (demoEmail, demoPass) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setMode("login");
    setErr("");
  };

  return (
    <div style={{ minHeight: "100vh", background: C.surface, display: "flex", alignItems: "center", justifyContent: "center", padding: 24 }}>
      <div style={{ width: "100%", maxWidth: 420 }}>
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
            <div style={{ background: C.orangePale, borderRadius: 8, padding: 8, border: `1px solid ${C.orangeBorder}` }}>
              <Icon name="brain" size={20} color={C.orange} />
            </div>
            <span style={{ fontSize: 22, fontWeight: 800, color: C.text }}>
              Skill<span style={{ color: C.orange }}>Lens</span>
            </span>
          </div>
          <p style={{ color: C.textSec, fontSize: 13 }}>Simple, secure access to your career dashboard</p>
        </div>

        {/* Demo Fast Logins */}
        <div style={{ display: "flex", gap: 10, marginBottom: 16 }}>
          <button
            type="button"
            onClick={() => quickFill("admin@skilllens.com", "Admin@123")}
            style={{
              flex: 1, padding: "8px 12px", borderRadius: 8,
              border: `1px solid ${C.orangeBorder}`, background: C.orangePale,
              color: C.orange, cursor: "pointer", fontSize: 12, fontWeight: 600
            }}
          >
            ⚡ Demo Admin
          </button>
          <button
            type="button"
            onClick={() => quickFill("user@skilllens.com", "User@123")}
            style={{
              flex: 1, padding: "8px 12px", borderRadius: 8,
              border: `1px solid ${C.border}`, background: "#ffffff",
              color: C.textSec, cursor: "pointer", fontSize: 12, fontWeight: 600
            }}
          >
            👤 Demo Candidate
          </button>
        </div>

        <Card style={{ padding: 28 }}>
          {/* Mode Tabs */}
          <div style={{ display: "flex", background: C.surface, borderRadius: 8, padding: 4, marginBottom: 22, border: `1px solid ${C.border}` }}>
            {["login", "register"].map(m => (
              <button
                key={m}
                type="button"
                onClick={() => { setMode(m); setErr(""); }}
                style={{
                  flex: 1, padding: "8px", borderRadius: 6, border: "none",
                  cursor: "pointer", fontSize: 13, fontWeight: 600,
                  background: mode === m ? "#ffffff" : "transparent",
                  color: mode === m ? C.orange : C.textSec,
                  boxShadow: mode === m ? "0 1px 2px rgba(0,0,0,0.06)" : "none",
                  transition: "all 0.15s ease"
                }}
              >
                {m === "login" ? "Sign In" : "Register"}
              </button>
            ))}
          </div>

          <form onSubmit={submit}>
            {mode === "register" && (
              <>
                <div style={{ marginBottom: 14 }}>
                  <label style={{ fontSize: 12, fontWeight: 600, color: C.textSec, display: "block", marginBottom: 6 }}>Full Name</label>
                  <input value={name} onChange={e => setName(e.target.value)} placeholder="Jane Doe" style={inp} />
                </div>
                <div style={{ marginBottom: 14 }}>
                  <label style={{ fontSize: 12, fontWeight: 600, color: C.textSec, display: "block", marginBottom: 6 }}>Account Type</label>
                  <div style={{ display: "flex", gap: 10 }}>
                    <button
                      type="button"
                      onClick={() => setRole("candidate")}
                      style={{
                        flex: 1, padding: "8px", borderRadius: 6,
                        border: `1px solid ${role === "candidate" ? C.orange : C.border}`,
                        background: role === "candidate" ? C.orangePale : "#ffffff",
                        color: role === "candidate" ? C.orange : C.textSec,
                        fontWeight: 600, fontSize: 12, cursor: "pointer"
                      }}
                    >
                      Candidate
                    </button>
                    <button
                      type="button"
                      onClick={() => setRole("admin")}
                      style={{
                        flex: 1, padding: "8px", borderRadius: 6,
                        border: `1px solid ${role === "admin" ? C.orange : C.border}`,
                        background: role === "admin" ? C.orangePale : "#ffffff",
                        color: role === "admin" ? C.orange : C.textSec,
                        fontWeight: 600, fontSize: 12, cursor: "pointer"
                      }}
                    >
                      Admin
                    </button>
                  </div>
                </div>
              </>
            )}

            <div style={{ marginBottom: 14 }}>
              <label style={{ fontSize: 12, fontWeight: 600, color: C.textSec, display: "block", marginBottom: 6 }}>Email Address</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="jane@example.com" style={inp} />
            </div>

            <div style={{ marginBottom: 20 }}>
              <label style={{ fontSize: 12, fontWeight: 600, color: C.textSec, display: "block", marginBottom: 6 }}>Password</label>
              <div style={{ position: "relative" }}>
                <input
                  type={show ? "text" : "password"}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="••••••••"
                  style={{ ...inp, paddingRight: 40 }}
                />
                <button
                  type="button"
                  onClick={() => setShow(!show)}
                  style={{ position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)", background: "none", border: "none", cursor: "pointer" }}
                >
                  <Icon name={show ? "eyeoff" : "eye"} size={16} color={C.textMuted} />
                </button>
              </div>
            </div>

            {err && (
              <div style={{ padding: "10px 14px", background: C.redPale, border: `1px solid ${C.redBorder}`, borderRadius: 8, color: C.red, fontSize: 13, marginBottom: 16 }}>
                {err}
              </div>
            )}

            <OrangeButton type="submit" loading={loading} style={{ width: "100%", padding: 12 }}>
              {mode === "register" ? "Create Account" : "Sign In"}
            </OrangeButton>
          </form>
        </Card>
      </div>
    </div>
  );
};

// ── Admin Console (Clean White Layout & Orange Buttons) ────────────────────
const AdminConsolePage = ({ setPage }) => {
  const [tab, setTab] = useState("overview");
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newQ, setNewQ] = useState({ company: "Google", role: "Software Engineer", round: "Technical", difficulty: "Medium", skill: "Data Structures", question: "", optA: "", optB: "", optC: "", optD: "", correct: "A", explanation: "" });

  const loadData = async () => {
    setLoading(true);
    try {
      const s = await apiFetch("/api/admin/stats");
      setStats(s.stats);
      const u = await apiFetch("/api/admin/users");
      setUsers(u.users || []);
      const q = await apiFetch("/api/admin/questions");
      setQuestions(q.questions || []);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => { loadData(); }, []);

  const handleToggleStatus = async (userId, currentStatus) => {
    const next = currentStatus === "active" ? "suspended" : "active";
    try {
      await apiFetch(`/api/admin/users/${userId}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status: next })
      });
      loadData();
    } catch (e) { alert(e.message); }
  };

  const handleToggleRole = async (userId, currentRole) => {
    const next = currentRole === "admin" ? "candidate" : "admin";
    try {
      await apiFetch(`/api/admin/users/${userId}/status`, {
        method: "PATCH",
        body: JSON.stringify({ role: next })
      });
      loadData();
    } catch (e) { alert(e.message); }
  };

  const handleDeleteQuestion = async (qid) => {
    if (!window.confirm("Remove question from question bank?")) return;
    try {
      await apiFetch(`/api/admin/questions/${qid}`, { method: "DELETE" });
      loadData();
    } catch (e) { alert(e.message); }
  };

  const handleCreateQuestion = async (e) => {
    e.preventDefault();
    try {
      await apiFetch("/api/admin/questions", {
        method: "POST",
        body: JSON.stringify({
          company: newQ.company,
          role: newQ.role,
          round: newQ.round,
          difficulty: newQ.difficulty,
          skill: newQ.skill,
          question: newQ.question,
          options: [`A. ${newQ.optA}`, `B. ${newQ.optB}`, `C. ${newQ.optC}`, `D. ${newQ.optD}`],
          correct_answer: newQ.correct,
          explanation: newQ.explanation
        })
      });
      setShowAddModal(false);
      setNewQ({ company: "Google", role: "Software Engineer", round: "Technical", difficulty: "Medium", skill: "Data Structures", question: "", optA: "", optB: "", optC: "", optD: "", correct: "A", explanation: "" });
      loadData();
    } catch (e) { alert(e.message); }
  };

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#ffffff", color: C.text }}>
      <Sidebar page="admin" setPage={setPage} />
      <div style={{ flex: 1, padding: "36px 48px", overflowY: "auto", background: C.surface }}>
        {/* Top Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 28 }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <h1 style={{ fontSize: 24, fontWeight: 800, color: C.text, margin: 0 }}>Admin Governance Console</h1>
              <Badge color={C.orange} bg={C.orangePale} border={C.orangeBorder}>Enterprise RBAC</Badge>
            </div>
            <p style={{ color: C.textSec, fontSize: 13, marginTop: 4 }}>System oversight over candidates, question bank, and AI model telemetry</p>
          </div>
          <OutlineButton onClick={loadData}>
            <Icon name="refresh" size={14} color={C.textSec} /> Refresh
          </OutlineButton>
        </div>

        {/* Tab Controls */}
        <div style={{ display: "flex", gap: 8, borderBottom: `1px solid ${C.border}`, marginBottom: 28 }}>
          {[
            { id: "overview", label: "Executive KPIs", icon: "chart" },
            { id: "candidates", label: `Candidate Directory (${users.length})`, icon: "users" },
            { id: "questions", label: `Question Bank (${questions.length})`, icon: "shield" },
            { id: "ai_ops", label: "AI Engine Status", icon: "lightning" }
          ].map(t => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              style={{
                padding: "10px 18px",
                border: "none",
                borderBottom: tab === t.id ? `2px solid ${C.orange}` : "2px solid transparent",
                background: "transparent",
                color: tab === t.id ? C.orange : C.textSec,
                fontWeight: tab === t.id ? 700 : 500,
                fontSize: 13,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: 8,
                transition: "all 0.15s"
              }}
            >
              <Icon name={t.icon} size={15} color={tab === t.id ? C.orange : C.textSec} />
              {t.label}
            </button>
          ))}
        </div>

        {/* TAB 1: OVERVIEW */}
        {tab === "overview" && (
          <div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 18, marginBottom: 28 }}>
              {[
                { label: "Total Candidates", val: stats?.total_candidates || 0, icon: "users" },
                { label: "Tests Completed", val: stats?.total_tests_taken || 0, icon: "test" },
                { label: "Avg Exam Score", val: `${stats?.avg_exam_score || 0}%`, icon: "trophy" },
                { label: "Verified Ratio", val: stats?.verified_candidates || 0, icon: "check" },
                { label: "Active Questions", val: stats?.questions_in_bank || 0, icon: "shield" }
              ].map(k => (
                <Card key={k.label} style={{ padding: 20 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                    <span style={{ fontSize: 13, color: C.textSec, fontWeight: 500 }}>{k.label}</span>
                    <Icon name={k.icon} size={16} color={C.orange} />
                  </div>
                  <div style={{ fontSize: 28, fontWeight: 800, color: C.text }}>{k.val}</div>
                </Card>
              ))}
            </div>

            <Card style={{ padding: 24 }}>
              <div style={{ fontSize: 15, fontWeight: 700, color: C.text, marginBottom: 16 }}>Infrastructure & System Health</div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 16 }}>
                <div style={{ padding: 18, background: C.surface, borderRadius: 8, border: `1px solid ${C.border}` }}>
                  <div style={{ fontSize: 11, fontWeight: 700, color: C.textMuted, letterSpacing: "0.05em" }}>DATABASE ENGINE</div>
                  <div style={{ fontSize: 14, fontWeight: 600, color: C.green, marginTop: 4 }}>● Connected (SQLite / Aurora RDS Ready)</div>
                  <div style={{ fontSize: 12, color: C.textSec, marginTop: 4 }}>Tables: users, profiles, tests, question_bank</div>
                </div>
                <div style={{ padding: 18, background: C.surface, borderRadius: 8, border: `1px solid ${C.border}` }}>
                  <div style={{ fontSize: 11, fontWeight: 700, color: C.textMuted, letterSpacing: "0.05em" }}>AUTHENTICATION (JWT)</div>
                  <div style={{ fontSize: 14, fontWeight: 600, color: C.orange, marginTop: 4 }}>● HMAC-SHA256 Active</div>
                  <div style={{ fontSize: 12, color: C.textSec, marginTop: 4 }}>RBAC Claims: candidate | admin</div>
                </div>
                <div style={{ padding: 18, background: C.surface, borderRadius: 8, border: `1px solid ${C.border}` }}>
                  <div style={{ fontSize: 11, fontWeight: 700, color: C.textMuted, letterSpacing: "0.05em" }}>AI GATEWAY</div>
                  <div style={{ fontSize: 14, fontWeight: 600, color: C.text, marginTop: 4 }}>● Hybrid (Ollama + Heuristic Failover)</div>
                  <div style={{ fontSize: 12, color: C.textSec, marginTop: 4 }}>Zero downtime SLA protection</div>
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* TAB 2: CANDIDATES */}
        {tab === "candidates" && (
          <Card style={{ padding: 24 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
              <div style={{ fontSize: 16, fontWeight: 700, color: C.text }}>Candidate Governance Table</div>
              <span style={{ fontSize: 12, color: C.textSec }}>Role-Based Access Control</span>
            </div>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13, textAlign: "left" }}>
                <thead>
                  <tr style={{ borderBottom: `2px solid ${C.border}`, color: C.textMuted, fontSize: 11 }}>
                    <th style={{ padding: "10px 12px" }}>CANDIDATE</th>
                    <th style={{ padding: "10px 12px" }}>DETECTED ROLE</th>
                    <th style={{ padding: "10px 12px" }}>VERIFICATION</th>
                    <th style={{ padding: "10px 12px" }}>TESTS</th>
                    <th style={{ padding: "10px 12px" }}>STATUS</th>
                    <th style={{ padding: "10px 12px", textAlign: "right" }}>ACTIONS</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(u => (
                    <tr key={u.id} style={{ borderBottom: `1px solid ${C.border}` }}>
                      <td style={{ padding: "14px 12px" }}>
                        <div style={{ fontWeight: 600, color: C.text }}>{u.name}</div>
                        <div style={{ fontSize: 11, color: C.textSec }}>{u.email}</div>
                      </td>
                      <td style={{ padding: "14px 12px", color: C.text }}>{u.detected_role || "Not Analyzed"}</td>
                      <td style={{ padding: "14px 12px" }}>
                        <Badge
                          color={u.verification_score >= 80 ? C.green : C.textSec}
                          bg={u.verification_score >= 80 ? C.greenPale : C.grayBadge}
                          border={u.verification_score >= 80 ? C.greenBorder : C.border}
                        >
                          {u.verification_score ? `${u.verification_score}% Score` : "Unverified"}
                        </Badge>
                      </td>
                      <td style={{ padding: "14px 12px", color: C.text }}>{u.tests_count || 0}</td>
                      <td style={{ padding: "14px 12px" }}>
                        <Badge
                          color={u.status === "active" ? C.green : C.red}
                          bg={u.status === "active" ? C.greenPale : C.redPale}
                          border={u.status === "active" ? C.greenBorder : C.redBorder}
                        >
                          {u.status.toUpperCase()}
                        </Badge>
                      </td>
                      <td style={{ padding: "14px 12px", textAlign: "right" }}>
                        <div style={{ display: "inline-flex", gap: 8 }}>
                          <button
                            onClick={() => handleToggleStatus(u.id, u.status)}
                            style={{
                              padding: "5px 12px", borderRadius: 6,
                              border: `1px solid ${u.status === "active" ? C.redBorder : C.greenBorder}`,
                              background: u.status === "active" ? C.redPale : C.greenPale,
                              color: u.status === "active" ? C.red : C.green,
                              cursor: "pointer", fontSize: 12, fontWeight: 500
                            }}
                          >
                            {u.status === "active" ? "Suspend" : "Activate"}
                          </button>
                          <button
                            onClick={() => handleToggleRole(u.id, u.role)}
                            style={{
                              padding: "5px 12px", borderRadius: 6,
                              border: `1px solid ${C.border}`,
                              background: "#ffffff", color: C.textSec,
                              cursor: "pointer", fontSize: 12, fontWeight: 500
                            }}
                          >
                            {u.role === "admin" ? "Demote" : "Make Admin"}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {/* TAB 3: QUESTIONS */}
        {tab === "questions" && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
              <div>
                <div style={{ fontSize: 16, fontWeight: 700, color: C.text }}>Mock Exam & Skill Test Bank</div>
                <div style={{ fontSize: 13, color: C.textSec }}>Real-time CRUD management for company & skill questions</div>
              </div>
              <OrangeButton onClick={() => setShowAddModal(true)}>
                + Add Question
              </OrangeButton>
            </div>

            {showAddModal && (
              <Card style={{ marginBottom: 24, padding: 24, borderColor: C.orangeBorder, background: "#ffffff" }}>
                <div style={{ fontSize: 15, fontWeight: 700, color: C.orange, marginBottom: 16 }}>Create New Question</div>
                <form onSubmit={handleCreateQuestion}>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 14 }}>
                    <div>
                      <label style={{ fontSize: 11, fontWeight: 600, color: C.textSec, display: "block", marginBottom: 4 }}>Target Company</label>
                      <input value={newQ.company} onChange={e => setNewQ({ ...newQ, company: e.target.value })} style={{ width: "100%", padding: 9, border: `1px solid ${C.border}`, borderRadius: 6, fontSize: 13 }} />
                    </div>
                    <div>
                      <label style={{ fontSize: 11, fontWeight: 600, color: C.textSec, display: "block", marginBottom: 4 }}>Target Role</label>
                      <input value={newQ.role} onChange={e => setNewQ({ ...newQ, role: e.target.value })} style={{ width: "100%", padding: 9, border: `1px solid ${C.border}`, borderRadius: 6, fontSize: 13 }} />
                    </div>
                    <div>
                      <label style={{ fontSize: 11, fontWeight: 600, color: C.textSec, display: "block", marginBottom: 4 }}>Interview Round</label>
                      <input value={newQ.round} onChange={e => setNewQ({ ...newQ, round: e.target.value })} style={{ width: "100%", padding: 9, border: `1px solid ${C.border}`, borderRadius: 6, fontSize: 13 }} />
                    </div>
                  </div>
                  <div style={{ marginBottom: 14 }}>
                    <label style={{ fontSize: 11, fontWeight: 600, color: C.textSec, display: "block", marginBottom: 4 }}>Question Text</label>
                    <textarea required value={newQ.question} onChange={e => setNewQ({ ...newQ, question: e.target.value })} rows={2} style={{ width: "100%", padding: 9, border: `1px solid ${C.border}`, borderRadius: 6, fontSize: 13 }} />
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 14 }}>
                    <input placeholder="Option A" required value={newQ.optA} onChange={e => setNewQ({ ...newQ, optA: e.target.value })} style={{ padding: 9, border: `1px solid ${C.border}`, borderRadius: 6, fontSize: 13 }} />
                    <input placeholder="Option B" required value={newQ.optB} onChange={e => setNewQ({ ...newQ, optB: e.target.value })} style={{ padding: 9, border: `1px solid ${C.border}`, borderRadius: 6, fontSize: 13 }} />
                    <input placeholder="Option C" required value={newQ.optC} onChange={e => setNewQ({ ...newQ, optC: e.target.value })} style={{ padding: 9, border: `1px solid ${C.border}`, borderRadius: 6, fontSize: 13 }} />
                    <input placeholder="Option D" required value={newQ.optD} onChange={e => setNewQ({ ...newQ, optD: e.target.value })} style={{ padding: 9, border: `1px solid ${C.border}`, borderRadius: 6, fontSize: 13 }} />
                  </div>
                  <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 18 }}>
                    <span style={{ fontSize: 13, color: C.textSec, fontWeight: 600 }}>Correct Answer:</span>
                    {["A", "B", "C", "D"].map(letter => (
                      <button
                        type="button"
                        key={letter}
                        onClick={() => setNewQ({ ...newQ, correct: letter })}
                        style={{
                          padding: "6px 14px", borderRadius: 6,
                          border: `1px solid ${newQ.correct === letter ? C.orange : C.border}`,
                          background: newQ.correct === letter ? C.orangePale : "#ffffff",
                          color: newQ.correct === letter ? C.orange : C.textSec,
                          cursor: "pointer", fontWeight: 600, fontSize: 13
                        }}
                      >
                        {letter}
                      </button>
                    ))}
                  </div>
                  <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
                    <OutlineButton onClick={() => setShowAddModal(false)}>Cancel</OutlineButton>
                    <OrangeButton type="submit">Save Question</OrangeButton>
                  </div>
                </form>
              </Card>
            )}

            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {questions.map(q => (
                <Card key={q.id} style={{ padding: 20 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
                    <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                      <Badge color={C.orange}>{q.company}</Badge>
                      <Badge color={C.textSec} bg={C.grayBadge} border={C.border}>{q.role}</Badge>
                      <Badge color={C.textSec} bg={C.grayBadge} border={C.border}>{q.round || "Technical"}</Badge>
                      <Badge color={C.green} bg={C.greenPale} border={C.greenBorder}>{q.difficulty}</Badge>
                    </div>
                    <button
                      onClick={() => handleDeleteQuestion(q.id)}
                      style={{ background: "none", border: "none", color: C.red, cursor: "pointer", fontSize: 12, fontWeight: 500 }}
                    >
                      Delete
                    </button>
                  </div>
                  <div style={{ fontSize: 14, fontWeight: 600, color: C.text, marginBottom: 12 }}>{q.question}</div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 10, fontSize: 13, color: C.textSec }}>
                    {(q.options || []).map((o, idx) => (
                      <div
                        key={idx}
                        style={{
                          padding: "8px 12px",
                          borderRadius: 6,
                          border: `1px solid ${o.startsWith(q.correct_answer) ? C.greenBorder : C.border}`,
                          background: o.startsWith(q.correct_answer) ? C.greenPale : C.surface,
                          color: o.startsWith(q.correct_answer) ? C.green : C.text
                        }}
                      >
                        {o}
                      </div>
                    ))}
                  </div>
                  {q.explanation && (
                    <div style={{ fontSize: 12, color: C.textMuted, marginTop: 6 }}>💡 {q.explanation}</div>
                  )}
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* TAB 4: AI OPS */}
        {tab === "ai_ops" && (
          <Card style={{ padding: 24 }}>
            <div style={{ fontSize: 16, fontWeight: 700, color: C.text, marginBottom: 16 }}>AI Inference Gateway & Optimization</div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
              <div style={{ padding: 20, background: C.surface, borderRadius: 8, border: `1px solid ${C.border}` }}>
                <div style={{ fontSize: 14, fontWeight: 700, color: C.text, marginBottom: 12 }}>Active Local Configuration</div>
                <div style={{ fontSize: 13, color: C.textSec, lineHeight: 2 }}>
                  <div><strong>Inference Mode:</strong> Hybrid (Ollama + Rule-based Heuristic)</div>
                  <div><strong>Target Model:</strong> <code>phi (3.8B Quantized Q4)</code></div>
                  <div><strong>KV Cache Budget:</strong> <code>num_ctx: 2048</code></div>
                  <div><strong>Output Budget:</strong> Dynamic (500–3500 tokens)</div>
                  <div><strong>AWS Bedrock Ready:</strong> Claude 3.5 Sonnet / Llama 3 hook</div>
                </div>
              </div>
              <div style={{ padding: 20, background: C.surface, borderRadius: 8, border: `1px solid ${C.border}` }}>
                <div style={{ fontSize: 14, fontWeight: 700, color: C.text, marginBottom: 12 }}>Low-Spec PC Optimization Rules</div>
                <ul style={{ fontSize: 13, color: C.textSec, lineHeight: 1.8, paddingLeft: 18 }}>
                  <li>Quantization (INT4 / Q4_K_M) reduces RAM bus traffic by 75%.</li>
                  <li>Limiting context to 2048 prevents KV Cache allocation spikes.</li>
                  <li>Heuristic fallback executes instantly if local LLM is offline.</li>
                </ul>
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};

// ── Resume & Verify Page (Clean White & Orange) ─────────────────────────────
const ResumePage = ({ setPage }) => {
  const [text, setText] = useState("");
  const [github, setGithub] = useState("");
  const [linkedin, setLinkedin] = useState("");
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [err, setErr] = useState("");
  const [profile, setProfileLocal] = useState(getProfile());

  const analyze = async () => {
    if (!text.trim()) { setErr("Paste your resume content to proceed."); return; }
    setLoading(true); setErr("");
    try {
      const p = await analyzeResumeFull({ text, github, linkedin });
      setProfileLocal(p);
    } catch (e) {
      setErr(e.message || "Failed to analyze resume");
    }
    setLoading(false);
  };

  const runVerify = async () => {
    setVerifying(true);
    try {
      const gh = await verifyGitHub(github || profile?.github_username);
      const v = await verifyProfileWithAI(profile, gh, linkedin || profile?.linkedin_url, profile?.matched_skills);
      setProfileLocal({ ...(profile || {}), verification: v });
    } catch (e) {
      setErr(e.message || "Verification failed");
    }
    setVerifying(false);
  };

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#ffffff", color: C.text }}>
      <Sidebar page="resume" setPage={setPage} />
      <div style={{ flex: 1, padding: "36px 48px", overflowY: "auto", background: C.surface }}>
        <h1 style={{ fontSize: 24, fontWeight: 800, color: C.text, marginBottom: 4 }}>Resume Intelligence & Verification</h1>
        <p style={{ color: C.textSec, fontSize: 14, marginBottom: 28 }}>Extract skills, audit online footprint, and verify claimed competencies</p>

        <div style={{ display: "grid", gridTemplateColumns: "1.2fr 0.8fr", gap: 24, maxWidth: 1100 }}>
          {/* Form */}
          <div>
            <Card style={{ padding: 24 }}>
              <div style={{ fontSize: 15, fontWeight: 700, color: C.text, marginBottom: 14 }}>Resume Plain Text</div>
              <textarea
                value={text}
                onChange={e => setText(e.target.value)}
                placeholder="Paste your plain text resume or work experience details here..."
                rows={11}
                style={{
                  width: "100%", padding: 14, borderRadius: 8,
                  border: `1px solid ${C.border}`, background: "#ffffff",
                  color: C.text, fontSize: 13, resize: "vertical",
                  outline: "none", marginBottom: 18, boxSizing: "border-box"
                }}
              />
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 18 }}>
                <div>
                  <label style={{ fontSize: 12, fontWeight: 600, color: C.textSec, display: "block", marginBottom: 6 }}>GitHub Username</label>
                  <input
                    value={github}
                    onChange={e => setGithub(e.target.value)}
                    placeholder="e.g. torvalds"
                    style={{ width: "100%", padding: 10, borderRadius: 6, border: `1px solid ${C.border}`, fontSize: 13, boxSizing: "border-box" }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: 12, fontWeight: 600, color: C.textSec, display: "block", marginBottom: 6 }}>LinkedIn Profile URL</label>
                  <input
                    value={linkedin}
                    onChange={e => setLinkedin(e.target.value)}
                    placeholder="https://linkedin.com/in/..."
                    style={{ width: "100%", padding: 10, borderRadius: 6, border: `1px solid ${C.border}`, fontSize: 13, boxSizing: "border-box" }}
                  />
                </div>
              </div>

              {err && (
                <div style={{ padding: "10px 14px", background: C.redPale, border: `1px solid ${C.redBorder}`, borderRadius: 8, color: C.red, fontSize: 13, marginBottom: 16 }}>
                  {err}
                </div>
              )}

              <OrangeButton onClick={analyze} loading={loading} style={{ width: "100%", padding: 12 }}>
                Analyze Resume with AI →
              </OrangeButton>
            </Card>
          </div>

          {/* Profile Card */}
          <div>
            {profile ? (
              <Card style={{ padding: 24 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
                  <span style={{ fontSize: 12, fontWeight: 700, color: C.textMuted }}>AI PROFILE REPORT</span>
                  <Badge color={C.textSec} bg={C.grayBadge} border={C.border}>{profile.years_experience}</Badge>
                </div>
                <div style={{ fontSize: 20, fontWeight: 800, color: C.orange, marginBottom: 8 }}>{profile.detected_role}</div>
                <p style={{ fontSize: 13, color: C.textSec, lineHeight: 1.6, marginBottom: 18 }}>{profile.ai_summary}</p>

                <div style={{ marginBottom: 18 }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: C.textMuted, marginBottom: 8 }}>MATCHED SKILLS</div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                    {(profile.matched_skills || []).map(s => (
                      <Badge key={s} color={C.orange} bg={C.orangePale} border={C.orangeBorder}>{s}</Badge>
                    ))}
                  </div>
                </div>

                <div style={{ marginBottom: 20 }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: C.textMuted, marginBottom: 8 }}>ACTIONABLE TIPS</div>
                  <ul style={{ fontSize: 13, color: C.textSec, paddingLeft: 18, lineHeight: 1.7 }}>
                    {(profile.improvement_tips || []).map((t, idx) => <li key={idx}>{t}</li>)}
                  </ul>
                </div>

                <OutlineButton onClick={runVerify} disabled={verifying} style={{ width: "100%", padding: 11 }}>
                  {verifying ? "Verifying Footprint…" : "Run Live Verification Audit →"}
                </OutlineButton>

                {profile.verification && (
                  <div style={{ marginTop: 18, padding: 16, borderRadius: 8, background: C.surface, border: `1px solid ${C.border}` }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                      <span style={{ fontSize: 13, fontWeight: 600 }}>Verification Score</span>
                      <span style={{ fontSize: 16, fontWeight: 800, color: C.green }}>{profile.verification.verification_score}%</span>
                    </div>
                    <div style={{ fontSize: 12, color: C.textSec }}>{profile.verification.github_insight}</div>
                  </div>
                )}
              </Card>
            ) : (
              <Card style={{ textAlign: "center", padding: 48 }}>
                <Icon name="upload" size={36} color={C.textMuted} />
                <div style={{ fontSize: 14, fontWeight: 600, color: C.text, marginTop: 14 }}>No Profile Analyzed</div>
                <p style={{ fontSize: 13, color: C.textSec, marginTop: 4 }}>Paste your resume on the left to extract skills and generate your profile.</p>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// ── Quiz Engine (Clean White Card & Clean Options) ─────────────────────────
const QuizEngine = ({ questions, role, testType, onFinish, setPage, sidebar }) => {
  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(30 * 60);
  const answersRef = useRef({});
  const timerRef = useRef(null);

  const finish = (finalAnswers) => {
    clearInterval(timerRef.current);
    const ans = finalAnswers || answersRef.current;
    let correct = 0;
    questions.forEach(q => {
      const a = ans[q.id];
      if (a && a[0] === q.correct_answer) correct += 1;
    });
    const pct = questions.length ? Math.round((correct / questions.length) * 100) : 0;
    const grade = pct >= 80 ? "Excellent 🏆" : pct >= 60 ? "Good 👍" : "Needs Review 📚";
    const result = { role, testType, score: pct, correct, total: questions.length, grade, taken_at: new Date().toISOString() };
    saveTest(result);
    recordTestSubmission({ test_type: testType, role, questions, answers: ans });
    onFinish(result);
  };

  useEffect(() => {
    timerRef.current = setInterval(() => setTimeLeft(t => {
      if (t <= 1) { clearInterval(timerRef.current); finish(answersRef.current); return 0; }
      return t - 1;
    }), 1000);
    return () => clearInterval(timerRef.current);
  }, []);

  const handleAnswer = (opt) => {
    if (answers[q.id] !== undefined) return;
    const updated = { ...answers, [q.id]: opt };
    answersRef.current = updated;
    setAnswers(updated);
  };

  const mm = String(Math.floor(timeLeft / 60)).padStart(2, "0");
  const ss = String(timeLeft % 60).padStart(2, "0");
  const q = questions[current] || {};
  const answered = answers[q.id];

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#ffffff", color: C.text }}>
      <Sidebar page={sidebar} setPage={setPage} />
      <div style={{ flex: 1, padding: "32px 48px", overflowY: "auto", background: C.surface }}>
        {/* Header Bar */}
        <div style={{
          display: "flex", justifyContent: "space-between", alignItems: "center",
          marginBottom: 20, padding: "14px 20px", background: "#ffffff",
          borderRadius: 8, border: `1px solid ${C.border}`
        }}>
          <div style={{ display: "flex", gap: 8 }}>
            <Badge color={C.orange}>{role}</Badge>
            <Badge color={C.textSec} bg={C.grayBadge} border={C.border}>{testType}</Badge>
          </div>
          <div style={{ fontSize: 13, color: C.textSec, fontWeight: 500 }}>Question {current + 1} of {questions.length}</div>
          <div style={{ fontSize: 16, fontWeight: 800, color: timeLeft < 120 ? C.red : C.text, fontVariantNumeric: "tabular-nums" }}>{mm}:{ss}</div>
        </div>

        {/* Question Navigator */}
        <div style={{ display: "flex", gap: 5, marginBottom: 20, flexWrap: "wrap" }}>
          {questions.map((item, i) => {
            const a = answers[item.id];
            const isOk = a && a[0] === item.correct_answer;
            return (
              <button
                key={item.id}
                onClick={() => setCurrent(i)}
                style={{
                  width: 28, height: 28, borderRadius: 6,
                  border: i === current ? `2px solid ${C.orange}` : `1px solid ${C.border}`,
                  background: i === current ? C.orange : (a ? (isOk ? C.greenPale : C.redPale) : "#ffffff"),
                  color: i === current ? "#ffffff" : (a ? (isOk ? C.green : C.red) : C.textSec),
                  cursor: "pointer", fontSize: 11, fontWeight: 600
                }}
              >
                {i + 1}
              </button>
            );
          })}
        </div>

        {/* Question Card */}
        {q && (
          <Card style={{ maxWidth: 740, padding: 28 }}>
            <div style={{ display: "flex", gap: 8, marginBottom: 14 }}>
              <Badge color={q.difficulty === "Easy" ? C.green : (q.difficulty === "Medium" ? C.orange : C.red)}>
                {q.difficulty}
              </Badge>
              <Badge color={C.textSec} bg={C.grayBadge} border={C.border}>{q.skill_tested}</Badge>
            </div>
            <p style={{ fontSize: 16, fontWeight: 600, lineHeight: 1.6, marginBottom: 20, color: C.text }}>{q.question}</p>

            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {(q.options || []).map(opt => {
                const letter = opt[0];
                const isSelected = answered === opt;
                const isCorrect = letter === q.correct_answer;

                let bg = "#ffffff", border = C.border, col = C.text;
                if (answered) {
                  if (isCorrect) { bg = C.greenPale; border = C.greenBorder; col = C.green; }
                  else if (isSelected) { bg = C.redPale; border = C.redBorder; col = C.red; }
                  else col = C.textMuted;
                }

                return (
                  <button
                    key={opt}
                    onClick={() => handleAnswer(opt)}
                    disabled={!!answered}
                    style={{
                      padding: "12px 16px", borderRadius: 8,
                      border: `1px solid ${border}`, background: bg,
                      color: col, fontSize: 14, textAlign: "left",
                      cursor: answered ? "default" : "pointer",
                      transition: "all 0.15s ease"
                    }}
                  >
                    {opt}
                  </button>
                );
              })}
            </div>

            {answered && (
              <div style={{
                marginTop: 18, padding: "12px 16px", borderRadius: 8,
                background: answered[0] === q.correct_answer ? C.greenPale : C.redPale,
                border: `1px solid ${answered[0] === q.correct_answer ? C.greenBorder : C.redBorder}`
              }}>
                <div style={{ fontWeight: 700, fontSize: 13, color: answered[0] === q.correct_answer ? C.green : C.red, marginBottom: 4 }}>
                  {answered[0] === q.correct_answer ? "✓ Correct!" : `✗ Incorrect — Correct Answer: ${q.correct_answer}`}
                </div>
                <p style={{ fontSize: 13, color: C.textSec, lineHeight: 1.5 }}>{q.explanation}</p>
              </div>
            )}

            <div style={{ display: "flex", justifyContent: "space-between", marginTop: 24, paddingTop: 16, borderTop: `1px solid ${C.borderLight}` }}>
              <OutlineButton onClick={() => setCurrent(c => Math.max(0, c - 1))} disabled={current === 0}>
                ← Prev
              </OutlineButton>
              {current < questions.length - 1 ? (
                <OrangeButton onClick={() => setCurrent(c => c + 1)}>
                  Next →
                </OrangeButton>
              ) : (
                <OrangeButton onClick={() => finish(answers)}>
                  Finish & Submit Exam
                </OrangeButton>
              )}
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};

// ── Quiz Results ───────────────────────────────────────────────────────────
const QuizResults = ({ result, onRetry, setPage, sidebar }) => (
  <div style={{ display: "flex", minHeight: "100vh", background: "#ffffff", color: C.text }}>
    <Sidebar page={sidebar} setPage={setPage} />
    <div style={{ flex: 1, padding: "48px 48px", overflowY: "auto", background: C.surface }}>
      <div style={{ maxWidth: 520, margin: "0 auto", textAlign: "center" }}>
        <div style={{
          width: 64, height: 64, borderRadius: "50%",
          background: result.score >= 60 ? C.greenPale : C.redPale,
          display: "flex", alignItems: "center", justifyContent: "center",
          margin: "0 auto 18px", border: `2px solid ${result.score >= 60 ? C.greenBorder : C.redBorder}`
        }}>
          <Icon name={result.score >= 60 ? "trophy" : "shield"} size={28} color={result.score >= 60 ? C.green : C.red} />
        </div>
        <h2 style={{ fontSize: 24, fontWeight: 800, color: C.text, marginBottom: 6 }}>Exam Completed</h2>
        <p style={{ color: C.textSec, fontSize: 14, marginBottom: 24 }}>{result.role} · {result.testType}</p>

        <Card style={{ padding: 32, marginBottom: 24 }}>
          <div style={{ fontSize: 52, fontWeight: 800, color: result.score >= 60 ? C.green : C.orange }}>
            {result.score}%
          </div>
          <div style={{ fontSize: 14, color: C.textSec, marginTop: 4 }}>
            Answered {result.correct} of {result.total} questions correctly
          </div>
          <div style={{ marginTop: 14 }}>
            <Badge color={result.score >= 60 ? C.green : C.orange} bg={result.score >= 60 ? C.greenPale : C.orangePale} border={result.score >= 60 ? C.greenBorder : C.orangeBorder}>
              {result.grade}
            </Badge>
          </div>
        </Card>

        <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
          <OutlineButton onClick={onRetry}>Retake Test</OutlineButton>
          <OrangeButton onClick={() => setPage("learning")}>View Recommended Roadmap →</OrangeButton>
        </div>
      </div>
    </div>
  </div>
);

// ── Skill Test Page ────────────────────────────────────────────────────────
const SkillTestPage = ({ setPage }) => {
  const [phase, setPhase] = useState("idle");
  const [questions, setQuestions] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const profile = getProfile();

  const start = async () => {
    if (!profile) { setErr("Upload resume first."); return; }
    setLoading(true); setErr("");
    try {
      const allSkills = [...(profile.matched_skills || []), ...(profile.extra_skills || [])];
      const qs = await generateSkillVerificationTest(profile, allSkills);
      setQuestions(qs);
      setPhase("testing");
    } catch (e) {
      setErr(e.message || "Failed to generate test");
    }
    setLoading(false);
  };

  if (phase === "testing") return <QuizEngine questions={questions} role={profile?.detected_role || "Software Engineer"} testType="Skill Verification" onFinish={r => { setResult(r); setPhase("results"); }} setPage={setPage} sidebar="skill-test" />;
  if (phase === "results" && result) return <QuizResults result={result} onRetry={() => { setResult(null); setPhase("idle"); }} setPage={setPage} sidebar="skill-test" />;

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#ffffff", color: C.text }}>
      <Sidebar page="skill-test" setPage={setPage} />
      <div style={{ flex: 1, padding: "36px 48px", overflowY: "auto", background: C.surface }}>
        <h1 style={{ fontSize: 24, fontWeight: 800, color: C.text, marginBottom: 5 }}>30Q Skill Verification Test</h1>
        <p style={{ color: C.textSec, fontSize: 14, marginBottom: 28 }}>Adaptive 30 questions generated from your exact resume skills across 3 difficulty tiers</p>

        {!profile && (
          <Card style={{ maxWidth: 520, padding: 24, borderColor: C.orangeBorder }}>
            <p style={{ color: C.orange, fontSize: 14, fontWeight: 500 }}>⚠️ Upload your resume first so questions target your competencies.</p>
            <OrangeButton onClick={() => setPage("resume")} style={{ marginTop: 14 }}>
              Go to Resume Upload
            </OrangeButton>
          </Card>
        )}

        {profile && (
          <Card style={{ maxWidth: 620, padding: 28 }}>
            <div style={{ fontSize: 14, fontWeight: 700, color: C.text, marginBottom: 10 }}>Targeting Competencies from {profile.detected_role}:</div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 20 }}>
              {(profile.matched_skills || []).map(s => (
                <Badge key={s} color={C.orange}>{s}</Badge>
              ))}
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 24 }}>
              <div style={{ textAlign: "center", padding: 14, background: C.surface, borderRadius: 8, border: `1px solid ${C.border}` }}>
                <div style={{ fontSize: 20, fontWeight: 800, color: C.text }}>30</div>
                <div style={{ fontSize: 12, color: C.textMuted, marginTop: 2 }}>Questions</div>
              </div>
              <div style={{ textAlign: "center", padding: 14, background: C.surface, borderRadius: 8, border: `1px solid ${C.border}` }}>
                <div style={{ fontSize: 20, fontWeight: 800, color: C.green }}>10 Easy</div>
                <div style={{ fontSize: 12, color: C.textMuted, marginTop: 2 }}>Definitions</div>
              </div>
              <div style={{ textAlign: "center", padding: 14, background: C.surface, borderRadius: 8, border: `1px solid ${C.border}` }}>
                <div style={{ fontSize: 20, fontWeight: 800, color: C.orange }}>8 Hard</div>
                <div style={{ fontSize: 12, color: C.textMuted, marginTop: 2 }}>Edge Cases</div>
              </div>
            </div>

            {err && (
              <div style={{ padding: "10px 14px", background: C.redPale, border: `1px solid ${C.redBorder}`, borderRadius: 8, color: C.red, fontSize: 13, marginBottom: 16 }}>
                {err}
              </div>
            )}

            <OrangeButton onClick={start} loading={loading} style={{ width: "100%", padding: 12 }}>
              Start 30Q Skill Verification Test →
            </OrangeButton>
          </Card>
        )}
      </div>
    </div>
  );
};

// ── Company Mock Test Page ─────────────────────────────────────────────────
const CompanyTestPage = ({ setPage }) => {
  const [phase, setPhase] = useState("idle");
  const [company, setCompany] = useState("Google");
  const [role, setRole] = useState("Software Engineer");
  const [year, setYear] = useState("2024");
  const [questions, setQuestions] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  const start = async () => {
    setLoading(true); setErr("");
    try {
      const qs = await generateCompanyTest(company, role, year);
      setQuestions(qs);
      setPhase("testing");
    } catch (e) {
      setErr(e.message || "Failed to generate company mock");
    }
    setLoading(false);
  };

  if (phase === "testing") return <QuizEngine questions={questions} role={`${company} — ${role}`} testType="Company Mock" onFinish={r => { setResult(r); setPhase("results"); }} setPage={setPage} sidebar="mock-test" />;
  if (phase === "results" && result) return <QuizResults result={result} onRetry={() => { setResult(null); setPhase("idle"); }} setPage={setPage} sidebar="mock-test" />;

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#ffffff", color: C.text }}>
      <Sidebar page="mock-test" setPage={setPage} />
      <div style={{ flex: 1, padding: "36px 48px", overflowY: "auto", background: C.surface }}>
        <h1 style={{ fontSize: 24, fontWeight: 800, color: C.text, marginBottom: 5 }}>Company Mock Interview Simulator</h1>
        <p style={{ color: C.textSec, fontSize: 14, marginBottom: 28 }}>30 questions modeled after documented company interview patterns</p>

        <Card style={{ maxWidth: 560, padding: 28 }}>
          <div style={{ marginBottom: 18 }}>
            <label style={{ fontSize: 12, fontWeight: 600, color: C.textSec, display: "block", marginBottom: 8 }}>Target Company</label>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              {["Google", "Amazon", "Microsoft", "TCS", "Infosys", "Swiggy"].map(c => (
                <button
                  key={c}
                  type="button"
                  onClick={() => setCompany(c)}
                  style={{
                    padding: "7px 14px", borderRadius: 6,
                    border: `1px solid ${company === c ? C.orange : C.border}`,
                    background: company === c ? C.orangePale : "#ffffff",
                    color: company === c ? C.orange : C.textSec,
                    cursor: "pointer", fontSize: 13, fontWeight: 600
                  }}
                >
                  {c}
                </button>
              ))}
            </div>
          </div>

          <div style={{ marginBottom: 20 }}>
            <label style={{ fontSize: 12, fontWeight: 600, color: C.textSec, display: "block", marginBottom: 8 }}>Role / Position</label>
            <input
              value={role}
              onChange={e => setRole(e.target.value)}
              style={{ width: "100%", padding: 10, border: `1px solid ${C.border}`, borderRadius: 6, fontSize: 13, boxSizing: "border-box" }}
            />
          </div>

          {err && (
            <div style={{ padding: "10px 14px", background: C.redPale, border: `1px solid ${C.redBorder}`, borderRadius: 8, color: C.red, fontSize: 13, marginBottom: 16 }}>
              {err}
            </div>
          )}

          <OrangeButton onClick={start} loading={loading} style={{ width: "100%", padding: 12 }}>
            Start {company} Mock Interview →
          </OrangeButton>
        </Card>
      </div>
    </div>
  );
};

// ── Learning Path Page (Clean Roadmap) ─────────────────────────────────────
const LearningPage = ({ setPage }) => {
  const [plan, setPlan] = useState(store.get("sl_learning") || null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const profile = getProfile();

  const generate = async () => {
    setLoading(true); setErr("");
    try {
      const p = await generateLearningPlan(profile, profile?.verification);
      setPlan(p);
      store.set("sl_learning", p);
    } catch (e) {
      setErr(e.message || "Failed to generate learning roadmap");
    }
    setLoading(false);
  };

  const handleMilestone = (idx) => {
    if (!plan) return;
    const updated = plan.map((item, i) => i === idx ? { ...item, completed: !item.completed } : item);
    setPlan(updated);
    store.set("sl_learning", updated);
  };

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#ffffff", color: C.text }}>
      <Sidebar page="learning" setPage={setPage} />
      <div style={{ flex: 1, padding: "36px 48px", overflowY: "auto", background: C.surface }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 28 }}>
          <div>
            <h1 style={{ fontSize: 24, fontWeight: 800, color: C.text, marginBottom: 4 }}>Certified Learning Path</h1>
            <p style={{ color: C.textSec, fontSize: 14 }}>Curated accredited courses and practical tutorials targeting verified gaps</p>
          </div>
          <OrangeButton onClick={generate} loading={loading}>
            {plan ? "Regenerate Roadmap" : "Generate Plan"}
          </OrangeButton>
        </div>

        {!plan && (
          <Card style={{ maxWidth: 520, padding: 28 }}>
            <div style={{ fontSize: 15, fontWeight: 700, color: C.text, marginBottom: 8 }}>Ready to bridge your skill gaps?</div>
            <p style={{ fontSize: 13, color: C.textSec, marginBottom: 18, lineHeight: 1.6 }}>Generate an accredited roadmap prioritizing Coursera, edX, and YouTube tutorials based on your assessment results.</p>
            <OrangeButton onClick={generate}>Generate Learning Path →</OrangeButton>
          </Card>
        )}

        {plan && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16, maxWidth: 900 }}>
            {plan.map((item, idx) => (
              <Card key={idx} style={{ padding: 22, borderLeft: item.completed ? `4px solid ${C.green}` : `4px solid ${C.orange}` }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <input
                      type="checkbox"
                      checked={!!item.completed}
                      onChange={() => handleMilestone(idx)}
                      style={{ width: 18, height: 18, cursor: "pointer", accentColor: C.orange }}
                    />
                    <span style={{ fontSize: 16, fontWeight: 700, textDecoration: item.completed ? "line-through" : "none", color: C.text }}>
                      {item.skill}
                    </span>
                    <Badge color={item.priority === "High" ? C.red : C.orange} bg={item.priority === "High" ? C.redPale : C.orangePale} border={item.priority === "High" ? C.redBorder : C.orangeBorder}>
                      {item.priority} Priority
                    </Badge>
                  </div>
                  <span style={{ fontSize: 12, color: C.textMuted }}>~{item.estimated_weeks} weeks</span>
                </div>

                <p style={{ fontSize: 13, color: C.textSec, lineHeight: 1.6, marginBottom: 14 }}>{item.why_important}</p>

                <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                  {(item.resources || []).map((r, rIdx) => (
                    <a
                      key={rIdx}
                      href={r.url}
                      target="_blank"
                      rel="noreferrer"
                      style={{
                        padding: "7px 14px", background: C.surface,
                        border: `1px solid ${C.border}`, borderRadius: 6,
                        color: C.text, textDecoration: "none", fontSize: 12, fontWeight: 600,
                        display: "inline-flex", alignItems: "center", gap: 6
                      }}
                    >
                      ↗ {r.platform}: {r.course_name}
                    </a>
                  ))}
                  {item.youtube_playlist && (
                    <a
                      href={item.youtube_playlist}
                      target="_blank"
                      rel="noreferrer"
                      style={{
                        padding: "7px 14px", background: C.orangePale,
                        border: `1px solid ${C.orangeBorder}`, borderRadius: 6,
                        color: C.orange, textDecoration: "none", fontSize: 12, fontWeight: 600,
                        display: "inline-flex", alignItems: "center", gap: 6
                      }}
                    >
                      ▶ Video Tutorials
                    </a>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// ── Dashboard Page (Minimalist Clean White + Orange) ───────────────────────
const DashboardPage = ({ setPage }) => {
  const auth = getAuth();
  const profile = getProfile();
  const history = getTestHistory();

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#ffffff", color: C.text }}>
      <Sidebar page="dashboard" setPage={setPage} />
      <div style={{ flex: 1, padding: "36px 48px", overflowY: "auto", background: C.surface }}>
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
          <div>
            <h1 style={{ fontSize: 26, fontWeight: 800, color: C.text, margin: 0 }}>Welcome back, {auth?.name || "Candidate"}</h1>
            <p style={{ color: C.textSec, fontSize: 14, marginTop: 4 }}>SkillLens AI Career & Skill Verification Dashboard</p>
          </div>
          {auth?.role === "admin" && (
            <OrangeButton onClick={() => setPage("admin")}>
              Open Admin Console →
            </OrangeButton>
          )}
        </div>

        {/* Metric Cards */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 20, marginBottom: 36 }}>
          <Card style={{ padding: 22 }}>
            <div style={{ fontSize: 13, color: C.textSec, fontWeight: 500, marginBottom: 8 }}>Target Role</div>
            <div style={{ fontSize: 20, fontWeight: 800, color: C.orange }}>
              {profile?.detected_role || "No Resume Yet"}
            </div>
          </Card>
          <Card style={{ padding: 22 }}>
            <div style={{ fontSize: 13, color: C.textSec, fontWeight: 500, marginBottom: 8 }}>Verification Score</div>
            <div style={{ fontSize: 32, fontWeight: 800, color: C.green }}>
              {profile?.verification?.verification_score || 0}%
            </div>
          </Card>
          <Card style={{ padding: 22 }}>
            <div style={{ fontSize: 13, color: C.textSec, fontWeight: 500, marginBottom: 8 }}>Tests Completed</div>
            <div style={{ fontSize: 32, fontWeight: 800, color: C.text }}>
              {history.length}
            </div>
          </Card>
        </div>

        {/* Quick Action Tiles */}
        <div style={{ fontSize: 16, fontWeight: 700, color: C.text, marginBottom: 16 }}>Available Workflows</div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 20 }}>
          {[
            { icon: "upload", t: "Resume & Verify", d: "Upload your resume to extract skills and run live GitHub verification.", p: "resume" },
            { icon: "shield", t: "30Q Skill Test", d: "Verify actual technical competency vs claimed resume skills.", p: "skill-test" },
            { icon: "building", t: "Company Mock", d: "Practice with realistic company interview patterns (Google/Amazon).", p: "mock-test" },
          ].map(c => (
            <div
              key={c.t}
              onClick={() => setPage(c.p)}
              style={{
                padding: 24,
                background: "#ffffff",
                border: `1px solid ${C.border}`,
                borderRadius: 10,
                cursor: "pointer",
                boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.04)",
                transition: "border-color 0.15s ease"
              }}
            >
              <div style={{
                width: 38, height: 38, borderRadius: 8,
                background: C.orangePale, border: `1px solid ${C.orangeBorder}`,
                display: "flex", alignItems: "center", justifyContent: "center",
                marginBottom: 14
              }}>
                <Icon name={c.icon} size={18} color={C.orange} />
              </div>
              <div style={{ fontSize: 16, fontWeight: 700, color: C.text, marginBottom: 6 }}>{c.t}</div>
              <div style={{ fontSize: 13, color: C.textSec, lineHeight: 1.6 }}>{c.d}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ── Root Application ───────────────────────────────────────────────────────
export default function App() {
  const [view, setView] = useState("landing");
  const [authMode, setAuthMode] = useState("login");

  useEffect(() => {
    if (isLoggedIn()) {
      if (isAdmin()) setView("admin");
      else setView("dashboard");
    }
  }, []);

  const go = m => { setAuthMode(m); setView("auth"); };

  if (view === "landing") return <LandingPage onGetStarted={go} />;
  if (view === "auth") return <AuthPage mode={authMode} onSuccess={d => setView(d)} />;
  if (!isLoggedIn()) return <AuthPage mode="login" onSuccess={d => setView(d)} />;

  if (view === "admin") return <AdminConsolePage setPage={setView} />;
  if (view === "resume") return <ResumePage setPage={setView} />;
  if (view === "skill-test") return <SkillTestPage setPage={setView} />;
  if (view === "mock-test") return <CompanyTestPage setPage={setView} />;
  if (view === "learning") return <LearningPage setPage={setView} />;
  return <DashboardPage setPage={setView} />;
}
