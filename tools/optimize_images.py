#!/usr/bin/env python3
"""Sinh ảnh WebP nhẹ + placeholder mờ cho mọi ảnh trong uploads/.

CHẠY KHI NÀO
    Sau mỗi lần thêm / thay ảnh trong uploads/:

        python tools/optimize_images.py

    (CI cũng tự chạy — xem .github/workflows/optimize-images.yml — nên nếu
    quên thì push lên GitHub vẫn được, bot sẽ commit phần thiếu.)

NÓ LÀM GÌ
    Mỗi ảnh gốc uploads/<đường-dẫn> sinh ra vài bản WebP thu nhỏ đặt trong
    uploads/opt/<đường-dẫn>.<chiều-rộng>.webp, cộng một "LQIP" — bản xem
    trước rộng 20px nhúng thẳng vào uploads/opt/manifest.json dạng base64.
    Trang web đọc manifest lúc chạy: ô ảnh hiện LQIP (phóng to nên nhòe,
    giống hệt ảnh thật về màu) ngay lập tức, rồi ảnh thật mờ dần đè lên.
    Đó là thứ thay cho ô xám trước đây.

    ẢNH GỐC KHÔNG BỊ SỬA. uploads/ vẫn là bản lưu trữ chất lượng cao; chỉ
    uploads/opt/ mới được trang web tải về. Nội dung trong content/*.md
    vẫn trỏ tới đường dẫn gốc như cũ, không phải sửa gì.

    Ảnh nào mà bản WebP không nhỏ hơn thật sự thì biến thể trỏ ngược về
    file gốc — không bao giờ phục vụ bản nặng hơn.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import sys
from pathlib import Path

try:
    from PIL import Image, ImageFilter, ImageOps
except ImportError:  # pragma: no cover - phụ thuộc lúc chạy tay
    sys.exit("Thiếu Pillow. Cài bằng:  pip install Pillow")

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "uploads"
OUT_DIR = SRC_DIR / "opt"
MANIFEST = OUT_DIR / "manifest.json"

SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}

# Ba bậc kích thước, khớp với ba cỡ mà trang thật sự hiển thị:
#   sm  ô gallery / thumbnail tin / thẻ thành viên   (~270-380px, thừa cho 2x)
#   md  thẻ nghiên cứu / ảnh trong bài / chân dung PI (~540-690px)
#   lg  hero toàn màn hình / lightbox
#
# lg = 2400 chứ không phải 1700: hero trải hết bề ngang cửa sổ, nên trên màn
# 1440px ở mức phóng 125% nó cần 1781px thật — bản 1700 bị trình duyệt kéo
# giãn, và trên màn 2x thì mới đạt 0.6 lần. Ảnh gốc vốn có sẵn 2435px.
TIERS = {"sm": 640, "md": 1100, "lg": 2400}

# 80 chứ không cao hơn: đo trên chính ảnh hero, q86 chỉ hạ sai lệch từ 2.69
# xuống 2.20 (thang 0-255, đều dưới ngưỡng mắt thấy) nhưng làm mọi ảnh nặng
# thêm ~29% — phần tải ngầm 1.77 -> 2.28 MB. Cái làm ảnh nét lên là bậc kích
# thước ở trên, không phải con số này.
QUALITY = 80          # WebP cho ảnh thật
LQIP_WIDTH = 20       # bản xem trước — vài trăm byte
LQIP_QUALITY = 35

# Đi vào signature() để đổi bậc/chất lượng là tự sinh lại, xem giải thích ở đó.
SETTINGS_SIG = "q{}-{}".format(QUALITY, "-".join(f"{t}{w}" for t, w in sorted(TIERS.items())))


def iter_sources():
    """Mọi ảnh trong uploads/, bỏ qua chính thư mục kết quả."""
    for path in sorted(SRC_DIR.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUFFIXES:
            continue
        if OUT_DIR in path.parents:
            continue
        yield path


def load(path: Path) -> Image.Image:
    im = Image.open(path)
    # Ảnh chụp từ điện thoại xoay bằng cờ EXIF; không "nướng" phép xoay vào
    # pixel thì bản WebP sẽ nằm ngang trong khi ảnh gốc đứng.
    im = ImageOps.exif_transpose(im)
    has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    return im.convert("RGBA" if has_alpha else "RGB")


def encode(im: Image.Image, width: int, quality: int) -> bytes:
    if im.width > width:
        height = max(1, round(im.height * width / im.width))
        im = im.resize((width, height), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    # method=6 là mức nén chậm nhất/nhỏ nhất của WebP. Chậm ở đây không sao:
    # script chỉ chạy khi có ảnh mới.
    im.save(buf, "WEBP", quality=quality, method=6)
    return buf.getvalue()


def lqip(im: Image.Image) -> str:
    tiny = encode(im.filter(ImageFilter.GaussianBlur(0.6)), LQIP_WIDTH, LQIP_QUALITY)
    return "data:image/webp;base64," + base64.b64encode(tiny).decode("ascii")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def signature(path: Path) -> str:
    """Vân tay nội dung của ảnh gốc, để biết bản đã sinh còn dùng được không.

    Không dùng mtime: máy CI vừa checkout xong thì mọi file đều có cùng giờ,
    nên mtime luôn nói "đã cũ" và cả kho ảnh bị mã hoá lại mỗi lần push. Hai
    lần mã hoá bằng hai phiên bản libwebp khác nhau ra hai chuỗi byte khác
    nhau, và commit sẽ phình lên vì những thay đổi không có thật.

    Vân tay gồm cả TIERS và QUALITY, không chỉ nội dung ảnh: đổi hai thông số
    đó mà vân tay không đổi thì mọi ảnh đều "còn dùng được" và lượt chạy tiếp
    theo không sinh lại gì cả — cài đặt mới nằm im trong file, không lên trang.
    """
    h = hashlib.sha1(path.read_bytes()).hexdigest()
    return f"{path.stat().st_size}-{h[:12]}-{SETTINGS_SIG}"


def process(src: Path, force: bool, cached: dict | None) -> dict:
    sig = signature(src)
    # Ảnh không đổi và mọi bản sinh ra vẫn còn nguyên: dùng lại y hệt.
    if not force and cached and cached.get("sig") == sig:
        made = [cached.get(t) for t in TIERS]
        if all(p and (ROOT / p).exists() for p in made):
            return cached

    im = load(src)
    entry = {"sig": sig, "w": im.width, "h": im.height}
    src_bytes = src.stat().st_size

    # Nhiều bậc có thể quy về cùng một chiều rộng khi ảnh gốc đã nhỏ
    # (ảnh 900px thì md và lg đều ra 900px) — mã hoá một lần, dùng chung.
    by_width: dict[int, str] = {}
    for tier, target in TIERS.items():
        width = min(target, im.width)
        if width not in by_width:
            out = OUT_DIR / (rel(src)[len("uploads/"):] + f".{width}.webp")
            out.parent.mkdir(parents=True, exist_ok=True)
            data = encode(im, width, QUALITY)
            # Ảnh gốc đã nhỏ hơn và không cần thu nhỏ (JPEG nén tốt, logo PNG
            # bảng màu…) thì phục vụ thẳng bản gốc.
            if width == im.width and len(data) >= src_bytes:
                out.unlink(missing_ok=True)
                by_width[width] = rel(src)
            else:
                out.write_bytes(data)
                by_width[width] = rel(out)
        entry[tier] = by_width[width]

    entry["lqip"] = lqip(im)
    return entry


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--force", action="store_true", help="mã hoá lại cả những bản đã có")
    args = ap.parse_args()

    # Console Windows mặc định cp1252, không in nổi tiếng Việt có dấu.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    if not SRC_DIR.is_dir():
        sys.exit(f"Không thấy thư mục {SRC_DIR}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        previous = json.loads(MANIFEST.read_text(encoding="utf-8")).get("images", {})
    except (OSError, ValueError):
        previous = {}

    images: dict[str, dict] = {}
    src_total = out_total = 0

    for src in iter_sources():
        key = rel(src)
        try:
            entry = process(src, args.force, previous.get(key))
        except Exception as exc:  # ảnh hỏng không được làm hỏng cả lượt chạy
            print(f"  BỎ QUA {key}: {exc}")
            continue
        images[key] = entry
        src_total += src.stat().st_size
        out_total += (ROOT / entry["sm"]).stat().st_size
        reused = " (dùng lại)" if previous.get(key) is entry else ""
        print(f"  {key}  {entry['w']}x{entry['h']}  ->  {len(set(entry[t] for t in TIERS))} bản{reused}")

    # Dọn file thừa của những ảnh đã xoá khỏi uploads/, để uploads/opt/ không
    # phình lên theo thời gian.
    keep = {ROOT / p for e in images.values() for t in TIERS if (p := e[t]).startswith("uploads/opt/")}
    for stale in OUT_DIR.rglob("*.webp"):
        if stale not in keep:
            stale.unlink()
            print(f"  xoá bản thừa {rel(stale)}")

    MANIFEST.write_text(
        json.dumps({"tiers": TIERS, "images": images}, indent=1, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(
        f"\n{len(images)} ảnh. Gốc {src_total / 1e6:.1f} MB"
        f" -> bản 'sm' {out_total / 1e6:.2f} MB. Manifest: {rel(MANIFEST)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
