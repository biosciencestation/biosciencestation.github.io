# Cập nhật nội dung website BioScience Station

Toàn bộ nội dung website nằm trong thư mục `content/`, dưới dạng file
Markdown (`.md`). **Sửa các file này = website tự cập nhật.** Không cần điều chỉnh HTML.

> Lưu ý: mở website qua một web server (vd chạy `python3 -m http.server`
> trong thư mục dự án rồi vào http://localhost:8000), không mở trực tiếp
> bằng file://, vì trang cần đọc các file trong `content/`.

## Quy tắc chung

- Mỗi file chứa nhiều "mục" (bài viết / thành viên / paper…), ngăn cách nhau
  bằng một dòng chỉ có ba dấu gạch: `---`
- Mỗi mục gồm các dòng `khóa: giá trị` (metadata), rồi **một dòng trống**,
  rồi phần nội dung (body) viết tự do theo đoạn văn.
- Thêm mục mới: copy một mục cũ, dán xuống dưới (nhớ có dòng `---` ngăn cách),
  rồi sửa nội dung.
- Muốn xóa: xóa cả khối mục đó (và dòng `---` thừa).

## Ảnh

- Bỏ ảnh vào thư mục `images/` (tạo nếu chưa có), rồi điền đường dẫn vào dòng
  `image:` — ví dụ `image: images/minh-anh.jpg`.
- Để trống `image:` thì ô ảnh sẽ hiện khung placeholder.
- Với Gallery, dòng `images:` nhận nhiều ảnh, ngăn nhau bằng dấu `|`:
  `images: images/g1.jpg | images/g2.jpg | images/g3.jpg | images/g4.jpg`

## Các file

| File | Nội dung |
|------|----------|
| `site.md` | Tên lab, email, LinkedIn, trang cá nhân (`pi_profile`), địa chỉ, thông tin PI, tiêu đề trang chủ |
| `news/` | Các bài News — **mỗi bài một file riêng** (xem mục dưới) |
| `research.md` | 3 hướng nghiên cứu |
| `team.md` | Thành viên hiện tại (Our Team) |
| `alumni.md` | Cựu thành viên + dòng "hiện đang ở đâu" |
| `publications.md` | Danh sách publications |
| `gallery.md` | Các mục ảnh Gallery |

## News — mỗi bài một file

Các bài News nằm trong thư mục `content/news/`, **mỗi bài là một file `.md` riêng**.

### Thêm một bài mới

Chỉ một việc: **tạo file mới trong `content/news/`**, tên file bắt đầu bằng ngày
dạng `YYYYMMDD` (năm-tháng-ngày) — ví dụ `20260803-hoi-thao-mua-he.md`. Rồi
push. Hết.

**Xoá bài:** xoá file đó đi. **Đổi thứ tự:** đổi ngày ở đầu tên file.

**Thứ tự hiển thị** tự sắp theo ngày trong tên file, **bài mới nhất lên đầu**.
Ví dụ `20260803-…` đứng trước `20250202-…`. Dòng `date:` bên trong file chỉ để
*hiển thị*, không ảnh hưởng thứ tự.

> **`content/news/index.txt` là file tự động sinh ra — đừng sửa tay.**
>
> GitHub Pages chỉ phục vụ file tĩnh, trình duyệt không thể "liệt kê" file
> trong một thư mục, nên trang cần một danh sách để biết phải tải gì.
> `.github/workflows/news-index.yml` tự sinh lại danh sách này mỗi lần push.
>
> Khi xem thử ở máy (`python -m http.server`), trang còn tự dò thẳng thư mục
> nên bài mới hiện ngay, không cần đợi push.

### Nội dung một file bài viết

```
title: Tiêu đề bài viết ở đây
date: August 2026
category: Milestone
image: uploads/news/anh-banner.jpg
images:
captions:
layout: single
summary: Một dòng tóm tắt hiện ở thẻ tin ngoài trang News.

Đoạn nội dung đầu tiên.

![](uploads/news/anh-1.jpg)

Đoạn nội dung thứ hai, viết sau ảnh.

![Chú thích của ảnh này](uploads/news/anh-2.jpg)

Đoạn cuối.
```

Lưu ý: **không** cần dòng `---` nữa (mỗi file chỉ chứa một bài).

| Khóa | Ý nghĩa |
|------|---------|
| `date:` | Ngày hiện trên trang (viết tự do). Việc **sắp xếp** dùng ngày trong *tên file*, không dùng dòng này. |
| `image:` | Ảnh bìa, hiện **nguyên khổ** ở đầu bài (không bị cắt). Để trống thì hiện khung placeholder. |
| `summary:` | Dòng tóm tắt ngoài danh sách News. |
| `images:` / `layout:` | Bộ ảnh xếp ở *cuối* bài (xem mục dưới). Không bắt buộc. |

### Chèn ảnh xen giữa các đoạn văn

Viết ảnh trên **một dòng riêng**, theo cú pháp markdown thường:

```
![chú thích](uploads/news/ten-anh.jpg)
```

- Ảnh hiện **đúng tỉ lệ gốc**, rộng bằng cột chữ, không bị cắt.
- Để trống phần trong `[ ]` thì ảnh không có chú thích: `![](uploads/news/a.jpg)`
- Đặt ảnh ở đâu trong bài thì nó hiện ở đúng chỗ đó.

### Bộ ảnh ở cuối bài (tuỳ chọn)

Ngoài ảnh chèn giữa bài, còn có thể xếp một cụm ảnh ở cuối qua dòng `images:`
(ngăn nhau bằng `|`), với 3 kiểu bố cục chọn bằng `layout:`

| `layout:` | Bố cục |
|-----------|--------|
| `single` | Mỗi ảnh một dòng, nằm ngang, rộng 3/4 cột chữ |
| `pair` | Hai ảnh một dòng, chia đôi, hai ảnh bằng đúng kích thước nhau |
| `grid` | Cụm ảnh 3 cột, ô vuông (mặc định) |
