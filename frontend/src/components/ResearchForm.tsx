import { useState } from 'react';
import type { ResearchRequest } from '../types';

interface ResearchFormProps {
  onSubmit: (request: ResearchRequest) => void;
  isLoading: boolean;
}

export function ResearchForm({ onSubmit, isLoading }: ResearchFormProps) {
  const [formData, setFormData] = useState<ResearchRequest>({
    nganh_hang: 'Mỹ phẩm thuần chay',
    thi_truong_muc_tieu: 'Việt Nam',
    phan_khuc_quan_tam: [],
    doi_thu_seed: [],
    khung_thoi_gian: '12 thang gan nhat',
    muc_tieu_nghien_cuu: [],
  });

  const [segments, setSegments] = useState<string>('Gen Z, Người mua trên sàn TMĐT');
  const [competitors, setCompetitors] = useState<string>('Cocoon, The Body Shop, Innisfree');
  const [objectives, setObjectives] = useState<string>('Độ lớn thị trường, Đối thủ và định vị, Xu hướng hành vi mua hàng');

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.nganh_hang.trim()) {
      alert('Vui lòng nhập ngành hàng');
      return;
    }

    const request: ResearchRequest = {
      ...formData,
      phan_khuc_quan_tam: segments
        .split(',')
        .map((s) => s.trim())
        .filter((s) => s),
      doi_thu_seed: competitors
        .split(',')
        .map((c) => c.trim())
        .filter((c) => c),
      muc_tieu_nghien_cuu: objectives
        .split(',')
        .map((o) => o.trim())
        .filter((o) => o),
    };

    onSubmit(request);
  };

  return (
    <div className="research-form">
      <h2>Nghiên Cứu Thị Trường</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="nganh_hang">Ngành Hàng *</label>
          <input
            type="text"
            id="nganh_hang"
            name="nganh_hang"
            value={formData.nganh_hang}
            onChange={handleInputChange}
            placeholder="VD: Mỹ phẩm thuần chay"
            disabled={isLoading}
            required
          />
          <small>Tên ngành hàng, lĩnh vực kinh doanh</small>
        </div>

        <div className="form-group">
          <label htmlFor="thi_truong_muc_tieu">Thị Trường Mục Tiêu *</label>
          <input
            type="text"
            id="thi_truong_muc_tieu"
            name="thi_truong_muc_tieu"
            value={formData.thi_truong_muc_tieu}
            onChange={handleInputChange}
            placeholder="VD: Việt Nam"
            disabled={isLoading}
            required
          />
          <small>Phạm vi thị trường</small>
        </div>

        <div className="form-group">
          <label htmlFor="phan_khuc_quan_tam">Phân Khúc Quan Tâm</label>
          <textarea
            id="phan_khuc_quan_tam"
            value={segments}
            onChange={(e) => setSegments(e.target.value)}
            placeholder="VD: Gen Z, Người mua trên sàn TMĐT&#10;(Nhập cách nhau bằng dấu phẩy)"
            disabled={isLoading}
            rows={3}
          />
          <small>Các tệp khách hàng hướng tới (cách nhau bằng dấu phẩy)</small>
        </div>

        <div className="form-group">
          <label htmlFor="doi_thu_seed">Đối Thủ Cạnh Tranh</label>
          <textarea
            id="doi_thu_seed"
            value={competitors}
            onChange={(e) => setCompetitors(e.target.value)}
            placeholder="VD: Cocoon, The Body Shop, Innisfree&#10;(Nhập cách nhau bằng dấu phẩy)"
            disabled={isLoading}
            rows={3}
          />
          <small>Các đối thủ để tham chiếu (cách nhau bằng dấu phẩy)</small>
        </div>

        <div className="form-group">
          <label htmlFor="khung_thoi_gian">Khung Thời Gian</label>
          <select
            id="khung_thoi_gian"
            name="khung_thoi_gian"
            value={formData.khung_thoi_gian}
            onChange={handleInputChange}
            disabled={isLoading}
          >
            <option value="12 thang gan nhat">12 tháng gần nhất</option>
            <option value="2024-2026">2024-2026</option>
            <option value="2024">2024</option>
            <option value="2025-2026">2025-2026</option>
          </select>
          <small>Mốc thời gian để tìm kiếm dữ liệu</small>
        </div>

        <div className="form-group">
          <label htmlFor="muc_tieu_nghien_cuu">Mục Tiêu Nghiên Cứu</label>
          <textarea
            id="muc_tieu_nghien_cuu"
            value={objectives}
            onChange={(e) => setObjectives(e.target.value)}
            placeholder="VD: Độ lớn thị trường, Đối thủ và định vị, Xu hướng hành vi mua hàng&#10;(Nhập cách nhau bằng dấu phẩy)"
            disabled={isLoading}
            rows={3}
          />
          <small>Các mục tiêu cụ thể để xoáy sâu (cách nhau bằng dấu phẩy)</small>
        </div>

        <button type="submit" disabled={isLoading} className="submit-btn">
          {isLoading ? 'Đang xử lý...' : 'Bắt Đầu Nghiên Cứu'}
        </button>
      </form>
    </div>
  );
}
