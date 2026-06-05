"""PBI Error Helper v2 — Diagnostic Console.

The entry point is a "paste your error" diagnostic interface.
Category browsing and detail views are secondary navigation.
"""

from __future__ import annotations

from pathlib import Path

import markdown as md_lib
import streamlit as st

import kb
import styles

ASSETS = Path(__file__).parent / "assets"
LOGO_YPF = ASSETS / "logo_ypf.png"
LOGO_DAIA = ASSETS / "logo_daia.png"

SECTION_KIND = {
    "Síntoma": ("symptom", "01"),
    "Causa": ("cause", "02"),
    "Solución paso a paso": ("solution", "03"),
    "Cómo prevenirlo": ("prevention", "04"),
    "Fuentes": ("sources", "05"),
}


st.set_page_config(
    page_title="PBI Error Helper · YPF",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

styles.inject()


# ============ STATE ============

def _init() -> None:
    st.session_state.setdefault("view", "home")
    st.session_state.setdefault("selected_id", None)
    st.session_state.setdefault("selected_category", None)


def goto(view: str, *, error_id: str | None = None, category: str | None = None) -> None:
    st.session_state.view = view
    st.session_state.selected_id = error_id
    st.session_state.selected_category = category


# ============ DATA ============

@st.cache_resource
def get_kb():
    entries = kb.load_entries()
    index = kb.build_index(entries)
    return entries, index


# ============ SIDEBAR ============

def render_sidebar(entries: list[kb.ErrorEntry]) -> None:
    with st.sidebar:
        if LOGO_YPF.exists():
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                st.image(str(LOGO_YPF), width=80)

        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="brand-line"></div>
                <p class="product-name">PBI Error Helper</p>
                <p class="product-sub">Diagnostic Console · DA&IA</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-label">Navegación</div>', unsafe_allow_html=True)

        counts = kb.category_counts(entries)
        cats = sorted(counts.keys())
        options = ["__diag__"] + cats
        labels = {"__diag__": "  ⌁  Diagnosticar"}
        for c in cats:
            lbl = styles.CATEGORY_LABELS.get(c, c.title())
            icon = styles.CATEGORY_ICONS.get(c, "·")
            labels[c] = f"  {icon}  {lbl}  ·  {counts[c]}"

        current = "__diag__"
        if st.session_state.view == "category" and st.session_state.selected_category:
            current = st.session_state.selected_category
        elif st.session_state.view == "detail" and st.session_state.selected_category:
            current = st.session_state.selected_category

        pick = st.radio(
            "nav",
            options,
            format_func=lambda x: labels[x],
            index=options.index(current) if current in options else 0,
            label_visibility="collapsed",
            key="nav_radio",
        )
        if pick == "__diag__" and st.session_state.view not in ("home", "diagnose", "detail"):
            goto("home")
        elif pick != "__diag__" and st.session_state.view != "detail":
            if st.session_state.selected_category != pick:
                goto("category", category=pick)

        st.markdown(
            """
            <div class="sidebar-footer">
                <p class="footer-text">YPF · Gerencia Visualización · DA&IA</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if LOGO_DAIA.exists():
            c1, c2, c3 = st.columns([1, 3, 1])
            with c2:
                st.image(str(LOGO_DAIA), width="stretch")


# ============ COMPONENTS ============

def breadcrumb(parts: list[tuple[str, str | None]]) -> None:
    html = ['<div class="breadcrumb">']
    for i, (label, _) in enumerate(parts):
        is_last = i == len(parts) - 1
        cls = "crumb current" if is_last else "crumb"
        html.append(f'<span class="{cls}">{label}</span>')
        if not is_last:
            html.append('<span class="sep">/</span>')
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def section_label(marker: str, title: str) -> None:
    st.markdown(
        f"""
        <div class="section-label">
            <span class="marker">{marker}</span>
            <span class="title">{title}</span>
            <span class="rule"></span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result_list(items: list[kb.ErrorEntry], *, key_prefix: str = "res") -> None:
    if not items:
        return
    for e in items:
        st.markdown(
            f"""
            <div class="result-item">
                <span class="r-id">{e.id.upper()}</span>
                <div>
                    <p class="r-title">{e.title}</p>
                    <p class="r-snippet">{e.snippet or ''}</p>
                </div>
                <div style="display:flex; gap:0.35rem;">
                    {styles.category_badge(e.category)}
                    {styles.severity_badge(e.severity)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    cols = st.columns(min(len(items), 6))
    for i, e in enumerate(items):
        with cols[i % len(cols)]:
            if st.button(e.id.upper(), key=f"{key_prefix}_{e.id}", use_container_width=True, type="secondary"):
                goto("detail", error_id=e.id, category=e.category)
                st.rerun()


# ============ HOME / DIAGNOSTIC CONSOLE ============

def view_home(entries: list[kb.ErrorEntry]) -> None:
    counts = kb.category_counts(entries)
    n_high = sum(1 for e in entries if e.severity.lower() == "alta")

    # --- Console header (dark block) ---
    st.markdown(
        f"""
        <div class="diag-console">
            <div class="console-eyebrow">Diagnostic Console · v0.2</div>
            <h1>Pegá tu error.<br/><span class="accent">Nosotros lo resolvemos.</span></h1>
            <p class="console-sub">
                Copiá el mensaje de error de Power BI y pegalo acá abajo.
                El motor de diagnóstico lo matchea contra {len(entries)} casos documentados.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Textarea for pasting error (inside the dark console aesthetic) ---
    error_text = st.text_area(
        "Pegá el error aquí",
        placeholder="Ej: A circular dependency was detected: Table[Column1]...\n\nTambién podés describir el problema con tus palabras.",
        height=120,
        key="diag_input",
        label_visibility="collapsed",
    )

    col1, col2, _ = st.columns([1, 1, 3])
    with col1:
        diagnose_clicked = st.button("⌁  Diagnosticar", type="primary", use_container_width=True)
    with col2:
        if st.button("Limpiar", type="secondary", use_container_width=True):
            st.session_state.diag_input = ""
            st.rerun()

    # --- Diagnostic results ---
    if diagnose_clicked and error_text.strip():
        matches = kb.diagnose(entries, error_text, limit=5)
        if matches:
            st.markdown("", unsafe_allow_html=True)
            section_label("MATCH", f"{len(matches)} resultado{'s' if len(matches) > 1 else ''}")

            # Top match
            top = matches[0]
            color = styles.conf_color(top.score)
            kw_html = " · ".join(f"<code>{k}</code>" for k in top.matched_keywords[:6])

            st.markdown(
                f"""
                <div class="diag-result top-match">
                    <div class="match-header">
                        <span class="match-id">{top.entry.id.upper()}</span>
                        {styles.severity_badge(top.entry.severity)}
                        {styles.category_badge(top.entry.category)}
                        <span class="match-conf"><span class="pct">{top.confidence_pct}%</span> match</span>
                    </div>
                    <h2 class="match-title">{top.entry.title}</h2>
                    <p class="match-snippet">{top.entry.snippet}</p>
                    <div class="match-tags">{kw_html}</div>
                    <div class="conf-bar">
                        <div class="conf-fill" style="width:{top.confidence_pct}%; background:{color};"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                f"Ver solución completa  →  {top.entry.id.upper()}",
                key=f"goto_top_{top.entry.id}",
                type="primary",
                use_container_width=True,
            ):
                goto("detail", error_id=top.entry.id, category=top.entry.category)
                st.rerun()

            # Alternative matches
            alts = matches[1:]
            if alts:
                section_label("ALT", "Otros posibles matches")
                for m in alts:
                    st.markdown(
                        f"""
                        <div class="alt-match">
                            <span class="alt-id">{m.entry.id.upper()}</span>
                            <span class="alt-title">{m.entry.title}</span>
                            <span class="alt-conf">{m.confidence_pct}%</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                cols = st.columns(min(len(alts), 4))
                for i, m in enumerate(alts):
                    with cols[i % len(cols)]:
                        if st.button(
                            m.entry.id.upper(),
                            key=f"goto_alt_{m.entry.id}",
                            use_container_width=True,
                            type="secondary",
                        ):
                            goto("detail", error_id=m.entry.id, category=m.entry.category)
                            st.rerun()
        else:
            st.markdown(
                """
                <div class="empty-state">
                    <div class="empty-icon">⌁</div>
                    <h3>Sin coincidencias</h3>
                    <p>No encontramos un match para ese texto.
                    Probá con el mensaje de error exacto de Power BI,
                    o explorá por categoría en el panel izquierdo.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # --- Category pills + stats (below console) ---
    st.markdown("<br>", unsafe_allow_html=True)

    cats = sorted(counts.keys())
    pills_html = "".join(
        f'<span class="console-cat-pill">'
        f'<span class="cat-icon">{styles.CATEGORY_ICONS.get(c, "·")}</span>'
        f'{styles.CATEGORY_LABELS.get(c, c.title())}'
        f'<span class="cat-count">{counts[c]}</span>'
        f'</span>'
        for c in cats
    )
    st.markdown(
        f"""
        <div style="margin-bottom: 0.85rem;">
            <div class="section-label">
                <span class="marker">EXPLORAR</span>
                <span class="title">Por categoría</span>
                <span class="rule"></span>
            </div>
            <div class="console-cats">{pills_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(len(cats))
    for i, c in enumerate(cats):
        with cols[i]:
            lbl = styles.CATEGORY_LABELS.get(c, c.title())
            if st.button(lbl, key=f"cat_btn_{c}", use_container_width=True, type="secondary"):
                goto("category", category=c)
                st.rerun()


# ============ CATEGORY VIEW ============

def view_category(entries: list[kb.ErrorEntry]) -> None:
    cat = st.session_state.selected_category
    label = styles.CATEGORY_LABELS.get(cat, cat.title() if cat else "")
    icon = styles.CATEGORY_ICONS.get(cat, "·")
    items = kb.by_category(entries, cat) if cat else []

    breadcrumb([("Diagnosticar", "home"), (label, None)])

    st.markdown(
        f"""
        <div style="padding: 0.25rem 0 1.5rem; border-bottom: 1px solid var(--line); margin-bottom: 1.5rem;">
            <p style="font-family: var(--mono); font-size: 0.68rem; font-weight: 600;
               color: var(--blue); text-transform: uppercase; letter-spacing: 0.14em;
               margin: 0 0 0.5rem;">
                <span style="margin-right: 0.45rem;">{icon}</span> Categoría
            </p>
            <h1 style="font-size: 2rem; font-weight: 700; margin: 0 0 0.4rem; letter-spacing: -0.03em;">
                {label}
            </h1>
            <p style="font-size: 0.92rem; color: var(--ink-3); margin: 0;">
                {len(items)} {'caso' if len(items)==1 else 'casos'} documentados.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if items:
        render_result_list(items, key_prefix=f"cat_{cat}")
    else:
        st.markdown(
            f"""
            <div class="empty-state">
                <div class="empty-icon">{icon}</div>
                <h3>Sin casos en {label}</h3>
                <p>Cuando un error se repita en el equipo, documentalo acá para que el próximo lo resuelva en segundos.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Volver al diagnóstico", key="back_from_cat", type="secondary"):
        goto("home")
        st.rerun()


# ============ DETAIL VIEW ============

def view_detail(entries: list[kb.ErrorEntry]) -> None:
    entry = kb.by_id(entries, st.session_state.selected_id)
    if entry is None:
        st.warning("Error no encontrado.")
        return

    cat_label = styles.CATEGORY_LABELS.get(entry.category, entry.category.title())
    breadcrumb([("Diagnosticar", "home"), (cat_label, None), (entry.id.upper(), None)])

    # Hero
    chips = "".join(f'<span class="chip chip-tool">{t}</span>' for t in entry.tools)
    chips += "".join(f'<span class="chip">{t}</span>' for t in entry.tags)

    st.markdown(
        f"""
        <div class="detail-hero">
            <div class="meta-row">
                <span class="id-tag">{entry.id.upper()}</span>
                {styles.severity_badge(entry.severity)}
                {styles.category_badge(entry.category)}
            </div>
            <h1>{entry.title}</h1>
            <div class="chip-row">{chips}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sections as cards
    sections = entry.sections
    for sec_name, (kind, number) in SECTION_KIND.items():
        if sec_name not in sections or not sections[sec_name].strip():
            continue
        body_html = md_lib.markdown(
            sections[sec_name],
            extensions=["fenced_code", "tables", "nl2br"],
        )
        st.markdown(
            f"""
            <div class="case-section" data-kind="{kind}">
                <div class="case-header">
                    <span class="case-accent"></span>
                    <span class="case-number">{number}</span>
                    <span class="case-title">{sec_name}</span>
                </div>
                <div class="case-body">{body_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Images & videos
    shown_imgs = [p for p in entry.image_paths if p.exists()]
    shown_vids = [p for p in entry.video_paths if p.exists()]
    if shown_imgs or shown_vids:
        section_label("06", "Material complementario")
        for img in shown_imgs:
            st.image(str(img), caption=img.name, use_container_width=True)
        for vid in shown_vids:
            st.video(str(vid))

    # Related errors
    if entry.related:
        related_pills = "".join(
            f'<span class="rel-pill">{rid.upper()}</span>' for rid in entry.related
        )
        st.markdown(
            f"""
            <div class="related-block">
                <div class="rel-label">Errores relacionados</div>
                <div class="rel-list">{related_pills}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        cols = st.columns(min(len(entry.related), 6))
        for i, rid in enumerate(entry.related):
            rel_entry = kb.by_id(entries, rid)
            if rel_entry is None:
                continue
            with cols[i % len(cols)]:
                if st.button(
                    f"Ir a {rid.upper()}",
                    key=f"rel_{entry.id}_{rid}",
                    use_container_width=True,
                    type="secondary",
                ):
                    goto("detail", error_id=rid, category=rel_entry.category)
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Volver al diagnóstico", key="back_from_detail", type="secondary"):
        goto("home")
        st.rerun()


# ============ MAIN ============

def main() -> None:
    _init()
    entries, index = get_kb()
    render_sidebar(entries)

    view = st.session_state.view
    if view == "category" and st.session_state.selected_category:
        view_category(entries)
    elif view == "detail" and st.session_state.selected_id:
        view_detail(entries)
    else:
        view_home(entries)

    st.markdown(
        f"""
        <div class="app-footer">
            <span>PBI Error Helper · v0.2</span>
            <span>{len(entries):02d} casos · DA&IA</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
