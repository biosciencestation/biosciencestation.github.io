# Cập nhật nội dung website BioScience Station

Toàn bộ nội dung website nằm trong thư mục `content/` này, dưới dạng file
Markdown (`.md`). **Sửa các file này = website tự cập nhật.** Bạn không cần
động vào HTML.

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
| `site.md` | Tên lab, email, LinkedIn, địa chỉ, thông tin PI, tiêu đề trang chủ |
| `news.md` | Các bài News (mỗi bài bấm vào đọc được trang riêng) |
| `research.md` | 3 hướng nghiên cứu |
| `team.md` | Thành viên hiện tại (Our Team) |
| `alumni.md` | Cựu thành viên + dòng "hiện đang ở đâu" |
| `publications.md` | Danh sách publications |
| `gallery.md` | Các mục ảnh Gallery |

## Ví dụ thêm một bài News

Mở `news.md`, thêm vào đầu file (bài mới nhất lên trên):

```
title: Tiêu đề bài viết ở đây
date: July 2026
category: Milestone
image: images/anh-bai-viet.jpg
summary: Một dòng tóm tắt hiện ở thẻ tin.

Đoạn nội dung đầu tiên.

Đoạn nội dung thứ hai.
---
```
(dòng `---` để ngăn với bài kế tiếp)
