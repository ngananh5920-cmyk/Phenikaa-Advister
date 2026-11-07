"""registration_offers.py
------------------------
Crawl + phân tích trang "Đăng ký học" (mục Đăng ký trực tuyến trên QLDT).

Trang này CHỈ có dữ liệu trong đợt đăng ký học phần. Ngoài đợt, danh sách
rỗng / không có học phần → website Advisor phải hiện thông báo
"Chưa có lịch đăng ký học".

Kết quả lưu ``dang_ky_hoc.json`` trong thư mục data của từng session:

    {
      "cap_nhat": "ISO datetime",
      "mo": true/false,          # True nếu có ít nhất 1 học phần đang mở
      "thong_bao": "...",        # khi mo=false
      "hoc_phan": [
        {
          "ma_hp": "FFS701071",
          "ten_hp": "Pickleball",
          "loai": "hoc_di" | "hoc_nang_diem" | "khac",
          "loai_nhan": "Học đi",
          "tuong_duong": "FFS701069" | null,   # mã HP gốc nếu là môn thay thế
          "raw": "FFS701071 - Pickleball(Học đi) ..."
        },
        ...
      ]
    }

Hàm ``prioritize_for_next_semester`` giao danh sách đang mở với lộ trình /
gợi ý kỳ tới của planner+advisor để trả về thứ tự ưu tiên đăng ký.
"""
from __future__ import annotations

import json
import re
import time
import unicodedata
from datetime import datetime
from pathlib import Path

OUTPUT_NAME = "dang_ky_hoc.json"

# Các hash có thể gặp trên QLDT (tùy phiên bản SPA). Matcher text vẫn là nguồn chính.
CANDIDATE_HASHES = (
    "#dangkyhoc",
    "#dangkytuy",
    "#dkhoc",
    "#dangky",
    "#dangkytuyenhoc",
    "#dangkytuyenhocphan",
)

EMPTY_MESSAGES = (
    "chưa có lịch đăng ký",
    "chua co lich dang ky",
    "không có học phần",
    "khong co hoc phan",
    "chưa mở đăng ký",
    "chua mo dang ky",
    "ngoài thời gian",
    "ngoai thoi gian",
    "không trong đợt",
    "khong trong dot",
)


def _fold(text) -> str:
    text = unicodedata.normalize("NFD", str(text or "")).replace("đ", "d").replace("Đ", "D")
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", text).strip().lower()


def _is_registration_menu(text: str, href: str = "") -> bool:
    """True nếu mục menu là 'Đăng ký học' (không phải kết quả / nguyện vọng / thi)."""
    t = _fold(text)
    h = _fold(href)
    if not t and not h:
        return False
    # Loại các mục liên quan nhưng KHÔNG phải danh sách đang mở đăng ký
    skip = (
        "ket qua", "kết quả", "nguyen vong", "nguyện vọng",
        "dang ky thi", "đăng ký thi", "tra cuu", "tra cứu",
    )
    if any(s in t for s in skip):
        return False
    if "dang ky hoc" in t or "đăng ký học" in t:
        return True
    if h in {_fold(x) for x in CANDIDATE_HASHES}:
        return True
    if h.startswith("#dangky") and "thi" not in h and "nguyen" not in h and "ketqua" not in h:
        return True
    return False


def parse_course_label(raw: str) -> dict | None:
    """
    'FFS701071 - Pickleball(Học đi) (môn tương đương của học phần FFS701069)'
    -> {ma_hp, ten_hp, loai, loai_nhan, tuong_duong, raw}
    """
    text = re.sub(r"\s+", " ", str(raw or "")).strip()
    if not text or len(text) < 4:
        return None

    # Bỏ prefix mũi tên / icon nếu còn
    text = re.sub(r"^[\s>›•·\-–]+", "", text).strip()

    m = re.match(
        r"^([A-Za-z]{2,6}\d{4,8}[A-Za-z0-9]*)\s*[-–:]\s*(.+)$",
        text,
    )
    if not m:
        # Thử bắt mã đứng đầu không có dấu gạch
        m2 = re.match(r"^([A-Za-z]{2,6}\d{4,8}[A-Za-z0-9]*)\b\s*(.*)$", text)
        if not m2:
            return None
        ma, rest = m2.group(1).upper(), m2.group(2).strip()
    else:
        ma, rest = m.group(1).upper(), m.group(2).strip()

    loai = "khac"
    loai_nhan = ""
    folded_rest = _fold(rest)
    if "hoc di" in folded_rest or "(học đi)" in rest.lower() or "(hoc di)" in folded_rest:
        loai = "hoc_di"
        loai_nhan = "Học đi"
    elif "nang diem" in folded_rest or "nâng điểm" in rest.lower():
        loai = "hoc_nang_diem"
        loai_nhan = "Học nâng điểm"

    tuong_duong = None
    m_eq = re.search(
        r"(?:môn\s+)?tương\s*đương\s*(?:của\s*)?(?:học\s*phần\s*)?([A-Za-z]{2,6}\d{4,8}[A-Za-z0-9]*)",
        rest,
        flags=re.I,
    )
    if not m_eq:
        m_eq = re.search(
            r"tuong\s*duong\s*(?:cua\s*)?(?:hoc\s*phan\s*)?([A-Za-z]{2,6}\d{4,8}[A-Za-z0-9]*)",
            _fold(rest),
        )
    if m_eq:
        tuong_duong = m_eq.group(1).upper()

    # Tên: bỏ phần (Học đi)/(Học nâng điểm) và ghi chú tương đương
    ten = rest
    ten = re.sub(r"\(Học\s*đi\)", "", ten, flags=re.I)
    ten = re.sub(r"\(Học\s*nâng\s*điểm\)", "", ten, flags=re.I)
    ten = re.sub(r"\(Hoc\s*di\)", "", ten, flags=re.I)
    ten = re.sub(r"\(Hoc\s*nang\s*diem\)", "", ten, flags=re.I)
    ten = re.sub(
        r"\([^)]*(?:tương\s*đương|tuong\s*duong)[^)]*\)",
        "",
        ten,
        flags=re.I,
    )
    ten = re.sub(r"\s+", " ", ten).strip(" -–")

    if not ten:
        ten = ma

    return {
        "ma_hp": ma,
        "ten_hp": ten,
        "loai": loai,
        "loai_nhan": loai_nhan or ("Học đi" if loai == "hoc_di" else "Học nâng điểm" if loai == "hoc_nang_diem" else ""),
        "tuong_duong": tuong_duong,
        "raw": text,
    }


# JS lấy danh sách học phần đang hiển thị trên trang Đăng ký học.
# Cố gắng bao quát nhiều cấu trúc DOM có thể gặp (list / card / table / link).
_OFFERS_JS = r"""
() => {
  const fold = (s) => (s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/đ/g, 'd').replace(/Đ/g, 'D').toLowerCase().replace(/\s+/g, ' ').trim();

  const out = [];
  const seen = new Set();

  const push = (raw) => {
    const t = (raw || '').replace(/\s+/g, ' ').trim();
    if (!t || t.length < 5) return;
    // Phải trông giống mã học phần (CSE..., FFS..., FEL...)
    if (!/[A-Za-z]{2,6}\d{4,}/.test(t)) return;
    const key = fold(t).slice(0, 80);
    if (seen.has(key)) return;
    seen.add(key);
    out.push(t);
  };

  // 1) Các phần tử thường gặp trên trang đăng ký (list item / course row)
  const selectors = [
    '.subject-item',
    '.hocphan-item',
    '.course-item',
    '.dk-hocphan',
    '.list-hocphan li',
    '.list-group-item',
    '[class*="hocphan"]',
    '[class*="subject"]',
    'a[href*="hocphan"]',
    'a[onclick*="hocphan"]',
    'a[onclick*="DangKy"]',
    'a[onclick*="dangky"]',
    '#zoneDanhSachHocPhan a',
    '#zoneDanhSachHocPhan li',
    '#zoneKetQua a',
    '.table tbody tr',
  ];
  for (const sel of selectors) {
    try {
      document.querySelectorAll(sel).forEach((el) => {
        // Ưu tiên text của chính phần tử; nếu là <tr> ghép các td
        let raw = '';
        if (el.tagName === 'TR') {
          raw = Array.from(el.querySelectorAll('td')).map(td => td.textContent.trim()).filter(Boolean).join(' - ');
        } else {
          raw = (el.getAttribute('title') || el.textContent || '').trim();
        }
        push(raw);
      });
    } catch (e) {}
  }

  // 2) Fallback: quét mọi node text có dạng "MÃ - Tên(Học ...)"
  if (out.length === 0) {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let node;
    const re = /[A-Za-z]{2,6}\d{4,8}[A-Za-z0-9]*\s*[-–]\s*[^\\n]{3,80}/;
    while ((node = walker.nextNode())) {
      const t = (node.textContent || '').trim();
      if (re.test(t)) push(t);
    }
  }

  // 3) Thông báo trang trống / ngoài đợt
  let emptyHint = '';
  const bodyText = fold(document.body ? document.body.innerText : '');
  const hints = [
    'chua co lich dang ky', 'khong co hoc phan', 'chua mo dang ky',
    'ngoai thoi gian', 'khong trong dot', 'chua den thoi gian',
    'het thoi gian dang ky', 'chua co du lieu',
  ];
  for (const h of hints) {
    if (bodyText.includes(h)) { emptyHint = h; break; }
  }

  return { items: out, emptyHint, url: location.href || '', title: document.title || '' };
}
"""


def parse_offers_from_page(page) -> dict:
    """Đọc danh sách học phần đang mở từ page Playwright hiện tại."""
    try:
        snap = page.evaluate(_OFFERS_JS) or {}
    except Exception as exc:
        return {
            "cap_nhat": datetime.now().isoformat(timespec="seconds"),
            "mo": False,
            "thong_bao": f"Không đọc được trang Đăng ký học: {type(exc).__name__}: {exc}"[:200],
            "hoc_phan": [],
            "raw_count": 0,
        }

    raw_items = snap.get("items") or []
    parsed = []
    seen_ma = set()
    for raw in raw_items:
        item = parse_course_label(raw)
        if not item:
            continue
        key = item["ma_hp"]
        if key in seen_ma:
            continue
        seen_ma.add(key)
        parsed.append(item)

    empty_hint = (snap.get("emptyHint") or "").strip()
    is_open = len(parsed) > 0
    if is_open:
        thong_bao = ""
    elif empty_hint:
        thong_bao = "Chưa có lịch đăng ký học (đợt đăng ký chưa mở hoặc trang báo không có học phần)."
    else:
        thong_bao = "Chưa có lịch đăng ký học. Có thể đợt đăng ký chưa mở hoặc trang chưa tải xong — hãy crawl lại khi đợt mở."

    return {
        "cap_nhat": datetime.now().isoformat(timespec="seconds"),
        "mo": is_open,
        "thong_bao": thong_bao,
        "hoc_phan": parsed,
        "raw_count": len(raw_items),
        "page_url": snap.get("url") or "",
    }


def parse_offers_from_html(html: str) -> dict:
    """Phân tích từ file HTML đã lưu (không cần browser)."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html or "", "html.parser")
    candidates = []
    for el in soup.find_all(["a", "li", "div", "span", "td", "button"]):
        raw = (el.get("title") or el.get_text(" ", strip=True) or "").strip()
        if re.search(r"[A-Za-z]{2,6}\d{4,}", raw):
            candidates.append(raw)

    parsed, seen = [], set()
    for raw in candidates:
        item = parse_course_label(raw)
        if not item or item["ma_hp"] in seen:
            continue
        seen.add(item["ma_hp"])
        parsed.append(item)

    body_fold = _fold(soup.get_text(" ", strip=True))
    empty = any(h in body_fold for h in EMPTY_MESSAGES)
    is_open = len(parsed) > 0
    return {
        "cap_nhat": datetime.now().isoformat(timespec="seconds"),
        "mo": is_open,
        "thong_bao": (
            "" if is_open else
            "Chưa có lịch đăng ký học (đợt đăng ký chưa mở hoặc trang báo không có học phần)."
            if empty else
            "Chưa có lịch đăng ký học. Có thể đợt đăng ký chưa mở — hãy crawl lại khi đợt mở."
        ),
        "hoc_phan": parsed,
        "raw_count": len(candidates),
    }


def crawl_registration_offers(page, out_dir=None, emit=None, wait_ms: int = 8000) -> dict:
    """Chờ trang ổn định rồi lấy danh sách học phần đang mở đăng ký."""
    def _log(status, msg):
        if emit:
            try:
                emit("crawl", status, msg)
            except Exception:
                pass

    # Chờ nội dung list xuất hiện hoặc timeout
    deadline = time.time() + wait_ms / 1000
    last_count = -1
    stable = 0
    data = None
    while time.time() < deadline:
        data = parse_offers_from_page(page)
        count = len(data.get("hoc_phan") or [])
        if count > 0 and count == last_count:
            stable += 1
            if stable >= 2:
                break
        else:
            stable = 0
        last_count = count
        try:
            page.wait_for_timeout(300)
        except Exception:
            time.sleep(0.3)

    if data is None:
        data = parse_offers_from_page(page)

    _log(
        "info" if data.get("mo") else "info",
        f"Đăng ký học: {'mở' if data.get('mo') else 'chưa mở'} — "
        f"{len(data.get('hoc_phan') or [])} học phần.",
    )

    if out_dir is not None:
        path = Path(out_dir) / OUTPUT_NAME
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        _log("info", f"Đã lưu {OUTPUT_NAME}")
    return data


def load_offers(user_dir: Path) -> dict | None:
    path = Path(user_dir) / OUTPUT_NAME
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    return data


def prioritize_for_next_semester(roadmap: dict, offers: dict | None, pace_key: str = "moderate") -> dict:
    """Giao danh sách đang mở với gợi ý kỳ tới / môn còn cần → xếp ưu tiên đăng ký.

    Trả về:
      - mo: đợt có mở không
      - thong_bao: khi chưa mở
      - priority: list môn nên đăng ký (đã mở + phù hợp lộ trình), có lý do
      - other_open: môn đang mở nhưng không nằm trong gợi ý/còn cần
      - missing_recommended: môn gợi ý kỳ tới nhưng KHÔNG thấy trong danh sách mở
    """
    from planner import PACE_OPTIONS, build_academic_plan, _course_credits

    if not offers or not offers.get("mo") or not (offers.get("hoc_phan") or []):
        return {
            "mo": False,
            "thong_bao": (offers or {}).get("thong_bao")
            or "Chưa có lịch đăng ký học. Hãy cập nhật dữ liệu QLĐT khi đợt đăng ký đang mở.",
            "priority": [],
            "other_open": [],
            "missing_recommended": [],
            "cap_nhat": (offers or {}).get("cap_nhat"),
            "pace": dict(PACE_OPTIONS.get(pace_key, PACE_OPTIONS["moderate"])),
        }

    courses = roadmap.get("mon_hoc") or []
    by_code = {str(c.get("ma_hp") or "").upper(): c for c in courses if c.get("ma_hp")}
    by_name = {}
    for c in courses:
        if c.get("ten_hp"):
            by_name[_fold(c["ten_hp"])] = c

    # Index offers theo mã + mã tương đương
    open_by_code = {}
    for o in offers.get("hoc_phan") or []:
        ma = str(o.get("ma_hp") or "").upper()
        if ma:
            open_by_code[ma] = o
        eq = str(o.get("tuong_duong") or "").upper()
        if eq and eq not in open_by_code:
            open_by_code[eq] = {**o, "matched_via": "tuong_duong"}

    plan = build_academic_plan(roadmap, pace_key=pace_key)
    suggested = []
    if plan.get("semesters"):
        suggested = plan["semesters"][0].get("courses") or []
    suggested_codes = {str(c.get("ma_hp") or "").upper() for c in suggested if c.get("ma_hp")}

    # Môn còn cần / có thể đăng ký / học lại
    need_statuses = {"CO_THE_DANG_KY", "CAN_HOC_LAI", "BI_KHOA"}
    need_codes = {
        str(c.get("ma_hp") or "").upper()
        for c in courses
        if c.get("trang_thai") in need_statuses and c.get("ma_hp")
        and not c.get("khong_tinh_tin_chi")
    }

    priority = []
    used = set()

    def reason_for(code, course, offer):
        reasons = []
        st = course.get("trang_thai") if course else None
        if st == "CAN_HOC_LAI":
            reasons.append("Học phần nợ — ưu tiên học lại")
        if code in suggested_codes:
            reasons.append("Nằm trong gợi ý kỳ tới của lộ trình")
        if st == "CO_THE_DANG_KY":
            reasons.append("Đã đủ tiên quyết, có thể đăng ký")
        if offer.get("loai") == "hoc_nang_diem":
            reasons.append("Đang mở đăng ký nâng điểm")
        elif offer.get("loai") == "hoc_di":
            reasons.append("Đang mở đăng ký học đi")
        if offer.get("tuong_duong") or offer.get("matched_via") == "tuong_duong":
            eq = offer.get("tuong_duong") or offer.get("ma_hp")
            reasons.append(f"Môn tương đương ({eq})")
        return reasons or ["Đang mở đăng ký và còn trong chương trình"]

    # 1) Gợi ý kỳ tới đang mở
    for c in suggested:
        code = str(c.get("ma_hp") or "").upper()
        offer = open_by_code.get(code)
        if not offer:
            continue
        used.add(code)
        if offer.get("ma_hp"):
            used.add(str(offer["ma_hp"]).upper())
        priority.append({
            "ma_hp": code,
            "ten_hp": c.get("ten_hp") or offer.get("ten_hp"),
            "so_tin": c.get("so_tin"),
            "khoi_kt": c.get("khoi_kt"),
            "trang_thai": c.get("trang_thai"),
            "offer": offer,
            "priority_rank": 1,
            "reasons": reason_for(code, c, offer),
        })

    # 2) Học lại / có thể ĐK đang mở (chưa nằm ở trên)
    for code in sorted(need_codes):
        if code in used:
            continue
        offer = open_by_code.get(code)
        if not offer:
            continue
        course = by_code.get(code)
        used.add(code)
        if offer.get("ma_hp"):
            used.add(str(offer["ma_hp"]).upper())
        rank = 0 if (course and course.get("trang_thai") == "CAN_HOC_LAI") else 2
        priority.append({
            "ma_hp": code,
            "ten_hp": (course or {}).get("ten_hp") or offer.get("ten_hp"),
            "so_tin": (course or {}).get("so_tin"),
            "khoi_kt": (course or {}).get("khoi_kt"),
            "trang_thai": (course or {}).get("trang_thai"),
            "offer": offer,
            "priority_rank": rank,
            "reasons": reason_for(code, course, offer),
        })

    priority.sort(key=lambda x: (x["priority_rank"], str(x.get("ten_hp") or "")))

    # 3) Môn đang mở nhưng không khớp chương trình / gợi ý
    other_open = []
    for o in offers.get("hoc_phan") or []:
        ma = str(o.get("ma_hp") or "").upper()
        eq = str(o.get("tuong_duong") or "").upper()
        if ma in used or eq in used:
            continue
        # Thử khớp theo tên
        course = by_code.get(ma) or by_name.get(_fold(o.get("ten_hp") or ""))
        other_open.append({
            "ma_hp": ma,
            "ten_hp": o.get("ten_hp"),
            "so_tin": (course or {}).get("so_tin"),
            "trang_thai": (course or {}).get("trang_thai"),
            "offer": o,
            "in_program": course is not None,
        })

    missing_recommended = []
    for c in suggested:
        code = str(c.get("ma_hp") or "").upper()
        if code and code not in open_by_code:
            missing_recommended.append({
                "ma_hp": code,
                "ten_hp": c.get("ten_hp"),
                "so_tin": c.get("so_tin"),
                "trang_thai": c.get("trang_thai"),
                "note": "Có trong gợi ý kỳ tới nhưng chưa thấy trong danh sách đang mở đăng ký",
            })

    # Giới hạn tín chỉ theo pace (chỉ đếm phần priority)
    pace = PACE_OPTIONS.get(pace_key, PACE_OPTIONS["moderate"])
    running = 0.0
    within_pace = []
    for item in priority:
        tc = 0.0
        try:
            tc = float(item.get("so_tin") or 0)
        except (TypeError, ValueError):
            tc = 0.0
        if running + tc <= pace["max"] + 1e-6 or not within_pace:
            within_pace.append(item)
            running += tc
        # vẫn giữ full priority; within_pace là gợi ý "đăng ký ngay trong hạn mức"

    return {
        "mo": True,
        "thong_bao": "",
        "cap_nhat": offers.get("cap_nhat"),
        "pace": dict(pace),
        "priority": priority,
        "within_pace": within_pace,
        "within_pace_credits": round(running, 1),
        "other_open": other_open,
        "missing_recommended": missing_recommended,
        "open_count": len(offers.get("hoc_phan") or []),
    }
