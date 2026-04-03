import type { ResearchReport } from '../types';

interface ResearchReportProps {
  report: ResearchReport | undefined;
  mongodbId?: string;
}

export function ResearchReportComponent({ report, mongodbId }: ResearchReportProps) {
  if (!report) {
    return <div className="report-empty">Chưa có báo cáo</div>;
  }

  return (
    <div className="research-report">
      <h2>Báo Cáo Nghiên Cứu Thị Trường</h2>

      {mongodbId && (
        <div className="report-metadata">
          <p>
            <strong>ID Báo Cáo:</strong> {mongodbId}
          </p>
        </div>
      )}

      <section className="report-section">
        <h3>📊 Tổng Quan Thị Trường</h3>
        <div className="report-content">{report.tong_quan_thi_truong}</div>
      </section>

      <section className="report-section">
        <h3>🎯 Phân Tích Đối Thủ</h3>
        <div className="report-content">{report.phan_tich_doi_thu}</div>
      </section>

      <section className="report-section">
        <h3>📈 Xu Hướng Ngành</h3>
        <div className="report-content">{report.xu_huong_nganh}</div>
      </section>

      <section className="report-section">
        <h3>👥 Phân Khúc & Insight Khách Hàng</h3>
        <div className="report-content">{report.phan_khuc_va_insight_khach_hang}</div>
      </section>

      {report.citations && report.citations.length > 0 && (
        <section className="report-section">
          <h3>📚 Nguồn Tham Khảo</h3>
          <div className="citations-list">
            {report.citations.map((citation, index) => (
              <div key={index} className="citation-item">
                <h4>
                  <a href={citation.url} target="_blank" rel="noopener noreferrer">
                    {citation.title}
                  </a>
                </h4>
                <p className="citation-snippet">{citation.snippet}</p>
                <div className="citation-meta">
                  {citation.published_date && <span className="citation-date">📅 {citation.published_date}</span>}
                  <span className="citation-score">⭐ {(citation.source_score * 100).toFixed(0)}%</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
