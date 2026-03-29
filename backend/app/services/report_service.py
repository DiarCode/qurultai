from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

import bleach
import markdown
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer

from app.core.config import get_settings
from app.core.utils import ensure_directory
from app.services import s3_service

REPORT_CSS = """
:root {
  --report-ink: #0f172a;
  --report-muted: #475569;
  --report-soft: #64748b;
  --report-border: rgba(148, 163, 184, 0.18);
  --report-panel: rgba(255, 255, 255, 0.96);
  --report-accent: #0f766e;
  --report-accent-soft: rgba(15, 118, 110, 0.1);
}
body {
  margin: 0;
  background:
    radial-gradient(circle at top left, rgba(14, 165, 233, 0.08), transparent 24%),
    radial-gradient(circle at top right, rgba(15, 118, 110, 0.1), transparent 28%),
    linear-gradient(180deg, #f8fafc 0%, #edf3f8 100%);
  color: var(--report-ink);
  font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
}
.report-shell {
  max-width: 1120px;
  margin: 0 auto;
  padding: 56px 24px 72px;
}
.report-card {
  background: var(--report-panel);
  border: 1px solid var(--report-border);
  border-radius: 30px;
  box-shadow: 0 24px 90px rgba(15, 23, 42, 0.08);
  overflow: hidden;
}
.report-header {
  padding: 42px 44px 34px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.96) 42%, rgba(236, 253, 245, 0.8) 100%);
  border-bottom: 1px solid var(--report-border);
}
.report-kicker {
  margin: 0 0 12px;
  color: var(--report-muted);
  font-size: 12px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}
.report-subtitle {
  margin: 14px 0 0;
  max-width: 64rem;
  color: var(--report-muted);
  font-size: 16px;
  line-height: 1.75;
}
.report-meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-top: 24px;
}
.report-meta-card {
  border: 1px solid var(--report-border);
  border-radius: 18px;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.8);
}
.report-meta-card strong {
  display: block;
  font-size: 22px;
  line-height: 1.1;
  color: var(--report-ink);
}
.report-meta-card span {
  display: block;
  margin-top: 6px;
  color: var(--report-soft);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.report-content {
  padding: 26px 44px 48px;
}
.report-markdown {
  line-height: 1.82;
  font-size: 16px;
}
h1, h2, h3 {
  color: var(--report-ink);
  font-weight: 600;
  letter-spacing: -0.03em;
}
h1 { font-size: 38px; margin: 0; }
h2 {
  margin: 30px 0 12px;
  padding-top: 14px;
  border-top: 1px solid var(--report-border);
  font-size: 24px;
}
h3 { font-size: 18px; margin: 18px 0 8px; }
p, li { color: #334155; }
ul, ol {
  margin: 14px 0;
  padding-left: 1.4rem;
}
li + li {
  margin-top: 0.45rem;
}
hr {
  border: 0;
  border-top: 1px solid var(--report-border);
  margin: 24px 0;
}
code {
  background: rgba(15, 23, 42, 0.06);
  border-radius: 8px;
  padding: 2px 6px;
}
pre {
  overflow-x: auto;
  padding: 16px 18px;
  border-radius: 18px;
  background: #0f172a;
  color: #e2e8f0;
}
pre code {
  background: transparent;
  padding: 0;
  color: inherit;
}
blockquote {
  margin: 18px 0;
  padding: 16px 18px;
  border-left: 4px solid var(--report-accent);
  background: var(--report-accent-soft);
  border-radius: 0 18px 18px 0;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin: 18px 0;
}
th, td {
  border: 1px solid rgba(148, 163, 184, 0.2);
  padding: 10px 12px;
  text-align: left;
  vertical-align: top;
}
th {
  background: rgba(15, 23, 42, 0.04);
  color: var(--report-ink);
}
.report-footer {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 0 44px 28px;
  color: var(--report-soft);
  font-size: 12px;
}
@media print {
  body {
    background: white;
  }
  .report-shell {
    max-width: none;
    padding: 0;
  }
  .report-card {
    box-shadow: none;
    border-radius: 0;
    border: 0;
  }
}
"""

MARKDOWN_EXTENSIONS = ["extra", "sane_lists", "tables", "fenced_code", "nl2br"]
BLEACH_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
    "p",
    "pre",
    "code",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "br",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "blockquote",
    "ol",
    "ul",
    "li",
]
BLEACH_ATTRIBUTES = {
    "a": ["href", "title", "target", "rel"],
    "th": ["colspan", "rowspan"],
    "td": ["colspan", "rowspan"],
}


def artifact_paths(run_id: str) -> tuple[Path, Path]:
    settings = get_settings()
    reports_dir = ensure_directory(settings.reports_dir_path)
    return Path(reports_dir) / f"room_{run_id}.html", Path(reports_dir) / f"room_{run_id}.pdf"


def report_object_keys(run_id: str) -> tuple[str, str, str]:
    settings = get_settings()
    base = f"{settings.S3_REPORTS_PREFIX}/{run_id}"
    return f"{base}/report.md", f"{base}/report.html", f"{base}/report.pdf"


def render_markdown_html(markdown_text: str) -> str:
    raw_html = markdown.markdown(
        markdown_text,
        extensions=MARKDOWN_EXTENSIONS,
        output_format="html5",
    )
    cleaned = bleach.clean(
        raw_html,
        tags=BLEACH_TAGS,
        attributes=BLEACH_ATTRIBUTES,
        strip=True,
    )
    return bleach.linkify(cleaned)


def render_report_html(
    report_md: str,
    *,
    title: str,
    subtitle: str | None = None,
    stats: list[tuple[str, str]] | None = None,
) -> str:
    body_html = render_markdown_html(report_md)
    subtitle_html = (
        f'<p class="report-subtitle">{escape(subtitle)}</p>'
        if subtitle and subtitle.strip()
        else ""
    )
    stats_html = ""
    if stats:
        stats_html = (
            '<section class="report-meta-grid">'
            + "".join(
                f'<div class="report-meta-card"><strong>{escape(value)}</strong><span>{escape(label)}</span></div>'
                for label, value in stats
            )
            + "</section>"
        )
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{escape(title)}</title>
    <style>{REPORT_CSS}</style>
  </head>
  <body>
    <main class="report-shell">
      <section class="report-card">
        <header class="report-header">
          <p class="report-kicker">Qurultai Professional Report</p>
          <h1>{escape(title)}</h1>
          {subtitle_html}
          {stats_html}
        </header>
        <section class="report-content report-markdown">
          {body_html}
        </section>
        <footer class="report-footer">
          <span>Prepared by Qurultai</span>
          <span>Grounded with available chat evidence and selected institutional analysis</span>
        </footer>
      </section>
    </main>
  </body>
</html>
"""


def _pdf_styles() -> dict[str, ParagraphStyle]:
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=30,
            textColor=colors.HexColor("#0f172a"),
            alignment=TA_LEFT,
            spaceAfter=12,
        ),
        "heading": ParagraphStyle(
            "ReportHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=22,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=10,
            spaceAfter=8,
        ),
        "subheading": ParagraphStyle(
            "ReportSubHeading",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=18,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=8,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "ReportBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=16,
            textColor=colors.HexColor("#334155"),
            spaceAfter=6,
        ),
        "callout": ParagraphStyle(
            "ReportCallout",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=16,
            textColor=colors.HexColor("#0f766e"),
            backColor=colors.HexColor("#e6fffb"),
            borderPadding=10,
            borderColor=colors.HexColor("#99f6e4"),
            borderWidth=1,
            borderRadius=8,
            spaceBefore=6,
            spaceAfter=8,
        ),
    }


def _flush_list(story: list, bullets: list[str], body_style: ParagraphStyle) -> None:
    if not bullets:
        return
    story.append(
        ListFlowable(
            [ListItem(Paragraph(escape(item), body_style), leftIndent=0) for item in bullets],
            bulletType="bullet",
            leftIndent=16,
            bulletFontName="Helvetica",
            bulletFontSize=10,
        )
    )
    story.append(Spacer(1, 4))
    bullets.clear()


def build_pdf_report(report_md: str, output_path: Path, *, title: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title=title,
        author="Qurultai",
    )

    styles = _pdf_styles()
    story: list = [Paragraph(escape(title), styles["title"]), Spacer(1, 6)]
    bullets: list[str] = []

    for raw_line in report_md.splitlines():
        line = raw_line.strip()
        if not line:
            _flush_list(story, bullets, styles["body"])
            story.append(Spacer(1, 4))
            continue

        if line.startswith("# "):
            _flush_list(story, bullets, styles["body"])
            if len(story) <= 2:
                continue
            story.append(Paragraph(escape(line[2:].strip()), styles["heading"]))
            continue

        if line.startswith("## "):
            _flush_list(story, bullets, styles["body"])
            story.append(Paragraph(escape(line[3:].strip()), styles["heading"]))
            continue

        if line.startswith("### "):
            _flush_list(story, bullets, styles["body"])
            story.append(Paragraph(escape(line[4:].strip()), styles["subheading"]))
            continue

        if line.startswith("> "):
            _flush_list(story, bullets, styles["body"])
            story.append(Paragraph(escape(line[2:].strip()), styles["callout"]))
            continue

        if line.startswith("- "):
            bullets.append(line[2:].strip())
            continue

        if len(line) > 3 and line[0].isdigit() and ". " in line[:4]:
            bullets.append(line.split(". ", 1)[1].strip())
            continue

        _flush_list(story, bullets, styles["body"])
        story.append(Paragraph(escape(line), styles["body"]))

    _flush_list(story, bullets, styles["body"])
    doc.build(story)


def write_report_artifacts(
    run_id: str,
    report_md: str,
    *,
    title: str,
    subtitle: str | None = None,
    stats: list[tuple[str, str]] | None = None,
) -> tuple[str, str | None]:
    html_path, pdf_path = artifact_paths(run_id)
    md_key, html_key, pdf_key = report_object_keys(run_id)

    html_content = render_report_html(report_md, title=title, subtitle=subtitle, stats=stats)
    html_path.write_text(html_content, encoding="utf-8")

    try:
        s3_service.upload_text(md_key, report_md, content_type="text/markdown")
        s3_service.upload_text(html_key, html_content, content_type="text/html")
    except Exception:
        pass

    pdf_written: str | None = None
    try:
        build_pdf_report(report_md, pdf_path, title=title)
        pdf_bytes = pdf_path.read_bytes()
        try:
            s3_service.upload_bytes(pdf_key, pdf_bytes, content_type="application/pdf")
            pdf_written = s3_service.s3_uri(pdf_key)
        except Exception:
            pdf_written = str(pdf_path)
    except Exception:
        pdf_written = None

    try:
        return s3_service.s3_uri(html_key), pdf_written
    except Exception:
        return str(html_path), pdf_written
