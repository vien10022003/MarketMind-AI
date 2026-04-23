"""
Synthesis Module
Generate final report sections using LLM
"""

import pandas as pd
from rich import print as rprint

from .data_models import StageAInput, StageAOutput, EvidenceItem
from .llm_config import LocalTextGenerator


def dataframe_to_compact_context(df: pd.DataFrame, top_n: int = 25) -> str:
    """Convert DataFrame to compact context string"""
    rows = []
    for idx, row in df.head(top_n).iterrows():
        rows.append(
            f"[{idx+1}] title={row['title']} | url={row['url']} | "
            f"score={row['source_score']:.2f} | snippet={row['snippet'][:300]}"
        )
    return "\n".join(rows)


def synthesize_tong_quan_thi_truong(
    llm: LocalTextGenerator,
    research_input: StageAInput,
    df: pd.DataFrame
) -> str:
    """Generate market overview section"""
    evidence_context = dataframe_to_compact_context(df, top_n=20)
    
    prompt = f"""
Ban la senior market analyst chuyen gia chi tiet.
Nhiem vu: Tao TONG QUAN THI TRUONG chi tiet va tong hop.

Input:
- Nganh hang: {research_input.nganh_hang}
- Thi truong: {research_input.thi_truong_muc_tieu}
- Khung thoi gian: {research_input.khung_thoi_gian}

Yeu cau:
1. Toc do tang truong, quy mo thi truong
2. Vai tro cac nguoi chien thang
3. Luc dua day thi truong
4. Tien do va xu huong
5. Dan chung URL trong [url]

Evidence:
{evidence_context}

Chi tra ve phan tich chi tiet, khong JSON, khong mo dau/ket luan.
"""
    raw = llm.generate(prompt, max_new_tokens=800)
    return raw.strip() if raw else "Khong du du lieu."


def synthesize_phan_tich_doi_thu(
    llm: LocalTextGenerator,
    research_input: StageAInput,
    df: pd.DataFrame
) -> str:
    """Generate competitor analysis section"""
    evidence_context = dataframe_to_compact_context(df, top_n=20)
    
    prompt = f"""
Ban la chuyen gia phan tich canh tranh.
Nhiem vu: Phan tich cac DOI THU chinh va chien luoc.

Input:
- Nganh hang: {research_input.nganh_hang}
- Thi truong: {research_input.thi_truong_muc_tieu}
- Doi thu seed: {research_input.doi_thu_seed}

Yeu cau:
1. Cac doi thu chinh tren thi truong
2. Vi tri san pham va diem can trong
3. Uu diem va han che
4. Chien luoc gia ca, phan phoi, truyen thong
5. Diem yeu co the khai thac
6. Dan chung URL [url]

Evidence:
{evidence_context}

Chi tra ve phan tich chi tiet, khong JSON, khong mo dau/ket luan.
"""
    raw = llm.generate(prompt, max_new_tokens=800)
    return raw.strip() if raw else "Khong du du lieu."


def synthesize_xu_huong_nganh(
    llm: LocalTextGenerator,
    research_input: StageAInput,
    df: pd.DataFrame
) -> str:
    """Generate industry trends section"""
    evidence_context = dataframe_to_compact_context(df, top_n=20)
    
    prompt = f"""
Ban la chuyen gia xu huong nganh hang.
Nhiem vu: Xuat hien cac XU HUONG chinh dang dinh hinh nganh hang.

Input:
- Nganh hang: {research_input.nganh_hang}
- Thi truong: {research_input.thi_truong_muc_tieu}
- Khung thoi gian: {research_input.khung_thoi_gian}

Yeu cau:
1. Xu huong cong nghe (AI, tu dong hoa, blockchain, IoT)
2. Xu huong tieu dung
3. Quy dinh va chinh sach anh huong
4. Xuan phat trong sach ngoai
5. Cau truc thi truong dang thay doi
6. Dan chung URL [url]

Evidence:
{evidence_context}

Chi tra ve phan tich chi tiet, khong JSON, khong mo dau/ket luan.
"""
    raw = llm.generate(prompt, max_new_tokens=800)
    return raw.strip() if raw else "Khong du du lieu."


def synthesize_phan_khuc_va_insight(
    llm: LocalTextGenerator,
    research_input: StageAInput,
    df: pd.DataFrame
) -> str:
    """Generate customer segment and insights section"""
    evidence_context = dataframe_to_compact_context(df, top_n=20)
    
    prompt = f"""
Ban la chuyen gia hang vi khach hang va hanh vi pham.
Nhiem vu: Tao PHAN KHUC KHACH HANG va INSIGHT HANH VI.

Input:
- Nganh hang: {research_input.nganh_hang}
- Thi truong: {research_input.thi_truong_muc_tieu}
- Phan khuc quan tam: {research_input.phan_khuc_quan_tam}

Yeu cau:
1. Phan khuc chinh va dac diem
2. Chi tieu tieu dung va hanh vi mua
3. Pain point chinh
4. Uu tien va quyet dinh mua
5. Kenh tiem can va phuong thuc giao tieu
6. Dan chung URL [url]

Evidence:
{evidence_context}

Chi tra ve phan tich chi tiet, khong JSON, khong mo dau/ket luan.
"""
    raw = llm.generate(prompt, max_new_tokens=800)
    return raw.strip() if raw else "Khong du du lieu."


def synthesize_stage_a_report(
    llm: LocalTextGenerator,
    research_input: StageAInput,
    df: pd.DataFrame
) -> StageAOutput:
    """Generate complete Stage A report"""
    rprint("[yellow]Synthesizing report sections...[/yellow]")
    
    # Generate each section
    tong_quan = synthesize_tong_quan_thi_truong(llm, research_input, df)
    phan_tich_doi_thu = synthesize_phan_tich_doi_thu(llm, research_input, df)
    xu_huong = synthesize_xu_huong_nganh(llm, research_input, df)
    phan_khuc_insight = synthesize_phan_khuc_va_insight(llm, research_input, df)

    # Create citations
    citations = []
    for _, row in df.head(20).iterrows():
        citations.append(
            EvidenceItem(
                title=row["title"],
                url=row["url"],
                snippet=row["snippet"],
                published_date=row.get("published_date"),
                source_score=float(row["source_score"]),
            )
        )

    rprint("[green]✅ Report synthesis completed[/green]")
    
    return StageAOutput(
        tong_quan_thi_truong=tong_quan,
        phan_tich_doi_thu=phan_tich_doi_thu,
        xu_huong_nganh=xu_huong,
        phan_khuc_va_insight_khach_hang=phan_khuc_insight,
        citations=citations,
    )
