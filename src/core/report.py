"""Compact PDF report generation for analysis results (REPORT-01).

The report is intentionally minimal: run parameters, a short statistics block,
the first rows of the result table, a Van Krevelen diagram and the distribution
histograms. Everything else is omitted to keep the document informative and
compact.
"""

from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image as PILImage

from src.core.batch import compute_sample_summary
from src.core.statistics import create_histograms_plot
from src.core.van_krevelen import create_van_krevelen_plot

#: Human-readable labels for the run parameters shown in the report.
_PARAM_LABELS = {
    "sign": "Режим ионизации",
    "rel_error": "Допуск масс, ppm",
    "ppm_tol": "Допуск серий, ppm",
    "load_mass_min": "m/z min",
    "load_mass_max": "m/z max",
    "noise_force": "Шум (force)",
    "noise_intensity": "Шум (intensity)",
    "noise_quantile": "Шум (quantile)",
    "max_groups": "Макс. групп",
    "allow_gaps": "Пропуски в сериях",
    "isotope_filter": "Изотопный фильтр",
}

#: Columns of the result table reproduced in the report.
_RESULT_COLUMNS = [
    ("mass", "m/z"),
    ("brutto", "Формула"),
    ("N_COOH", "N_COOH"),
    ("N_OH", "N_OH"),
]

_MAX_ROWS = 50
_PAGE_W = 17.0  # cm, usable width on A4 with 2 cm margins


def _register_fonts() -> None:
    """Register DejaVuSans (bundled with matplotlib) so Cyrillic renders."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    fonts_dir = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    registered = set(pdfmetrics.getRegisteredFontNames())
    for name, fname in (
        ("DejaVu", "DejaVuSans.ttf"),
        ("DejaVu-Bold", "DejaVuSans-Bold.ttf"),
    ):
        if name not in registered:
            path = fonts_dir / fname
            if path.exists():
                pdfmetrics.registerFont(TTFont(name, str(path)))


def _figure_png(fig, width_cm: float):
    """Render a matplotlib figure to a ReportLab ``Image`` flowable."""
    from reportlab.platypus import Image

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    with PILImage.open(buf) as im:
        w, h = im.size
    buf.seek(0)
    return Image(buf, width=width_cm, height=width_cm * h / w)


def _params_table(params: dict | None):
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle

    rows = []
    for key, label in _PARAM_LABELS.items():
        if params and key in params and params[key] is not None:
            val = params[key]
            if isinstance(val, bool):
                val = "да" if val else "нет"
            rows.append([label, str(val)])
    if not rows:
        return None
    t = Table(rows, colWidths=[6.0, 11.0])
    t.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
                ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return t


def _stats_table(table, stats):
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle

    summary = compute_sample_summary(table, "sample", stats)
    rows = [
        ["Назначено формул", summary.get("n_compounds", 0)],
        ["Σ N_COOH", summary.get("N_COOH_total", 0)],
        ["Σ N_OH", summary.get("N_OH_total", 0)],
        ["Средняя масса (m/z)", _fmt(summary.get("avg_mass"))],
    ]
    if "assigned_count" in summary:
        rows.append(["Назначено пиков", summary["assigned_count"]])
    if "assigned_ratio" in summary:
        rows.append(["Доля назначенных", f"{summary['assigned_ratio']:.1%}"])
    t = Table(rows, colWidths=[6.0, 11.0])
    t.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
                ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return t


def _fmt(value):
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _results_table(table):
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle

    if table is None or table.empty:
        return None
    header = [label for _, label in _RESULT_COLUMNS]
    data = [header]
    for _, row in table.head(_MAX_ROWS).iterrows():
        data.append(
            [
                f"{float(row['mass']):.4f}" if "mass" in table.columns else "—",
                str(row.get("brutto", "—")),
                str(row.get("N_COOH", "—")),
                str(row.get("N_OH", "—")),
            ]
        )
    t = Table(data, colWidths=[4.0, 5.0, 4.0, 4.0], repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    return t


def generate_pdf_report(
    output_path: str | Path,
    sample_name: str,
    table: pd.DataFrame,
    stats=None,
    params: dict | None = None,
    version: str | None = None,
) -> str:
    """Generate a compact PDF report and return the resolved output path."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph

    _register_fonts()

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title=f"NOM HRMS FGA — {sample_name}",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontName="DejaVu-Bold",
        fontSize=16,
        spaceAfter=4,
    )
    sub_style = ParagraphStyle(
        "Sub", parent=styles["Normal"], fontName="DejaVu", fontSize=11, spaceAfter=2
    )
    meta_style = ParagraphStyle(
        "Meta",
        parent=styles["Normal"],
        fontName="DejaVu",
        fontSize=9,
        textColor=colors.grey,
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontName="DejaVu-Bold",
        fontSize=13,
        spaceBefore=14,
        spaceAfter=6,
    )

    story = [
        Paragraph("NOM HRMS FGA — отчёт анализа", title_style),
        Paragraph(f"Образец: {sample_name}", sub_style),
        Paragraph(
            f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')} • "
            f"Версия ПО: {version or '—'}",
            meta_style,
        ),
    ]

    story.append(Paragraph("Параметры анализа", heading_style))
    story.append(_params_table(params) or Paragraph("—", sub_style))

    story.append(Paragraph("Сводная статистика", heading_style))
    story.append(_stats_table(table, stats))

    story.append(Paragraph(f"Результаты (первые {_MAX_ROWS})", heading_style))
    story.append(_results_table(table) or Paragraph("—", sub_style))

    story.append(Paragraph("Диаграмма Ван-Кревелена", heading_style))
    try:
        story.append(_figure_png(create_van_krevelen_plot(table), _PAGE_W))
    except Exception:
        story.append(Paragraph("—", sub_style))

    story.append(Paragraph("Гистограммы распределений", heading_style))
    try:
        story.append(_figure_png(create_histograms_plot(table), _PAGE_W))
    except Exception:
        story.append(Paragraph("—", sub_style))

    doc.build(story)
    return str(Path(output_path).resolve())
