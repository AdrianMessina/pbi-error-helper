"""PBI Error Helper — Design System v2: Diagnostic Console.

Aesthetic: industrial diagnostic terminal meets clean corporate.
Dark-on-light with the landing diagnostic area treated as a hero "console".
Typography: Fira Sans 300-800 + Fira Code 400-600.
Palette: YPF Blue #0451E4 / Slate dark sidebar / Light content.
"""

import streamlit as st

CATEGORY_LABELS = {
    "dax": "DAX & Medidas",
    "modelo": "Modelo & Relaciones",
    "powerquery": "Power Query / M",
    "refresh": "Refresh & Gateway",
    "conexion": "Conexión & Red",
}

CATEGORY_ICONS = {
    "dax": "fx",
    "modelo": "⬡",
    "powerquery": "⧉",
    "refresh": "↻",
    "conexion": "⌁",
}


def get_css() -> str:
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Fira+Sans:wght@300;400;500;600;700;800&display=swap');

    :root {
        --blue: #0451E4;
        --blue-hover: #0340B8;
        --blue-deep: #022A8A;
        --blue-glow: rgba(4,81,228,0.14);
        --blue-subtle: rgba(4,81,228,0.05);
        --blue-tint: rgba(4,81,228,0.10);

        --surface-0: #FFFFFF;
        --surface-1: #F8FAFC;
        --surface-2: #F1F5F9;
        --surface-3: #E2E8F0;

        --dark-0: #080E1A;
        --dark-1: #0F172A;
        --dark-2: #1E293B;
        --dark-3: #334155;

        --ink: #0F172A;
        --ink-2: #1E293B;
        --ink-3: #4B5563;
        --ink-4: #6B7280;
        --ink-on-dark: #CBD5E1;
        --ink-white: #F1F5F9;

        --line: #E2E8F0;
        --line-light: #F1F5F9;
        --line-dark: rgba(255,255,255,0.07);

        --sev-alta: #DC2626;
        --sev-alta-bg: rgba(220,38,38,0.08);
        --sev-media: #D97706;
        --sev-media-bg: rgba(217,119,6,0.08);
        --sev-baja: #059669;
        --sev-baja-bg: rgba(5,150,105,0.08);

        --sec-symptom: #D97706;
        --sec-cause: #0451E4;
        --sec-solution: #059669;
        --sec-prevention: #0891B2;
        --sec-sources: #6B7280;

        --r-sm: 6px;
        --r-md: 8px;
        --r-lg: 12px;
        --r-xl: 16px;
        --r-full: 9999px;

        --sh-xs: 0 1px 2px rgba(0,0,0,0.04);
        --sh-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
        --sh-md: 0 4px 12px rgba(0,0,0,0.07);
        --sh-lg: 0 10px 28px rgba(0,0,0,0.10);
        --sh-blue: 0 4px 20px rgba(4,81,228,0.15);
        --sh-hover: 0 8px 24px rgba(4,81,228,0.10), 0 2px 8px rgba(0,0,0,0.06);
        --sh-console: inset 0 2px 8px rgba(0,0,0,0.15), 0 4px 20px rgba(0,0,0,0.12);

        --ease: cubic-bezier(0.25, 0.46, 0.45, 0.94);
        --t-fast: 120ms;
        --t-norm: 200ms;
        --t-slow: 320ms;

        --sans: 'Fira Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        --mono: 'Fira Code', 'Cascadia Code', 'Consolas', monospace;
    }

    /* ============ STREAMLIT CHROME ============ */
    #MainMenu, footer, .stDeployButton { visibility: hidden; }
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
    }
    .stAppViewBlockContainer,
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 1rem !important;
        max-width: 1100px !important;
    }
    .block-container { padding-top: 1rem !important; }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }
    }

    /* ============ TYPOGRAPHY ============ */
    html, body, [class*="css"] {
        font-family: var(--sans) !important;
        color: var(--ink);
        -webkit-font-smoothing: antialiased;
    }
    code, pre, .stCodeBlock, [data-testid="stCode"] {
        font-family: var(--mono) !important;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: var(--sans) !important;
        color: var(--ink);
        letter-spacing: -0.025em;
        line-height: 1.2;
    }

    /* ============ SIDEBAR ============ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--dark-0) 0%, var(--dark-1) 60%, var(--dark-2) 100%);
        border-right: 1px solid var(--line-dark);
    }
    [data-testid="stSidebar"] > div:first-child { padding: 0.5rem 0.25rem; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { color: var(--ink-on-dark); }
    [data-testid="stSidebar"] hr { border-color: var(--line-dark); margin: 0.65rem 0; }

    .sidebar-brand {
        padding: 0.5rem 0.75rem 0.85rem;
        text-align: center;
    }
    .sidebar-brand .brand-line {
        height: 2px;
        background: linear-gradient(90deg, var(--blue) 0%, var(--blue-hover) 60%, transparent 100%);
        margin: 0.75rem auto 0.85rem;
        width: 100%;
    }
    .sidebar-brand .product-name {
        color: #FFF; font-size: 1.05rem; font-weight: 700;
        letter-spacing: -0.02em; margin: 0; font-family: var(--sans);
    }
    .sidebar-brand .product-sub {
        color: var(--ink-on-dark); font-size: 0.62rem; font-weight: 500;
        text-transform: uppercase; letter-spacing: 0.14em;
        margin: 0.25rem 0 0; font-family: var(--mono);
    }

    .sidebar-label {
        color: #94A3B8; font-size: 0.6rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.14em;
        padding: 0.85rem 0.85rem 0.4rem; font-family: var(--mono);
    }

    /* Sidebar radio */
    [data-testid="stSidebar"] .stRadio > label { display: none !important; }
    [data-testid="stSidebar"] .stRadio > div { gap: 1px; }
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"] {
        background: transparent; cursor: pointer !important;
        border-radius: 4px; padding: 0.05rem 0;
        transition: background var(--t-fast) var(--ease);
        position: relative;
    }
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"]:hover {
        background: rgba(4,81,228,0.14);
    }
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stRadio label *,
    [data-testid="stSidebar"] .stRadio p,
    [data-testid="stSidebar"] .stRadio span {
        color: var(--ink-on-dark) !important;
        font-family: var(--sans) !important;
        font-size: 0.86rem !important;
        font-weight: 400 !important;
    }
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"]:hover label,
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"]:hover span {
        color: #FFF !important;
    }
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"][aria-checked="true"] {
        background: rgba(4,81,228,0.20);
    }
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"][aria-checked="true"]::before {
        content: ''; position: absolute;
        left: 0; top: 18%; bottom: 18%;
        width: 2px; background: var(--blue);
        border-radius: 0 2px 2px 0;
    }
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"][aria-checked="true"] label,
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"][aria-checked="true"] span {
        color: #FFF !important; font-weight: 600 !important;
    }

    /* Sidebar footer */
    .sidebar-footer {
        margin-top: 1.25rem; padding: 0.85rem 0.75rem 0.5rem;
        border-top: 1px solid var(--line-dark);
    }
    .sidebar-footer .footer-text {
        color: #64748B; font-size: 0.6rem; text-align: center;
        font-family: var(--mono); letter-spacing: 0.06em; margin: 0 0 0.6rem 0;
    }

    /* ============ DIAGNOSTIC CONSOLE (HERO) ============ */
    .diag-console {
        background: var(--dark-1);
        border-radius: var(--r-xl);
        padding: 3rem 2.5rem 2.5rem;
        margin: 0 0 2.5rem;
        position: relative;
        overflow: hidden;
        box-shadow: var(--sh-console);
    }
    .diag-console::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--blue) 0%, var(--blue-hover) 40%, transparent 80%);
    }
    .diag-console::after {
        content: '';
        position: absolute;
        inset: 0;
        background-image:
            linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
        background-size: 40px 40px;
        pointer-events: none;
    }

    .diag-console .console-eyebrow {
        font-family: var(--mono);
        font-size: 0.65rem;
        font-weight: 600;
        color: var(--blue);
        text-transform: uppercase;
        letter-spacing: 0.18em;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.7rem;
        position: relative;
        z-index: 1;
    }
    .diag-console .console-eyebrow::before {
        content: '';
        width: 24px; height: 1.5px;
        background: var(--blue);
    }

    .diag-console h1 {
        color: var(--ink-white);
        font-size: 2.4rem;
        font-weight: 800;
        line-height: 1.05;
        letter-spacing: -0.035em;
        margin: 0 0 0.5rem;
        position: relative;
        z-index: 1;
    }
    .diag-console h1 .accent { color: var(--blue); }

    .diag-console .console-sub {
        color: var(--ink-on-dark);
        font-size: 0.95rem;
        line-height: 1.55;
        margin: 0 0 2rem;
        max-width: 520px;
        position: relative;
        z-index: 1;
    }

    .diag-console .console-divider {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        margin: 1.75rem 0 1rem;
        color: #475569;
        font-family: var(--mono);
        font-size: 0.68rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        position: relative;
        z-index: 1;
    }
    .diag-console .console-divider::before,
    .diag-console .console-divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: rgba(255,255,255,0.07);
    }

    /* Category pills inside console */
    .console-cats {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        position: relative;
        z-index: 1;
    }
    .console-cat-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        font-family: var(--mono);
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--ink-on-dark);
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        padding: 0.45rem 0.85rem;
        border-radius: var(--r-sm);
        cursor: pointer;
        transition: all var(--t-fast) var(--ease);
    }
    .console-cat-pill:hover {
        background: rgba(4,81,228,0.18);
        border-color: rgba(4,81,228,0.35);
        color: #FFF;
    }
    .console-cat-pill .cat-icon {
        font-size: 0.85rem;
        opacity: 0.65;
    }
    .console-cat-pill .cat-count {
        font-size: 0.6rem;
        color: #64748B;
        margin-left: 0.25rem;
    }

    /* Stats bar */
    .console-stats {
        display: flex;
        gap: 2rem;
        margin-top: 1.5rem;
        padding-top: 1.25rem;
        border-top: 1px solid rgba(255,255,255,0.06);
        position: relative;
        z-index: 1;
    }
    .console-stats .stat-num {
        font-size: 1.35rem;
        font-weight: 700;
        color: #FFF;
        line-height: 1;
        font-family: var(--mono);
    }
    .console-stats .stat-num .blue { color: var(--blue); }
    .console-stats .stat-label {
        font-family: var(--mono);
        font-size: 0.6rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.35rem;
    }

    /* ============ DIAGNOSTIC RESULT ============ */
    .diag-result {
        background: var(--surface-0);
        border: 1px solid var(--line);
        border-radius: var(--r-lg);
        padding: 1.75rem 2rem;
        margin-bottom: 1rem;
        box-shadow: var(--sh-sm);
        position: relative;
        transition: all var(--t-norm) var(--ease);
    }
    .diag-result.top-match {
        border-color: rgba(4,81,228,0.25);
        box-shadow: var(--sh-blue);
    }
    .diag-result.top-match::before {
        content: '';
        position: absolute;
        top: 0; left: 0; bottom: 0;
        width: 3px;
        background: var(--blue);
        border-radius: var(--r-lg) 0 0 var(--r-lg);
    }

    .diag-result .match-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.85rem;
    }
    .diag-result .match-id {
        font-family: var(--mono);
        font-size: 0.72rem;
        font-weight: 700;
        color: var(--blue);
        background: var(--blue-subtle);
        padding: 0.28rem 0.65rem;
        border-radius: var(--r-sm);
        border: 1px solid rgba(4,81,228,0.15);
        letter-spacing: 0.05em;
    }
    .diag-result .match-conf {
        font-family: var(--mono);
        font-size: 0.72rem;
        font-weight: 700;
        color: var(--ink-4);
        margin-left: auto;
    }
    .diag-result .match-conf .pct {
        color: var(--blue);
    }
    .diag-result .match-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: var(--ink);
        margin: 0 0 0.65rem;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    .diag-result .match-snippet {
        font-size: 0.88rem;
        color: var(--ink-3);
        line-height: 1.55;
        margin: 0;
    }
    .diag-result .match-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.35rem;
        margin-top: 0.85rem;
    }

    /* Confidence bar */
    .conf-bar {
        width: 100%;
        height: 3px;
        background: var(--surface-2);
        border-radius: 2px;
        margin: 0.85rem 0 0;
        overflow: hidden;
    }
    .conf-bar .conf-fill {
        height: 100%;
        border-radius: 2px;
        transition: width 0.6s var(--ease);
    }

    /* Alternative matches (smaller) */
    .alt-match {
        display: grid;
        grid-template-columns: auto 1fr auto;
        gap: 0.85rem;
        align-items: center;
        padding: 0.75rem 1rem;
        background: var(--surface-0);
        border: 1px solid var(--line);
        border-radius: var(--r-md);
        cursor: pointer;
        transition: all var(--t-fast) var(--ease);
        margin-bottom: 0.35rem;
    }
    .alt-match:hover {
        border-color: rgba(4,81,228,0.2);
        background: var(--surface-1);
    }
    .alt-match .alt-id {
        font-family: var(--mono);
        font-size: 0.68rem;
        font-weight: 700;
        color: var(--ink-4);
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .alt-match .alt-title {
        font-size: 0.88rem;
        font-weight: 600;
        color: var(--ink);
    }
    .alt-match .alt-conf {
        font-family: var(--mono);
        font-size: 0.72rem;
        font-weight: 600;
        color: var(--ink-4);
    }

    /* ============ SECTION LABEL ============ */
    .section-label {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        margin: 2rem 0 1rem;
    }
    .section-label .marker {
        font-family: var(--mono);
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--blue);
        letter-spacing: 0.12em;
    }
    .section-label .title {
        font-size: 0.92rem; font-weight: 700;
        color: var(--ink); letter-spacing: -0.01em;
    }
    .section-label .rule { flex: 1; height: 1px; background: var(--line); }

    /* ============ CASE SECTIONS (Detail) ============ */
    .case-section {
        position: relative;
        margin: 0 0 1.65rem;
        background: var(--surface-0);
        border: 1px solid var(--line);
        border-radius: var(--r-md);
        overflow: hidden;
        transition: box-shadow var(--t-norm) var(--ease);
    }
    .case-section:hover { box-shadow: var(--sh-sm); }

    .case-section .case-header {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        padding: 0.85rem 1.15rem;
        background: var(--surface-1);
        border-bottom: 1px solid var(--line-light);
    }
    .case-section .case-accent {
        width: 4px; height: 22px;
        border-radius: 2px;
    }
    .case-section[data-kind="symptom"] .case-accent { background: var(--sec-symptom); }
    .case-section[data-kind="cause"] .case-accent { background: var(--sec-cause); }
    .case-section[data-kind="solution"] .case-accent { background: var(--sec-solution); }
    .case-section[data-kind="prevention"] .case-accent { background: var(--sec-prevention); }
    .case-section[data-kind="sources"] .case-accent { background: var(--sec-sources); }

    .case-section .case-number {
        font-family: var(--mono); font-size: 0.68rem;
        font-weight: 700; color: var(--ink-4);
        letter-spacing: 0.1em;
    }
    .case-section .case-title {
        font-size: 0.95rem; font-weight: 700;
        color: var(--ink); margin: 0; letter-spacing: -0.01em;
    }

    .case-section .case-body {
        padding: 1rem 1.25rem 1.15rem;
        font-size: 0.92rem;
        line-height: 1.7;
        color: var(--ink-2);
    }
    .case-section .case-body p { margin: 0 0 0.75rem; }
    .case-section .case-body h3 {
        font-size: 0.98rem; font-weight: 600;
        margin: 1.25rem 0 0.6rem; color: var(--ink);
    }
    .case-section .case-body ul,
    .case-section .case-body ol { margin: 0 0 0.85rem; padding-left: 1.25rem; }
    .case-section .case-body li { margin-bottom: 0.35rem; line-height: 1.6; }
    .case-section .case-body li::marker { color: var(--blue); }
    .case-section .case-body code {
        background: var(--surface-2);
        color: var(--blue-deep);
        padding: 0.08rem 0.35rem;
        border-radius: 4px;
        font-size: 0.84em;
    }
    .case-section .case-body pre {
        background: var(--dark-1);
        color: var(--ink-white);
        padding: 0.85rem 1rem;
        border-radius: var(--r-sm);
        overflow-x: auto;
        font-size: 0.82rem;
        margin: 0.75rem 0 0.95rem;
        border: 1px solid var(--dark-2);
    }
    .case-section .case-body pre code {
        background: transparent; color: inherit; padding: 0;
    }
    .case-section .case-body blockquote {
        border-left: 3px solid var(--blue);
        background: var(--blue-subtle);
        margin: 0.75rem 0;
        padding: 0.65rem 0.95rem;
        color: var(--ink-2);
        font-style: italic;
        border-radius: 0 var(--r-sm) var(--r-sm) 0;
    }
    .case-section .case-body a {
        color: var(--blue);
        text-decoration: none;
        border-bottom: 1px solid rgba(4,81,228,0.25);
        transition: border-color var(--t-fast) var(--ease);
    }
    .case-section .case-body a:hover { border-bottom-color: var(--blue); }

    /* Detail hero */
    .detail-hero {
        padding: 0.5rem 0 2rem;
        border-bottom: 1px solid var(--line);
        margin-bottom: 1.75rem;
    }
    .detail-hero .meta-row {
        display: flex; align-items: center;
        gap: 0.65rem; margin-bottom: 1rem;
    }
    .detail-hero .id-tag {
        font-family: var(--mono); font-size: 0.78rem;
        font-weight: 700; color: var(--blue);
        background: var(--blue-subtle);
        padding: 0.32rem 0.72rem;
        border-radius: var(--r-sm);
        border: 1px solid rgba(4,81,228,0.15);
        letter-spacing: 0.05em;
    }
    .detail-hero h1 {
        font-size: 2rem; font-weight: 700;
        line-height: 1.12; letter-spacing: -0.03em;
        color: var(--ink); margin: 0 0 1rem; max-width: 880px;
    }
    .detail-hero .chip-row {
        display: flex; flex-wrap: wrap; gap: 0.4rem;
    }

    /* Related errors block */
    .related-block {
        margin: 2rem 0 1rem;
        padding: 1.2rem 1.25rem;
        background: var(--surface-1);
        border-radius: var(--r-md);
        border: 1px solid var(--line);
    }
    .related-block .rel-label {
        font-family: var(--mono); font-size: 0.65rem;
        font-weight: 600; color: var(--ink-4);
        text-transform: uppercase; letter-spacing: 0.12em;
        margin-bottom: 0.65rem;
    }
    .related-block .rel-list { display: flex; flex-wrap: wrap; gap: 0.4rem; }
    .related-block .rel-pill {
        font-family: var(--mono); font-size: 0.72rem;
        font-weight: 600; color: var(--blue);
        background: var(--surface-0); border: 1px solid var(--line);
        padding: 0.3rem 0.65rem; border-radius: var(--r-sm);
        cursor: pointer; transition: all var(--t-fast) var(--ease);
    }
    .related-block .rel-pill:hover {
        background: var(--blue-subtle);
        border-color: rgba(4,81,228,0.3);
    }

    /* ============ RESULT LIST (category browse) ============ */
    .result-item {
        background: var(--surface-0);
        border: 1px solid var(--line);
        border-radius: var(--r-md);
        padding: 0.95rem 1.15rem;
        cursor: pointer;
        transition: all var(--t-fast) var(--ease);
        display: grid;
        grid-template-columns: 90px 1fr auto;
        gap: 1rem;
        align-items: center;
        margin-bottom: 0.35rem;
    }
    .result-item:hover {
        border-color: rgba(4,81,228,0.25);
        box-shadow: var(--sh-sm);
        background: var(--surface-1);
    }
    .result-item .r-id {
        font-family: var(--mono); font-size: 0.72rem;
        font-weight: 600; color: var(--ink-4);
        letter-spacing: 0.04em; text-transform: uppercase;
    }
    .result-item .r-title {
        font-size: 0.94rem; font-weight: 600;
        color: var(--ink); margin: 0 0 0.2rem;
        letter-spacing: -0.01em; line-height: 1.3;
    }
    .result-item .r-snippet {
        font-size: 0.82rem; color: var(--ink-3);
        margin: 0; line-height: 1.4;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 1;
        -webkit-box-orient: vertical;
    }

    /* ============ BADGES & CHIPS ============ */
    .badge {
        display: inline-flex; align-items: center;
        gap: 0.35rem; font-family: var(--mono);
        font-size: 0.66rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.08em;
        padding: 0.22rem 0.55rem;
        border-radius: var(--r-full);
        white-space: nowrap;
    }
    .badge-cat { background: var(--surface-2); color: var(--ink-3); border: 1px solid var(--line); }
    .badge-sev { font-weight: 700; }
    .badge-sev::before {
        content: ''; width: 5px; height: 5px;
        border-radius: 50%; background: currentColor;
    }
    .badge-sev-alta { background: var(--sev-alta-bg); color: var(--sev-alta); }
    .badge-sev-media { background: var(--sev-media-bg); color: var(--sev-media); }
    .badge-sev-baja { background: var(--sev-baja-bg); color: var(--sev-baja); }

    .chip {
        display: inline-flex; align-items: center;
        font-family: var(--mono); font-size: 0.68rem;
        font-weight: 500; padding: 0.18rem 0.55rem;
        border-radius: var(--r-sm); background: var(--surface-1);
        color: var(--ink-3); border: 1px solid var(--line);
    }
    .chip-tool {
        background: rgba(4,81,228,0.06);
        color: var(--blue-deep);
        border-color: rgba(4,81,228,0.14);
    }

    /* ============ BREADCRUMB ============ */
    .breadcrumb {
        display: flex; align-items: center; gap: 0.5rem;
        font-family: var(--mono); font-size: 0.72rem;
        color: var(--ink-4); text-transform: uppercase;
        letter-spacing: 0.08em; margin-bottom: 1.25rem;
    }
    .breadcrumb .crumb { color: var(--ink-4); }
    .breadcrumb .crumb.current { color: var(--ink); font-weight: 600; }
    .breadcrumb .sep { color: var(--surface-3); }

    /* ============ EMPTY STATE ============ */
    .empty-state {
        text-align: center;
        padding: 3.5rem 2rem;
        background: var(--surface-1);
        border: 1px dashed var(--line);
        border-radius: var(--r-lg);
        margin: 1rem 0;
    }
    .empty-state .empty-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        opacity: 0.4;
    }
    .empty-state h3 {
        font-size: 1.05rem; font-weight: 600;
        color: var(--ink-2); margin: 0 0 0.4rem;
    }
    .empty-state p {
        font-size: 0.88rem; color: var(--ink-4);
        margin: 0 auto; max-width: 380px; line-height: 1.55;
    }

    /* ============ BUTTONS ============ */
    .stButton > button,
    .stDownloadButton > button {
        background: var(--blue) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--r-sm) !important;
        font-weight: 600 !important;
        font-family: var(--sans) !important;
        font-size: 0.85rem !important;
        padding: 0.5rem 1.15rem !important;
        transition: background var(--t-norm) var(--ease),
                    box-shadow var(--t-norm) var(--ease),
                    transform var(--t-fast) var(--ease) !important;
        cursor: pointer !important;
    }
    .stButton > button:hover {
        background: var(--blue-hover) !important;
        box-shadow: var(--sh-blue) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button:active { transform: translateY(0) !important; }

    /* Sidebar text input */
    [data-testid="stSidebar"] .stTextInput > div > div > input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        color: #FFF !important;
        font-family: var(--sans) !important;
        font-size: 0.88rem !important;
        padding: 0.5rem 0.75rem !important;
        border-radius: var(--r-sm) !important;
    }
    [data-testid="stSidebar"] .stTextInput > div > div > input::placeholder {
        color: #64748B !important;
    }
    [data-testid="stSidebar"] .stTextInput > div > div > input:focus {
        background: rgba(255,255,255,0.08) !important;
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 3px rgba(4,81,228,0.18) !important;
    }

    /* Main textarea */
    .stTextArea textarea {
        font-family: var(--mono) !important;
        font-size: 0.9rem !important;
        background: rgba(255,255,255,0.06) !important;
        color: #FFF !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: var(--r-md) !important;
        padding: 0.85rem !important;
    }
    .stTextArea textarea::placeholder {
        color: #475569 !important;
        font-style: italic;
    }
    .stTextArea textarea:focus {
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 3px rgba(4,81,228,0.2) !important;
    }
    .stTextArea label { color: var(--ink-on-dark) !important; }

    /* ============ FOOTER ============ */
    .app-footer {
        margin-top: 3rem;
        padding: 1rem 0 0.5rem;
        border-top: 1px solid var(--line);
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: var(--mono);
        font-size: 0.68rem;
        color: var(--ink-4);
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* ============ SCROLLBAR ============ */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--surface-3); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--ink-4); }

    .stAlert {
        border-radius: var(--r-md) !important;
        font-family: var(--sans) !important;
        font-size: 0.87rem !important;
    }

    /* ============ ANIMATIONS ============ */
    @keyframes fade-up {
        from { opacity: 0; transform: translateY(18px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @supports (animation-timeline: view()) {
        .diag-result, .alt-match, .case-section, .result-item {
            animation: fade-up linear both;
            animation-timeline: view();
            animation-range: entry 0% entry 30%;
        }
    }
    @media (prefers-reduced-motion: reduce) {
        .diag-result, .alt-match, .case-section, .result-item {
            animation: none !important;
        }
    }
    </style>
    """


def inject() -> None:
    st.markdown(get_css(), unsafe_allow_html=True)


def severity_badge(severity: str) -> str:
    s = severity.lower()
    label = {"alta": "Alta", "media": "Media", "baja": "Baja"}.get(s, s.title())
    return f'<span class="badge badge-sev badge-sev-{s}">{label}</span>'


def category_badge(category: str) -> str:
    label = CATEGORY_LABELS.get(category, category.title())
    return f'<span class="badge badge-cat">{label}</span>'


def conf_color(score: float) -> str:
    if score >= 0.7:
        return "var(--blue)"
    if score >= 0.4:
        return "var(--sev-media)"
    return "var(--ink-4)"
