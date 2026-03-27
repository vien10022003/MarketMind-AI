# Huong dan trien khai de tai Marketing Assistant (GenAI + Agentic AI)

Tai lieu nay tong hop de xuat da trao doi, giup ban doi chieu va thuc hien theo tung buoc.

## 1) Muc tieu de tai
Xay dung he thong tro ly marketing co kha nang:
- Nghien cuu va phan tich thi truong
- Xay dung chien luoc marketing
- Tao noi dung quang cao va truyen thong

## 2) Mapping notebook theo 3 giai doan

### Giai doan A: Nghien cuu va phan tich thi truong
Notebook nen dung:
- 04_planning.ipynb: Lap ke hoach nghien cuu theo buoc ro rang
- 03_ReAct.ipynb: Vong lap suy nghi + hanh dong khi thu thap thong tin
- 02_tool_use.ipynb: Goi cong cu/API de lay du lieu thuc te

Nang cao (tuy chon):
- 13_ensemble.ipynb: Tong hop da goc nhin (doi thu, xu huong, khach hang)
- 12_graph.ipynb: Bieu dien tri thuc thi truong theo do thi quan he
- 08_episodic_with_semantic.ipynb: Luu bo nho dai han cho insight va su kien

Dau ra mong doi:
- Bao cao thi truong tong quan
- Phan tich doi thu canh tranh
- Xu huong nganh
- Phan khuc va insight khach hang

### Giai doan B: Xay dung chien luoc Marketing
Notebook nen dung:
- 04_planning.ipynb: Tao khung ke hoach chien luoc
- 05_multi_agent.ipynb: Chia vai tro chuyen gia (STP, dinh vi, pricing, channel)
- 11_meta_controller.ipynb: Dieu phoi den dung agent theo bai toan

Tang do tin cay (nen co):
- 06_PEV.ipynb: Plan -> Execute -> Verify de kiem tra va sua loi chien luoc

Dau ra mong doi:
- Tai lieu chien luoc marketing tong the
- Muc tieu, thong diep gia tri, kenh truyen thong, ngan sach so bo
- Roadmap trien khai theo giai doan

### Giai doan C: Tao noi dung quang cao va truyen thong
Notebook nen dung:
- 01_reflection.ipynb: Tu phan bien va nang cap chat luong ban nhap
- 15_RLHF.ipynb: Vong bien tap theo feedback de toi uu noi dung
- 05_multi_agent.ipynb: Chia doi tao copy/script/creative theo kenh

Luu y quan trong:
- Repo nay manh ve kien truc agent va quy trinh text.
- Neu can tao video/poster thuc te, can tich hop them image/video generation API theo mau tool-calling cua 02_tool_use.ipynb.

Dau ra mong doi:
- Bai viet quang cao
- Script video ngan
- Copy cho poster/banner
- Bo thong diep theo tung kenh (Facebook, TikTok, Email, Landing page)

## 3) Combo trien khai de xuat (thuc chien)
Thu tu khuyen nghi:
1. Nghien cuu: 04 -> 03 -> 02
2. Chien luoc: 11 -> 05 -> 06
3. Noi dung: 01 -> 15 -> 05
4. Bo nho dai han: 08 hoac 12

Giai thich nhanh:
- 08 (episodic + semantic): phu hop neu uu tien bo nho hoi thoai + su kien
- 12 (graph): phu hop neu uu tien quan he thuc the va suy luan da buoc

## 4) Lo trinh thuc hien goi y

### Buoc 1: Dung pipeline nghien cuu
- Dung 04_planning de tao danh sach cau hoi nghien cuu
- Dung 03_ReAct + 02_tool_use de thu thap bang chung
- Tong hop thanh bao cao co nguon va ket luan

### Buoc 2: Dung pipeline chien luoc
- Tao team agent trong 05_multi_agent (market analyst, strategist, channel planner)
- Dung 11_meta_controller de route task
- Dung 06_PEV de verify tung phan cua chien luoc

### Buoc 3: Dung pipeline san xuat noi dung
- Dung 05_multi_agent de tao ban nhap da dinh dang
- Dung 01_reflection va 15_RLHF de nang cap chat luong
- Chuan hoa format output theo kenh truyen thong

### Buoc 4: Mo rong media (neu can)
- Tich hop tool tao anh/video ben ngoai thong qua co che tool use
- Them lop kiem duyet (approval gate) truoc khi xuat ban

## 5) Tieu chi danh gia de tai (goi y)
- Do dung va cap nhat cua thong tin thi truong
- Do nhat quan va kha thi cua chien luoc
- Chat luong noi dung tao ra (do ro, do hap dan, do dung target)
- Toc do tao dau ra va kha nang lap lai quy trinh
- Muc do giam cong suc thu cong cho nguoi lam marketing

## 6) Checklist toi thieu de bat dau
- Cai dat moi truong va API key theo README
- Chay lan luot cac notebook: 04, 03, 02, 11, 05, 06, 01, 15
- Chot format input/output cho tung node agent
- Tao bo mau prompt cho 3 nhom tac vu: research, strategy, content
- Dinh nghia bo metric danh gia ngay tu dau

---
Tai lieu nay la baseline implementation guide. Khi ban chot duoc nganh hang cu the (vi du: my pham, F&B, giao duc), co the bo sung bo prompt va KPI rieng cho domain do.