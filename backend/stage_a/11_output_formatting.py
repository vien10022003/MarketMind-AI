"""
Output Formatting Module
Convert results to various formats (Markdown, JSON, etc.)
"""

import pandas as pd
from typing import Any, Dict, List

from .04_data_models import StageAInput, StageAOutput


def build_markdown_report(input_obj: StageAInput, output_obj: StageAOutput) -> str:
    """Build a complete Markdown report"""
    lines = [
        f"# Báo Cáo Giai Đoạn A - {input_obj.nganh_hang} ({input_obj.thi_truong_muc_tieu})",
        "",
        f"**Thời gian**: {input_obj.khung_thoi_gian}",
        "",
        "## 1. Tổng Quan Thị Trường",
        output_obj.tong_quan_thi_truong,
        "",
        "## 2. Phân Tích Đối Thủ",
        output_obj.phan_tich_doi_thu,
        "",
        "## 3. Xu Hướng Ngành",
        output_obj.xu_huong_nganh,
        "",
        "## 4. Phân Khúc & Insight Khách Hàng",
        output_obj.phan_khuc_va_insight_khach_hang,
        "",
        "## Tài Liệu Tham Khảo",
    ]

    for idx, c in enumerate(output_obj.citations, start=1):
        lines.append(f"{idx}. **{c.title}** - [{c.url}]({c.url})")
        lines.append(f"   - Score: {c.source_score:.2f}")
        if c.published_date:
            lines.append(f"   - Date: {c.published_date}")
        lines.append("")

    return "\n".join(lines)


def convert_evidence_to_dict(evidence_df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Convert pandas DataFrame to list of dicts for JSON"""
    return evidence_df.to_dict(orient='records')


def build_json_report(
    input_obj: StageAInput,
    output_obj: StageAOutput,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Build a complete JSON report"""
    return {
        "input": input_obj.model_dump(),
        "report": output_obj.model_dump(),
        "metadata": metadata or {},
    }
