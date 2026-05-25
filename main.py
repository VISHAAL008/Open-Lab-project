"""GitHub Repository Analyzer — Multi-page Streamlit App
Pages: landing → browse → analysis (session-state routing)
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timezone
import repo

st.set_page_config(page_title="GitHub Repository Analyzer", page_icon="🔍", layout="wide")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
#MainMenu,footer,header{visibility:hidden;}
.stApp{background:#f5f7fa;}

/* ── Global text color fix ─────────────────────────────────────────── */
.stApp, .stApp p, .stApp span, .stApp div,
.stApp label, .stApp li, .stApp a {
    color: #0f172a;
}
/* Streamlit markdown paragraphs and bold labels */
.stMarkdown p, .stMarkdown strong, .stMarkdown b {
    color: #111827 !important;
    font-size: .95rem;
}
/* Section bold headings inside containers */
[data-testid="stVerticalBlock"] strong {
    color: #111827 !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
}
/* Streamlit widget labels */
.stTextInput label, .stSelectbox label,
.stSlider label, .stNumberInput label {
    color: #111827 !important;
    font-weight: 700 !important;
    font-size: .9rem !important;
}
/* ── Clean white input fields ──────────────────────────────────────── */
.stTextInput input {
    color: #111827 !important;
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 8px !important;
    font-size: .95rem !important;
    padding: .55rem .9rem !important;
    box-shadow: 0 1px 2px rgba(0,0,0,.04);
    transition: border-color .15s, box-shadow .15s;
}
.stTextInput input:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,.15) !important;
    outline: none !important;
}
.stTextInput input::placeholder {
    color: #6b7280 !important;
    opacity: 1 !important;
}
/* Selectbox — clean white with darker arrow */
.stSelectbox > div > div {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 8px !important;
}
/* Darker dropdown arrow */
.stSelectbox svg {
    fill: #374151 !important;
    color: #374151 !important;
    opacity: 1 !important;
}
/* Dropdown menu (portal) light theme */
div[data-baseweb="popover"] > div,
div[data-baseweb="menu"], ul[role="listbox"] {
    background-color: #ffffff !important;
}
li[role="option"], div[role="option"] {
    color: #111827 !important;
    background-color: #ffffff !important;
}
li[role="option"]:hover, div[role="option"]:hover {
    background-color: #f1f5f9 !important;
    color: #000000 !important;
}
li[role="option"][aria-selected="true"], div[role="option"][aria-selected="true"] {
    background-color: #e2e8f0 !important;
    font-weight: 600 !important;
}
/* Secondary / muted text */
.stApp [data-testid="stMarkdownContainer"] p {
    color: #1e293b !important;
}

/* center wrapper for landing/analysis */
.cx{max-width:640px;margin:0 auto;}

/* cards */
.rc{background:#fff;border:1px solid #e2e8f0;border-radius:12px;
    padding:1.2rem 1.3rem 0.9rem;box-shadow:0 1px 6px rgba(0,0,0,.06);
    height:100%;position:relative;}
.rc:hover{border-color:#93c5fd;box-shadow:0 4px 16px rgba(59,130,246,.12);}
.rc-name{font-size:1rem;font-weight:700;color:#0f172a;margin-bottom:.25rem;
         white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.rc-desc{font-size:.79rem;color:#64748b;margin-bottom:.6rem;min-height:2.2rem;
         display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
.rc-stats{display:flex;gap:.9rem;font-size:.79rem;color:#64748b;margin-bottom:.6rem;flex-wrap:wrap;}
.rc-foot{display:flex;align-items:center;gap:.5rem;margin-bottom:.7rem;}
.lang-pill{background:#eff6ff;color:#2563eb;font-size:.7rem;font-weight:600;
           padding:.12rem .55rem;border-radius:20px;}
.dot{width:9px;height:9px;border-radius:50%;display:inline-block;flex-shrink:0;}

/* score */
.score-big{font-size:3.5rem;font-weight:700;line-height:1;}
.score-denom{font-size:1.1rem;color:#94a3b8;}
.sec{font-size:.68rem;font-weight:700;text-transform:uppercase;
     letter-spacing:.09em;color:#94a3b8;margin:1.2rem 0 .45rem;}
.sec:first-child{margin-top:0;}
.rrow{display:flex;justify-content:space-between;padding:.45rem 0;
      border-bottom:1px solid #f1f5f9;font-size:.87rem;}
.rrow:last-child{border-bottom:none;}
.rk{color:#64748b;}.rv{color:#0f172a;font-weight:600;}
.lrow{margin-bottom:.45rem;}
.ltop{display:flex;justify-content:space-between;font-size:.79rem;color:#374151;margin-bottom:.14rem;}
.lbg{background:#e2e8f0;border-radius:5px;height:6px;}
.lbar{border-radius:5px;height:6px;}
.rec-box{border-radius:10px;padding:1.1rem 1.3rem;border:1px solid;}
.badge{display:inline-block;padding:.2rem .7rem;border-radius:20px;font-size:.75rem;font-weight:600;}
.b-ex{background:#dcfce7;color:#15803d;}
.b-go{background:#dbeafe;color:#1d4ed8;}
.b-av{background:#fef9c3;color:#92400e;}
.b-ne{background:#fee2e2;color:#b91c1c;}
/* ── ALL buttons base */
div.stButton > button {
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: .88rem !important;
    transition: all .18s ease !important;
}
div.stDownloadButton > button { border-radius: 6px !important; font-weight: 600 !important; }

/* ── PRIMARY — GitHub Blue — all selector variants */
/* by data-testid */
div.stButton > button[data-testid="baseButton-primary"],
/* by kind attribute (older Streamlit) */
div.stButton > button[kind="primary"],
/* stButton first-child when type=primary rendered */
.stButton [data-testid="baseButton-primary"],
[data-testid="stButton"] > button[data-testid="baseButton-primary"] {
    background-color: #4a7fc1 !important;
    background: #4a7fc1 !important;
    color: #ffffff !important;
    border: 1px solid rgba(31,35,40,0.15) !important;
    box-shadow: 0 1px 0 rgba(31,35,40,0.1) !important;
}
div.stButton > button[data-testid="baseButton-primary"]:hover,
div.stButton > button[kind="primary"]:hover {
    background-color: #ffffff !important;
    background: #ffffff !important;
    color: #4a7fc1 !important;
    border: 1.5px solid #4a7fc1 !important;
    box-shadow: 0 4px 14px rgba(74,127,193,.2) !important;
}
div.stButton > button[data-testid="baseButton-primary"]:hover *,
div.stButton > button[kind="primary"]:hover * {
    color: #4a7fc1 !important;
}
div.stButton > button[data-testid="baseButton-primary"] *,
div.stButton > button[kind="primary"] * {
    color: #ffffff !important;
}

/* ── SECONDARY — GitHub style outline (card Analyze buttons) */
div.stButton > button[data-testid="baseButton-secondary"],
div.stButton > button[kind="secondary"] {
    background: #ffffff !important;
    color: #0969da !important;
    border: 1.5px solid #0969da !important;
    transition: background .18s, color .18s, box-shadow .18s;
}
div.stButton > button[data-testid="baseButton-secondary"]:hover,
div.stButton > button[kind="secondary"]:hover {
    background: #ffffff !important;
    color: #0969da !important;
    border: 1.5px solid #0969da !important;
    box-shadow: 0 4px 12px rgba(9,105,218,.2) !important;
}
div.stButton > button[data-testid="baseButton-secondary"] p,
div.stButton > button[data-testid="baseButton-secondary"] span,
div.stButton > button[kind="secondary"] p,
div.stButton > button[kind="secondary"] span {
    color: inherit !important;
}

/* ── BACK / NAV buttons — dark slate */
div.stButton > button[key="browse_back"],
div.stButton > button[key="analysis_back"] {
    background: #1e293b !important;
    color: #ffffff !important;
    border: none !important;
}
div.stButton > button[key="browse_back"]:hover,
div.stButton > button[key="analysis_back"]:hover {
    background: #0f172a !important;
    box-shadow: none !important;
}
div.stButton > button[key="browse_back"] *,
div.stButton > button[key="analysis_back"] * {
    color: #ffffff !important;
}
</style>""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in {"page":"landing","user_repos":[],"browsed_user":"",
              "result_data":None,"p_owner":"","p_repo":"",
              "analysis_source":"landing"}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ───────────────────────────────────────────────────────────────────
PALETTE = ["#3b82f6","#10b981","#f59e0b","#ef4444","#8b5cf6","#06b6d4","#f97316","#84cc16"]
LANG_C  = {"Python":"#3572A5","JavaScript":"#f1e05a","TypeScript":"#2b7489",
           "Java":"#b07219","Go":"#00ADD8","Rust":"#dea584","Ruby":"#701516",
           "C++":"#f34b7d","C#":"#178600","Swift":"#ffac45","PHP":"#4F5D95",
           "Kotlin":"#F18E33","Shell":"#89e051","HTML":"#e34c26","CSS":"#563d7c"}

def go(page):
    st.session_state["page"] = page
    st.rerun()

def nav_analysis(owner, name, source="landing"):
    st.session_state.update({"p_owner":owner,"p_repo":name,
                             "result_data":None,"analysis_source":source})
    go("analysis")

def act_status(updated_raw):
    try:
        d = datetime.strptime(updated_raw, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        days = (datetime.now(timezone.utc) - d).days
    except Exception:
        return "inactive","🔴","#ef4444","Inactive"
    if days < 30:   return "active",  "🟢","#22c55e","Active"
    if days < 180:  return "moderate","🟡","#f59e0b","Moderate"
    return "inactive","🔴","#ef4444","Inactive"

def score_color(s):
    return "#16a34a" if s>=80 else "#2563eb" if s>=60 else "#d97706" if s>=40 else "#dc2626"

def sbadge(label):
    cls={"Excellent":"b-ex","Good":"b-go","Average":"b-av","Needs Improvement":"b-ne"}.get(label,"b-av")
    return f'<span class="badge {cls}">{label}</span>'

def row(k,v):
    return f'<div class="rrow"><span class="rk">{k}</span><span class="rv">{v}</span></div>'

def lang_bars(langs):
    if not langs: return "<p style='color:#94a3b8;font-size:.82rem;'>No language data.</p>"
    h=""
    for i,(lang,pct) in enumerate(list(langs.items())[:10]):
        c=LANG_C.get(lang,PALETTE[i%len(PALETTE)])
        h+=(f'<div class="lrow"><div class="ltop"><span>{lang}</span>'
            f'<span style="color:#94a3b8">{pct}%</span></div>'
            f'<div class="lbg"><div class="lbar" style="width:{min(pct,100)}%;background:{c}"></div></div></div>')
    return h

def get_recommendation(data):
    score = data["score"]
    days  = data.get("days_since_update", 0)
    reasons = []
    if not data.get("readme_exists"):       reasons.append("No README documentation")
    if data.get("license") == "No License": reasons.append("No open source license")
    if days > 180:                          reasons.append(f"Not updated in {days} days")
    if data.get("stars",0) > 0 and data.get("issues",0)/data["stars"] > 0.1:
        reasons.append("High open issue ratio")
    if score >= 72 and len(reasons) == 0:
        return "✅ Recommended", "#15803d", "#f0fdf4", "#86efac", reasons
    elif score >= 45:
        return "⚠️ Use with Caution", "#d97706", "#fffbeb", "#fcd34d", reasons
    return "❌ Not Recommended", "#dc2626", "#fef2f2", "#fca5a5", reasons

def filter_repos(repos, sort, language, min_stars, activity):
    f = repos
    if language != "All":    f = [r for r in f if r.get("language","") == language]
    if min_stars > 0:        f = [r for r in f if r.get("stars",0) >= min_stars]
    if activity  != "All":
        key = {"🟢 Active":"active","🟡 Moderate":"moderate","🔴 Inactive":"inactive"}.get(activity,"")
        f = [r for r in f if act_status(r.get("updated_raw",""))[0] == key]
    if   sort == "⭐ Stars":            f.sort(key=lambda r:r.get("stars",0),   reverse=True)
    elif sort == "🕒 Recently Updated": f.sort(key=lambda r:r.get("updated_raw",""), reverse=True)
    elif sort == "🍴 Forks":            f.sort(key=lambda r:r.get("forks",0),   reverse=True)
    return f

# ── Caching wrappers (↑ rate-limit friendly) ──────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def cached_analyze(owner, rname):
    return repo.analyze_repo(owner, rname)

@st.cache_data(ttl=300, show_spinner=False)
def cached_activity(owner, rname):
    return repo.get_commit_activity(owner, rname)

@st.cache_data(ttl=600, show_spinner=False)
def cached_user_repos(uname, sort_k):
    return repo.fetch_user_repos(uname, sort=sort_k, limit=50)

# ── Score Breakdown ───────────────────────────────────────────────────────────
def get_score_breakdown(data):
    stars  = data.get("stars", 0)
    issues = data.get("issues", 0)
    days   = data.get("days_since_update", 999)
    files  = data.get("total_files", 0)
    readme = data.get("readme_exists", False)
    bd = []
    # Popularity (max 30)
    if stars > 20000: p,n = 30, f"{stars:,} stars — very popular"
    elif stars > 5000: p,n = 25, f"{stars:,} stars — popular"
    else:              p,n = 15, f"{stars:,} stars — niche/new"
    bd.append(("⭐ Popularity", p, 30, n))
    # Health (max 20)
    if stars > 0:
        ratio = issues / stars
        if ratio < 0.02: p,n = 20, f"Issue ratio {ratio:.3f} (healthy)"
        else:            p,n = 10, f"Issue ratio {ratio:.3f} (elevated)"
    else: p,n = 10, "No stars to compare"
    bd.append(("🐞 Issue Health", p, 20, n))
    # Activity (max 20)
    if days < 30:  p,n = 20, f"Updated {days}d ago — active"
    else:          p,n = 10, f"Updated {days}d ago — less active"
    bd.append(("🛠 Activity", p, 20, n))
    # Structure (max 15)
    if files > 100: p,n = 15, f"{files:,} files — well-structured"
    else:           p,n = 5,  f"{files:,} files — small codebase"
    bd.append(("📁 Code Structure", p, 15, n))
    # README (max 15)
    if readme: p,n = 15, "README present — good docs"
    else:      p,n = 0,  "No README found"
    bd.append(("📄 Documentation", p, 15, n))
    return bd

# ── Reasoning Transparency ────────────────────────────────────────────────────
def get_reasoning(data):
    stars   = data.get("stars", 0)
    days    = data.get("days_since_update", 999)
    readme  = data.get("readme_exists", False)
    license_= data.get("license", "No License")
    issues  = data.get("issues", 0)
    out = []
    if stars > 20000: out.append(("pos", "Highly popular with strong community engagement"))
    elif stars > 5000: out.append(("pos", "Well-established with good adoption"))
    else:              out.append(("neu", "Limited adoption — may be niche or early-stage"))
    if days < 30:      out.append(("pos", "Actively maintained — updated within the last month"))
    elif days < 180:   out.append(("neu", f"Moderately active — last updated {days} days ago"))
    else:              out.append(("neg", f"Inactive — not updated in {days} days"))
    if readme:         out.append(("pos", "Has README — easier to onboard and contribute"))
    else:              out.append(("neg", "No README — harder for contributors to understand"))
    if license_ == "No License":
                       out.append(("neg", "No open-source license — limits production/legal use"))
    else:              out.append(("pos", f"Licensed under {license_} — safe for open-source use"))
    if stars > 0 and issues/stars > 0.1:
                       out.append(("neg", "High open issue ratio — may indicate maintenance gaps"))
    elif issues > 0:   out.append(("neu", f"{issues:,} open issues — being tracked"))
    return out

# ═════════════════════════════════════════════════════════════════════════════
# PAGE: LANDING
# ═════════════════════════════════════════════════════════════════════════════
def page_landing():
    st.markdown("<div class='cx'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;font-weight:700;color:#0f172a;"
                "margin-bottom:.15rem;'>🔍 GitHub Repository Analyzer</h2>"
                "<p style='text-align:center;color:#64748b;font-size:.9rem;"
                "margin-bottom:2rem;'>Analyze any public GitHub repository — metrics, score & insights.</p>",
                unsafe_allow_html=True)

    # ── Browse by username ───────────────────────────────────────────────
    with st.container(border=True):
        st.markdown("**👤 Browse by GitHub Username**")
        st.markdown("<p style='font-size:.8rem;color:#64748b;margin-top:-.4rem;"
                    "margin-bottom:.6rem;'>Fetch all repos and pick one from a visual grid.</p>",
                    unsafe_allow_html=True)
        u = st.text_input("Username", placeholder="github/owner",
                          label_visibility="collapsed", key="land_user")
        c1, c2 = st.columns([2,1])
        with c1:
            sort0 = st.selectbox("Sort", ["⭐ Stars","🕒 Recently Updated","🍴 Forks"],
                                 label_visibility="collapsed", key="land_sort")
        with c2:
            fetch = st.button("Fetch Repositories →", type="primary", use_container_width=True, key="land_fetch")

        if fetch:
            if not u.strip():
                st.warning("⚠️ Enter a GitHub username.")
            else:
                try:
                    uname = repo.extract_username(u.strip())
                    sort_k = "stars" if "Stars" in sort0 else "updated" if "Updated" in sort0 else "forks"
                    with st.spinner(f"Fetching repos for **{uname}** …"):
                        repos_list = repo.fetch_user_repos(uname, sort=sort_k, limit=50)
                    st.session_state.update({
                        "user_repos": repos_list,
                        "browsed_user": uname,
                        "f_sort": sort0  # Persist sort selection to next page
                    })
                    go("browse")
                except ValueError as e:
                    st.error(f"❌ {e}")

    st.markdown("""
        <div style='display:flex;align-items:center;gap:1rem;margin:1.4rem 0;'>
            <div style='flex:1;height:1.5px;background:linear-gradient(to right,transparent,#cbd5e1);'></div>
            <span style='color:#475569;font-size:1rem;font-weight:700;
                         letter-spacing:.12em;text-transform:uppercase;'>— or —</span>
            <div style='flex:1;height:1.5px;background:linear-gradient(to left,transparent,#cbd5e1);'></div>
        </div>""", unsafe_allow_html=True)

    # ── Direct URL ───────────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown("**🔗 Direct Repository URL**")
        st.markdown("<p style='font-size:.8rem;color:#64748b;margin-top:-.4rem;"
                    "margin-bottom:.6rem;'>Paste a full GitHub repo URL to analyze instantly.</p>",
                    unsafe_allow_html=True)
        url_in = st.text_input("URL", placeholder="github/owner/repo",
                               label_visibility="collapsed", key="land_url")
        if st.button("🚀 Analyze Repository", type="primary", use_container_width=True, key="land_analyze"):
            if not url_in.strip():
                st.warning("⚠️ Paste a GitHub repository URL.")
            else:
                try:
                    owner, rname = repo.extract_repo(url_in.strip())
                    nav_analysis(owner, rname)
                except ValueError as e:
                    st.error(f"❌ {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE: BROWSE
# ═════════════════════════════════════════════════════════════════════════════
def page_browse():
    repos_all = st.session_state.get("user_repos", [])
    user      = st.session_state.get("browsed_user", "")

    # Back button
    if st.button("← Back to Home", key="browse_back"):
        go("landing")

    st.markdown(f"<h2 style='font-weight:700;color:#0f172a;margin-bottom:.1rem;'>"
                f"Select a Repository</h2>"
                f"<p style='color:#64748b;font-size:.85rem;margin-bottom:1.2rem;'>"
                f"@{user} · {len(repos_all)} public repos fetched</p>",
                unsafe_allow_html=True)

    # ── Filter bar ───────────────────────────────────────────────────────
    all_langs = sorted({r.get("language","") for r in repos_all if r.get("language","")})

    with st.container(border=True):
        fc1, fc2, fc3 = st.columns([1, 1, 1], gap="small")
        with fc1:
            sort_by  = st.selectbox("Sort by", ["⭐ Stars","🕒 Recently Updated","🍴 Forks"],
                                    label_visibility="visible", key="f_sort")
        with fc2:
            lang_sel = st.selectbox("Language", ["All"] + all_langs,
                                    label_visibility="visible", key="f_lang")
        with fc3:
            act_sel  = st.selectbox("Activity", ["All","🟢 Active","🟡 Moderate","🔴 Inactive"],
                                    label_visibility="visible", key="f_act")

    filtered = filter_repos(repos_all, sort_by, lang_sel, 0, act_sel)

    if not filtered:
        st.info("No repositories match the current filters.")
        return

    st.markdown(f"<p style='font-size:.82rem;color:#64748b;margin:.6rem 0 .8rem;'>"
                f"Showing <strong>{len(filtered)}</strong> repositories</p>",
                unsafe_allow_html=True)

    # ── Card grid ─────────────────────────────────────────────────────────
    COLS = 3
    for i in range(0, len(filtered), COLS):
        chunk = filtered[i:i+COLS]
        cols  = st.columns(COLS, gap="medium")
        for col, r in zip(cols, chunk):
            with col:
                _, emoji, dot_color, act_label = act_status(r.get("updated_raw",""))
                lang = r.get("language","")
                lang_html = (f'<span class="lang-pill">'
                             f'<span style="background:{LANG_C.get(lang,"#64748b")};'
                             f'width:7px;height:7px;border-radius:50%;display:inline-block;'
                             f'margin-right:3px;vertical-align:middle;"></span>{lang}</span>'
                             if lang else "")
                desc = (r["description"][:85]+"…" if len(r["description"])>85
                        else r["description"] or "No description.")
                st.markdown(
                    f'<div class="rc">'
                    f'<div style="position:absolute;top:.9rem;right:.9rem;'
                    f'font-size:.7rem;color:{dot_color};font-weight:600;">'
                    f'{emoji} {act_label}</div>'
                    f'<div class="rc-name" title="{r["name"]}">{r["name"]}</div>'
                    f'<div class="rc-desc">{desc}</div>'
                    f'<div class="rc-foot">{lang_html}</div>'
                    f'<div class="rc-stats">'
                    f'<span>⭐ {r["stars"]:,}</span>'
                    f'<span>🍴 {r["forks"]:,}</span>'
                    f'<span>🕒 {r["updated"]}</span>'
                    f'</div></div>', unsafe_allow_html=True)
                if st.button("Analyze", key=f"a_{r['full_name']}",
                             type="secondary", use_container_width=True):
                    nav_analysis(r["owner"], r["name"], source="browse")
        st.write("")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE: ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
def page_analysis():
    owner = st.session_state.get("p_owner","")
    rname = st.session_state.get("p_repo","")

    if not owner or not rname:
        st.error("No repository selected.")
        if st.button("← Back"):  go("landing")
        return

    # Back button — always goes to the page that triggered the analysis
    back_dest  = st.session_state.get("analysis_source", "landing")
    back_label = "← Back to Repositories" if back_dest == "browse" else "← Back to Home"
    if st.button(back_label, key="analysis_back"):
        st.session_state["result_data"] = None
        go(back_dest)

    # Run analysis if not cached — show prominent loading screen
    if st.session_state["result_data"] is None:
        loading = st.empty()
        loading.markdown(
            f"""
            <div style='display:flex;flex-direction:column;align-items:center;
                        justify-content:center;padding:5rem 2rem;text-align:center;'>
                <div style='font-size:2.8rem;margin-bottom:1rem;'>⏳</div>
                <h3 style='color:#0f172a;font-weight:700;margin-bottom:.4rem;'>
                    Analyzing Repository</h3>
                <p style='color:#64748b;font-size:.95rem;margin-bottom:1.5rem;'>
                    Fetching data for <strong>{owner}/{rname}</strong> from GitHub API…</p>
                <div style='width:260px;height:4px;background:#e2e8f0;border-radius:4px;overflow:hidden;'>
                    <div style='height:100%;background:#3b82f6;border-radius:4px;
                                animation:slide 1.5s ease-in-out infinite;width:40%;'></div>
                </div>
                <style>@keyframes slide{{0%{{margin-left:-40%}}100%{{margin-left:100%}}}}</style>
                <p style='color:#94a3b8;font-size:.78rem;margin-top:1rem;'>
                    This may take a few seconds…</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        try:
            data = cached_analyze(owner, rname)
            activity_chart = cached_activity(owner, rname)
            data["commit_activity"] = activity_chart
            st.session_state["result_data"] = data
        except ValueError as e:
            loading.empty()
            st.error(f"❌ {e}")
            return
        except Exception as e:
            loading.empty()
            st.error(f"❌ Unexpected error: {e}")
            return
        loading.empty()  # clear loading screen

    data = st.session_state["result_data"]

    # ── Header ────────────────────────────────────────────────────────────
    st.markdown(f"<h2 style='font-weight:700;color:#0f172a;margin-bottom:.1rem;'>"
                f"Repository Analysis</h2>"
                f"<div style='display:flex;align-items:center;gap:.6rem;margin-bottom:.25rem;'>"
                f"<span style='font-size:1.1rem;font-weight:600;color:#0f172a;'>{data['full_name']}</span>"
                f"<span style='font-size:.75rem;background:#f1f5f9;color:#64748b;"
                f"padding:.1rem .5rem;border-radius:20px;'>{data['visibility']}</span></div>"
                f"<p style='font-size:.83rem;color:#64748b;margin-bottom:1.2rem;'>{data['description']}</p>",
                unsafe_allow_html=True)

    left, right = st.columns([1, 2], gap="large")

    # ── Score panel ───────────────────────────────────────────────────────
    with left:
        with st.container(border=True):
            st.markdown('<div class="sec">Overall Score</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div style="display:flex;align-items:baseline;gap:.4rem;margin-bottom:.5rem;">'
                f'<span class="score-big" style="color:{score_color(data["score"])};">'  
                f'{data["score"]}</span>'
                f'<span class="score-denom">/ 100</span>'
                f'{sbadge(data["label"])}</div>', unsafe_allow_html=True)
            st.progress(data["score"] / 100)
            st.markdown(f"<p style='font-size:.78rem;color:#64748b;margin-top:.4rem;'>"
                        f"{data['summary']}</p>", unsafe_allow_html=True)

    # ── Metrics ───────────────────────────────────────────────────────────
    with right:
        with st.container(border=True):
            m1, m2 = st.columns(2, gap="large")
            with m1:
                st.markdown('<div class="sec">Repository Metrics</div>', unsafe_allow_html=True)
                st.markdown(
                    row("⭐ Stars",       f"{data['stars']:,}") +
                    row("🍴 Forks",       f"{data['forks']:,}") +
                    row("🐞 Open Issues", f"{data['issues']:,}") +
                    row("👀 Watchers",    f"{data['watchers']:,}") +
                    row("📄 README",      data["readme"]) +
                    row("⚖️ License",     data["license"]),
                    unsafe_allow_html=True)
            with m2:
                st.markdown('<div class="sec">Code & Activity</div>', unsafe_allow_html=True)
                st.markdown(
                    row("🌿 Branch",      data["branch"]) +
                    row("🕒 Updated",     data["last_updated"]) +
                    row("📆 Created",     data["created_at"]) +
                    row("📁 Files",       f"{data['total_files']:,}") +
                    row("💾 Size",        f"{data['size_kb']:,} KB") +
                    row("📌 Commits",     str(data["commit_count"])),
                    unsafe_allow_html=True)

    # ── Score Breakdown ───────────────────────────────────────────────────
    bd = get_score_breakdown(data)
    with st.container(border=True):
        st.markdown('<div class="sec">Score Breakdown</div>', unsafe_allow_html=True)
        total_max = sum(m for _,_,m,_ in bd)
        for label, pts, max_pts, note in bd:
            pct = (pts / max_pts) * 100 if max_pts else 0
            bar_color = "#16a34a" if pct >= 80 else "#d97706" if pct >= 50 else "#dc2626"
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:.8rem;padding:.45rem 0;'
                f'border-bottom:1px solid #f1f5f9;font-size:.85rem;">'
                f'<span style="min-width:130px;color:#374151;font-weight:500;">{label}</span>'
                f'<div style="flex:1;background:#e2e8f0;border-radius:4px;height:6px;">'
                f'<div style="width:{pct:.0f}%;background:{bar_color};height:6px;border-radius:4px;"></div></div>'
                f'<span style="min-width:160px;color:#64748b;font-size:.78rem;">{note}</span>'
                f'<span style="min-width:50px;text-align:right;font-weight:700;color:{bar_color};">'
                f'+{pts}<span style="color:#94a3b8;font-weight:400;">/{max_pts}</span></span>'
                f'</div>',
                unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:right;font-size:.82rem;color:#64748b;margin-top:.4rem;">'
                    f'Total: <strong style="color:#0f172a;">{data["score"]}</strong> / {total_max}</div>',
                    unsafe_allow_html=True)

    # ── Reasoning Transparency ────────────────────────────────────────────
    reasons_list = get_reasoning(data)
    with st.container(border=True):
        st.markdown('<div class="sec">Analysis Reasoning</div>', unsafe_allow_html=True)
        icon_map  = {"pos":"✅", "neu":"⚠️", "neg":"❌"}
        color_map = {"pos":"#15803d", "neu":"#d97706", "neg":"#dc2626"}
        bg_map    = {"pos":"#f0fdf4", "neu":"#fffbeb", "neg":"#fef2f2"}
        html = ""
        for kind, text in reasons_list:
            html += (f'<div style="display:flex;align-items:flex-start;gap:.55rem;'
                     f'padding:.45rem .7rem;background:{bg_map[kind]};border-radius:7px;'
                     f'margin-bottom:.35rem;font-size:.84rem;color:{color_map[kind]};'
                     f'border-left:3px solid {color_map[kind]};">'
                     f'<span style="flex-shrink:0">{icon_map[kind]}</span>'
                     f'<span>{text}</span></div>')
        st.markdown(html, unsafe_allow_html=True)

    # ── Commit Activity Chart ─────────────────────────────────────────────
    activity = data.get("commit_activity", {})
    if activity:
        with st.container(border=True):
            st.markdown('<div class="sec">Commit Activity (Last 12 Weeks)</div>',
                        unsafe_allow_html=True)
            df = pd.DataFrame({"Commits": list(activity.values())},
                              index=list(activity.keys()))
            st.bar_chart(df, height=180)
    else:
        st.info("📊 Commit activity data not available for this repository.")

    # ── Languages ─────────────────────────────────────────────────────────
    if data.get("languages"):
        with st.container(border=True):
            st.markdown('<div class="sec">Languages</div>', unsafe_allow_html=True)
            st.markdown(lang_bars(data["languages"]), unsafe_allow_html=True)

    # ── Recommendation ────────────────────────────────────────────────────
    status_text, txt_color, bg, border_c, reasons = get_recommendation(data)
    with st.container(border=True):
        st.markdown('<div class="sec">Recommendation</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="rec-box" style="background:{bg};border-color:{border_c};">'
            f'<div style="font-size:1.05rem;font-weight:700;color:{txt_color};">'
            f'{status_text}</div>', unsafe_allow_html=True)
        if reasons:
            st.markdown("<ul style='margin:.5rem 0 0 1rem;font-size:.83rem;color:#374151;'>"+
                        "".join(f"<li>{r}</li>" for r in reasons)+
                        "</ul></div>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='font-size:.83rem;color:#374151;margin:.4rem 0 0;'>"
                        "This repository meets all quality criteria.</p></div>",
                        unsafe_allow_html=True)

    # ── GitHub link + Downloads ───────────────────────────────────────────
    st.markdown(f"<a href='{data['html_url']}' target='_blank' "
                f"style='font-size:.83rem;color:#2563eb;text-decoration:none;'>"
                f"🔗 View on GitHub → {data['html_url']}</a>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:.78rem;color:#94a3b8;text-align:center;"
                "margin:1rem 0 .4rem;'>Export Report</p>", unsafe_allow_html=True)
    safe = data["full_name"].replace("/","_")
    dl1, dl2 = st.columns(2, gap="small")
    with dl1:
        st.download_button("⬇️ Download JSON",
            data=repo.generate_json_report(data).encode("utf-8"),
            file_name=f"{safe}_report.json", mime="application/json",
            use_container_width=True)
    with dl2:
        st.download_button("⬇️ Download PDF",
            data=repo.generate_pdf_report(data),
            file_name=f"{safe}_report.pdf", mime="application/pdf",
            use_container_width=True)

# ── Router ────────────────────────────────────────────────────────────────────
p = st.session_state["page"]
if   p == "landing":  page_landing()
elif p == "browse":   page_browse()
elif p == "analysis": page_analysis()
