#!/usr/bin/env python3
"""Giữ hai dòng <link rel="preload"> ảnh hero trong <head> khớp với site.md.

CHẠY KHI NÀO
    Sau mỗi lần đổi `hero_image:` trong content/site.md:

        python tools/sync_hero_preload.py

    (CI cũng tự chạy — xem .github/workflows/optimize-images.yml — nên nếu
    quên thì push lên GitHub vẫn được, bot sẽ commit phần thiếu.)

VÌ SAO CẦN
    Đường dẫn ảnh hero chỉ biết được sau khi React khởi động, tải
    content/site.md rồi tra uploads/opt/manifest.json — cỡ một giây chuỗi
    phụ thuộc, mà suốt thời gian đó trình duyệt còn chưa biết là có ảnh.
    Hai dòng preload trong <head> nói trước cho nó, nên ảnh bắt đầu tải từ
    mili-giây thứ ~15 thay vì ~1000. Đổi lại, đường dẫn phải ghi cứng.

    Ghi cứng thì sẽ lệch: đổi ảnh hero trong site.md mà quên sửa <head> là
    hero lặng lẽ chậm lại như cũ, cộng thêm một file tải thừa. Script này
    làm việc ghi tay đó, nên không còn gì để quên.

NÓ LÀM GÌ
    Đọc `hero_image:` trong content/site.md, tra hai bản thu nhỏ tương ứng
    trong manifest, ghi lại href của hai dòng preload trong index.html, rồi
    đồng bộ sang 404.html (bản GitHub Pages phục vụ cho mọi URL con) và
    bioscience-station.dc.html nếu có ở máy.

    Hai dòng preload phải khớp đúng với heroTier() trong index.html: cùng
    một mốc chia, để chỉ một trong hai file được tải. Sửa mốc ở một nơi thì
    phải sửa cả nơi kia — BREAKPOINT dưới đây là bản sao của mốc đó.
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_MD = ROOT / "content" / "site.md"
MANIFEST = ROOT / "uploads" / "opt" / "manifest.json"
PAGE = ROOT / "index.html"
# 404.html là bản GitHub Pages phục vụ cho mọi đường dẫn con (/gallery,
# /news/2…), nên nó phải giống hệt index.html. .dc.html là bản dành cho trình
# soạn DC, nằm trong .gitignore nên chỉ có ở máy.
COPIES = (ROOT / "404.html", ROOT / "bioscience-station.dc.html")

# Bản sao của mốc chia trong heroTier() (index.html). Điện thoại lấy bản
# 1100px, còn lại lấy 1700px.
BREAKPOINT = 860
LINKS = (
    (f"(max-width: {BREAKPOINT}px)", "md"),
    (f"(min-width: {BREAKPOINT + 1}px)", "lg"),
)


def hero_source() -> str | None:
    """Giá trị `hero_image:` ở đầu content/site.md."""
    m = re.search(r"^hero_image:[ \t]*(\S.*?)[ \t]*$", SITE_MD.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else None


def hero_mode() -> str:
    """Hero delivery mode from site.md; optimized remains the default."""
    m = re.search(r"^hero_image_mode:[ \t]*(\S.*?)[ \t]*$", SITE_MD.read_text(encoding="utf-8"), re.M)
    return m.group(1).strip().lower() if m else "optimized"


def rendition(src: str, tier: str) -> str | None:
    """Đường dẫn bản thu nhỏ của `src` ở bậc `tier`, theo manifest."""
    import json

    try:
        images = json.loads(MANIFEST.read_text(encoding="utf-8")).get("images", {})
    except (OSError, ValueError) as exc:
        sys.exit(f"Không đọc được {MANIFEST.relative_to(ROOT)}: {exc}")
    entry = images.get(src)
    return entry.get(tier) if entry else None


def swap_href(html: str, media: str, href: str) -> tuple[str, bool]:
    """Đổi href của đúng dòng preload mang `media`. Trả về (html, có đổi không).

    [^>]*? chứ không phải .*? — để phần khớp không tràn sang thẻ kế tiếp khi
    một dòng preload bị xoá mất.
    """
    pat = re.compile(
        r'(<link rel="preload" as="image"[^>]*?media="' + re.escape(media) + r'"[^>]*?href=")([^"]*)(")'
    )
    m = pat.search(html)
    if not m:
        sys.exit(
            f'Không thấy dòng <link rel="preload"> nào có media="{media}" trong '
            f"{PAGE.relative_to(ROOT)}. Hai dòng đó là lý do ảnh hero tải sớm — "
            "nếu vừa xoá thì thêm lại, đừng để script này im lặng bỏ qua."
        )
    if m.group(2) == href:
        return html, False
    return html[: m.start(2)] + href + html[m.end(2) :], True


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    src = hero_source()
    if not src:
        # Không có hero_image thì trang cũng không có ảnh hero để tải sớm.
        # Để nguyên <head>: xoá đi rồi phải nhớ thêm lại còn dễ quên hơn.
        print(f"Không thấy hero_image: trong {SITE_MD.relative_to(ROOT)} — bỏ qua.")
        return 0

    mode = hero_mode()

    # newline="" cả lúc đọc lẫn lúc ghi: index.html trong bản làm việc trên
    # Windows là CRLF, và đọc kiểu thường sẽ nuốt \r rồi ghi lại thành LF —
    # đổi kiểu xuống dòng của cả file chỉ vì sửa hai chữ. (open() chứ không
    # phải read_text(newline=...), vốn chỉ có từ Python 3.13.)
    with PAGE.open("r", encoding="utf-8", newline="") as f:
        html = f.read()
    changed = False
    for media, tier in LINKS:
        href = src if mode == "original" else rendition(src, tier)
        if not href:
            print(
                f"CẢNH BÁO: manifest chưa có bản '{tier}' của {src}."
                " Chạy tools/optimize_images.py trước rồi chạy lại. Bỏ qua dòng này."
            )
            continue
        html, did = swap_href(html, media, href)
        changed |= did
        print(f"  {media:<22} -> {href}")

    if changed:
        with PAGE.open("w", encoding="utf-8", newline="") as f:
            f.write(html)
        print(f"\nĐã cập nhật {PAGE.relative_to(ROOT)}.")
    else:
        print(f"\n{PAGE.relative_to(ROOT)} đã khớp.")

    # Chép bất kể có đổi hay không: hai bản kia có thể lệch vì lần sửa tay
    # trước đó, và đây là chỗ duy nhất biết chắc chúng phải giống nhau.
    for copy in COPIES:
        if copy is COPIES[0] or copy.exists():
            shutil.copyfile(PAGE, copy)
            print(f"  đồng bộ {copy.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
