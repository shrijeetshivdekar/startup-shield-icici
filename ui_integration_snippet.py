"""
ui_integration_snippet.py — UI section to add to startup_risk_app.py
=====================================================================
This file shows the EXACT code block to insert into startup_risk_app.py
to render the "Competitive Intelligence" section after the existing
"Your Insurance Plan" section.

Insertion point in startup_risk_app.py:
    Right BEFORE the line `with st.expander("Founder's explainer ...`
    (around line 2059 in the current file)

Two changes needed:

(A) Add this import at the top of startup_risk_app.py (around line 31,
    in the same import block that imports from risk_engine):

        from competitor_catalog_expanded import recommend_competitor_products

(B) Paste the entire SECTION TO ADD block below into startup_risk_app.py
    at the insertion point described above.
"""

# =============================================================================
# SECTION TO ADD — paste this into startup_risk_app.py at the insertion point
# =============================================================================

UI_SECTION_CODE = '''
# ── Competitive Intelligence — products NOT in ICICI Lombard's catalog ──
st.markdown("---")
st.markdown(
    '<div class="section-heading">Competitive Intelligence</div>'
    '<div class="section-sub">Insurance products offered by Digit, Tata AIG, '
    'Bajaj Allianz and global insurers (Munich Re, Vouch, Kita, AIG) that '
    'fill specific gaps in ICICI Lombard\\'s current catalog — ranked by your '
    'risk profile.</div>',
    unsafe_allow_html=True,
)

competitor_recs = recommend_competitor_products(
    scores, sector, team_size, funding_stage, _inp, top_n=5, min_score=45.0,
)

# Top 5 ICICI Lombard products from the existing recommendations array,
# excluding mandatory-baseline append-ons (those are not part of the rank).
il_top5 = [r for r in recommendations if not r.get("mandatory", False)][:5]
il_top5_names = [r["name"] for r in il_top5]

if not competitor_recs:
    st.info(
        "No competitor products score above the relevance threshold for this "
        "profile — the existing ICICI Lombard catalog covers this startup's "
        "primary exposures."
    )
else:
    # Side-by-side context: ICICI top 5 and Competitor top 5
    ctx_l, ctx_r = st.columns(2)
    with ctx_l:
        st.markdown(
            '<div style="background:#FEF2F2;border-left:3px solid #AD1E23;'
            'border-radius:8px;padding:0.75rem 1rem;">'
            '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;'
            'text-transform:uppercase;color:#AD1E23;margin-bottom:0.4rem;">'
            'Your top 5 — ICICI Lombard</div>'
            + "".join(
                f'<div style="font-size:0.84rem;color:#0F172A;margin:0.3rem 0;">'
                f'<strong>{i+1}.</strong> {r["name"]} '
                f'<span style="color:#94A3B8;">— {r["score"]:.0f}/100</span>'
                f'</div>'
                for i, r in enumerate(il_top5)
            )
            + '</div>',
            unsafe_allow_html=True,
        )
    with ctx_r:
        st.markdown(
            '<div style="background:#F0F9FF;border-left:3px solid #0EA5E9;'
            'border-radius:8px;padding:0.75rem 1rem;">'
            '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;'
            'text-transform:uppercase;color:#0369A1;margin-bottom:0.4rem;">'
            'Top 5 competitor / global products NOT offered by IL</div>'
            + "".join(
                f'<div style="font-size:0.84rem;color:#0F172A;margin:0.3rem 0;">'
                f'<strong>{i+1}.</strong> {r["name"]} '
                f'<span style="color:#94A3B8;">— {r["score"]:.0f}/100</span>'
                f'</div>'
                for i, r in enumerate(competitor_recs)
            )
            + '</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Detailed competitor cards — each shows what IL is missing and why
    for c in competitor_recs:
        priority = c["priority"]
        if priority == "Critical Gap":
            badge_bg, badge_color, border_color = "#FEE2E2", "#991B1B", "#EF4444"
        elif priority == "Strategic Gap":
            badge_bg, badge_color, border_color = "#FEF3C7", "#92400E", "#F59E0B"
        else:
            badge_bg, badge_color, border_color = "#E0F2FE", "#075985", "#0EA5E9"

        st.markdown(
            f"""
            <div style="background:#FFFFFF;border:1px solid {border_color}33;
                        border-left:4px solid {border_color};border-radius:12px;
                        padding:1.1rem 1.3rem;margin-bottom:0.9rem;
                        box-shadow:0 1px 3px rgba(15,23,42,0.04);">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;
                          gap:0.75rem;margin-bottom:0.5rem;">
                <div>
                  <h4 style="font-size:1rem;font-weight:700;color:#0F172A;margin:0 0 0.2rem 0;">
                    {c["name"]}
                  </h4>
                  <div style="font-size:0.74rem;color:#64748B;font-weight:500;">
                    {c["providers"]}
                  </div>
                </div>
                <div style="display:flex;gap:0.4rem;align-items:center;flex-shrink:0;">
                  <span style="background:{badge_bg};color:{badge_color};
                               font-size:0.65rem;font-weight:700;padding:3px 10px;
                               border-radius:20px;letter-spacing:0.05em;
                               text-transform:uppercase;">{priority}</span>
                  <span style="background:#F1F5F9;color:#0F172A;font-size:0.78rem;
                               font-weight:700;padding:3px 9px;border-radius:8px;">
                    {c["score"]:.0f}/100
                  </span>
                </div>
              </div>

              <div style="font-size:0.78rem;color:#94A3B8;margin-bottom:0.55rem;">
                <strong style="color:#475569;">India availability:</strong> {c["india_status"]}
              </div>

              <div style="font-size:0.86rem;color:#0F172A;line-height:1.6;
                          margin-bottom:0.7rem;">
                <strong>What it covers:</strong> {c["what_it_covers"]}
              </div>

              <div style="background:#FEF2F2;border-left:3px solid #AD1E23;
                          border-radius:6px;padding:0.6rem 0.85rem;margin-bottom:0.5rem;">
                <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.06em;
                            text-transform:uppercase;color:#AD1E23;margin-bottom:0.25rem;">
                  Closest ICICI Lombard product
                </div>
                <div style="font-size:0.84rem;color:#0F172A;">{c["icici_equivalent"]}</div>
              </div>

              <div style="background:#F0FDF4;border-left:3px solid #16A34A;
                          border-radius:6px;padding:0.6rem 0.85rem;margin-bottom:0.5rem;">
                <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.06em;
                            text-transform:uppercase;color:#15803D;margin-bottom:0.25rem;">
                  Why the competitor product is better here
                </div>
                <div style="font-size:0.84rem;color:#0F172A;line-height:1.55;">
                  {c["icici_gap"]}
                </div>
              </div>

              <div style="font-size:0.76rem;color:#94A3B8;">
                <strong>Best for:</strong> {c["best_for"]}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Roll-up insight: how many gaps are critical / strategic
    n_critical = sum(1 for c in competitor_recs if c["priority"] == "Critical Gap")
    n_strategic = sum(1 for c in competitor_recs if c["priority"] == "Strategic Gap")
    n_tactical = sum(1 for c in competitor_recs if c["priority"] == "Tactical Gap")

    summary_color = "#AD1E23" if n_critical >= 3 else (
        "#D97706" if n_critical >= 1 else "#0369A1"
    )
    if n_critical >= 3:
        summary_msg = (
            f"<strong>{n_critical} critical coverage gaps</strong> in ICICI Lombard\\'s "
            f"current catalog for this profile. Recommend escalating these to the "
            f"product team — competitors already have filed product responses."
        )
    elif n_critical >= 1:
        summary_msg = (
            f"<strong>{n_critical} critical and {n_strategic} strategic gaps</strong> — "
            f"the IL catalog covers the foundation but competitors offer affirmative "
            f"products in emerging-risk areas where this startup will likely face "
            f"procurement asks within 12-18 months."
        )
    else:
        summary_msg = (
            f"Only {n_strategic} strategic and {n_tactical} tactical gaps. The "
            f"existing IL catalog covers this startup\\'s primary exposures well; "
            f"the competitive offerings are nice-to-haves, not deal-blockers."
        )

    st.markdown(
        f'<div class="verdict-card" style="margin-top:0.5rem;'
        f'border-left:4px solid {summary_color};">'
        f'<span style="font-size:1.1rem;flex-shrink:0;color:{summary_color};">⚠</span>'
        f'<span>{summary_msg}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
'''

if __name__ == "__main__":
    print("This is a documentation file; copy UI_SECTION_CODE into startup_risk_app.py.")
    print("See module docstring for exact insertion point and import line.")
