"""Generate the static course site from data/courses.json.

Every page is plain HTML so GitHub Pages can serve it without a build step.
Run from the repository root:

    python tools/build.py
"""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "courses.json"

FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
MONTHS = {
    1: "فروردین",
    2: "اردیبهشت",
    3: "خرداد",
    4: "تیر",
    5: "مرداد",
    6: "شهریور",
    7: "مهر",
    8: "آبان",
    9: "آذر",
    10: "دی",
    11: "بهمن",
    12: "اسفند",
}


def fa(value: object) -> str:
    return str(value).translate(FA_DIGITS)


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def format_date(iso: str | None) -> str | None:
    if not iso:
        return None
    year, month, day = (int(part) for part in iso.split("-"))
    return f"{fa(day)} {MONTHS[month]} {fa(year)}"


def format_duration(seconds: int | None) -> str | None:
    if not seconds:
        return None
    if seconds < 90:
        return f"{fa(round(seconds))} ثانیه"
    return f"{fa(round(seconds / 60))} دقیقه"


def session_meta(session: dict) -> list[str]:
    parts: list[str] = []
    date = format_date(session.get("date"))
    if date:
        parts.append(date)
    elif session.get("code"):
        parts.append(f"فایل {fa(session['code'])}")
    duration = format_duration(session.get("seconds"))
    if duration:
        parts.append(duration)
    return parts


FLAG_LABELS = {
    "recording": "جلسه برگزار نشد؛ فقط گزارش وضعیت ضبط",
    "text-only": "ضبط تصویری صفحهٔ خالی است؛ جزوه متنی است",
}


def render_session(session: dict) -> str:
    number = session.get("n")
    badge = f"جلسه {fa(f'{number:02d}')}" if isinstance(number, int) else "قطعهٔ کوتاه"
    meta = "".join(f'<span class="meta-item">{esc(item)}</span>' for item in session_meta(session))

    actions: list[str] = []
    video = session.get("video")
    if video:
        actions.append(
            f'<a class="act act-video" href="{esc(video)}" rel="noopener">'
            f'<span aria-hidden="true">▶</span> ویدیو</a>'
        )
    transcript = session.get("transcript")
    if transcript:
        actions.append(
            f'<a class="act act-text" href="{esc(transcript)}" download>'
            f'<span aria-hidden="true">↓</span> متن خام</a>'
        )
    else:
        actions.append('<span class="act is-empty">بدون متن</span>')

    note = session.get("note")
    if note:
        actions.append(
            f'<a class="act act-note" href="https://drive.google.com/file/d/{esc(note)}/view" rel="noopener">'
            f'<span aria-hidden="true">◫</span> جزوه</a>'
        )
    else:
        actions.append('<span class="act is-empty">بدون جزوه</span>')

    flag = session.get("flag")
    flag_html = f'<p class="session-flag">{esc(FLAG_LABELS[flag])}</p>' if flag in FLAG_LABELS else ""

    return (
        '<article class="session">'
        f'<div class="session-top"><span class="session-badge">{esc(badge)}</span>'
        f'<div class="session-meta">{meta}</div></div>'
        f"{flag_html}"
        f'<div class="session-actions">{"".join(actions)}</div>'
        "</article>"
    )


def render_extra(extra: dict) -> str:
    meta = " · ".join(
        filter(None, [format_date(extra.get("date")), format_duration(extra.get("seconds"))])
    )
    return (
        '<article class="session session-muted">'
        f'<div class="session-top"><span class="session-badge">{esc(extra["label"])}</span>'
        f'<div class="session-meta"><span class="meta-item">{esc(meta)}</span></div></div>'
        '<p class="session-flag">این فایل محتوای آموزشی ندارد و جزوه و متن برای آن ساخته نشده است.</p>'
        f'<div class="session-actions"><a class="act act-video" href="{esc(extra["video"])}" rel="noopener">'
        '<span aria-hidden="true">▶</span> ویدیو</a></div>'
        "</article>"
    )


def render_work(item: dict) -> str:
    return (
        f'<li><span class="work-kind">{esc(item["kind"])}</span>'
        f'<span class="work-text">{esc(item["text"])}</span></li>'
    )


def head(title: str, description: str, prefix: str = "") -> str:
    return (
        '<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta name="color-scheme" content="light dark">'
        f"<title>{esc(title)}</title>"
        f'<meta name="description" content="{esc(description)}">'
        f'<link rel="stylesheet" href="{prefix}style.css?v=4">'
        f'<script src="{prefix}theme.js"></script></head><body>'
    )


def header(data: dict, prefix: str = "") -> str:
    tg = data["telegram"]
    return (
        '<header class="site-header">'
        f'<a class="brand" href="{prefix}index.html">'
        '<span class="brand-mark" aria-hidden="true">ج</span>'
        '<span class="brand-text">جزوه‌های دانشگاه</span></a>'
        '<nav class="site-nav" aria-label="پیوندهای اصلی">'
        f'<a href="{prefix}index.html">درس‌ها</a>'
        f'<a href="{esc(tg["url"])}" rel="noopener">{esc(tg["label"])} <span aria-hidden="true">↗</span></a>'
        "</nav>"
        '<button class="theme-toggle" type="button" aria-pressed="false" hidden>'
        '<span aria-hidden="true">◐</span> حالت تاریک</button>'
        "</header>"
    )


def footer(data: dict, prefix: str = "") -> str:
    updated = format_date(data["updated"]) or data["updated"]
    return (
        '<footer class="site-footer">'
        f'<p>{esc(data["program"])}</p>'
        f'<p class="footer-note">{esc(data["semester"])} · آخرین به‌روزرسانی {esc(updated)}</p>'
        "</footer></body></html>"
    )


def render_index(data: dict) -> str:
    courses = data["courses"]
    total_sessions = sum(len(course["sessions"]) for course in courses)
    total_notes = sum(1 for course in courses for session in course["sessions"] if session.get("note"))
    total_texts = sum(1 for course in courses for session in course["sessions"] if session.get("transcript"))

    cards = []
    for course in courses:
        count = len(course["sessions"])
        teacher = (
            f'<span class="card-teacher">{esc(course["teacher"])}</span>'
            if course.get("teacher")
            else '<span class="card-teacher is-empty">استاد ثبت نشده</span>'
        )
        cards.append(
            f'<a class="course-card" href="{esc(course["page"])}">'
            f'<span class="card-title">{esc(course["title"])}</span>'
            f"{teacher}"
            f'<span class="card-foot"><span class="chip">{fa(count)} جلسه</span>'
            '<span class="card-arrow" aria-hidden="true">←</span></span></a>'
        )

    return (
        head("درس‌ها | جزوه‌های دانشگاه", "جزوه‌ها، متن خام و ویدیوی جلسه‌های نیمسال اول ۱۴۰۵–۱۴۰۶")
        + header(data)
        + "<main>"
        '<section class="hero hero-index">'
        '<div class="hero-body">'
        f'<p class="eyebrow">{esc(data["semester"])}</p>'
        "<h1>درس‌ها و جزوه‌ها</h1>"
        f'<p class="program">{esc(data["program"])}</p>'
        '<p class="hero-lead">برای هر جلسه ویدیوی کامل، متن خام پیاده‌شده و جزوهٔ مصور در دسترس است.</p>'
        '<div class="stats">'
        f'<span class="stat"><b>{fa(len(courses))}</b> درس</span>'
        f'<span class="stat"><b>{fa(total_sessions)}</b> جلسه</span>'
        f'<span class="stat"><b>{fa(total_texts)}</b> متن خام</span>'
        f'<span class="stat"><b>{fa(total_notes)}</b> جزوه</span>'
        "</div></div>"
        '<div class="hero-art" aria-hidden="true"></div>'
        "</section>"
        '<div class="course-grid">'
        + "".join(cards)
        + "</div></main>"
        + footer(data)
    )


def render_course(data: dict, course: dict) -> str:
    sessions = "".join(render_session(session) for session in course["sessions"])
    extras = "".join(render_extra(extra) for extra in course.get("extraVideos", []))
    resources = "".join(f"<li>{esc(item)}</li>" for item in course["resources"])
    resource_note = (
        f'<p class="resource-note">{esc(course["resourceNote"])}</p>'
        if course.get("resourceNote")
        else ""
    )
    work = "".join(render_work(item) for item in course["work"])
    others = "".join(
        f'<a class="course-pill" href="{esc(other["page"])}">{esc(other["title"])}'
        f'<span class="pill-count">{fa(len(other["sessions"]))}</span></a>'
        for other in data["courses"]
        if other["slug"] != course["slug"]
    )

    teacher = (
        f'<p class="teacher"><span class="teacher-label">استاد درس</span> {esc(course["teacher"])}</p>'
        if course.get("teacher")
        else '<p class="teacher is-empty"><span class="teacher-label">استاد درس</span> ثبت نشده</p>'
    )
    group = course["group"]
    handle = f'<p class="handle"><bdi dir="ltr">{esc(group["handle"])}</bdi></p>' if group.get("handle") else ""

    count = len(course["sessions"])
    return (
        head(f'{course["title"]} | جزوه‌های دانشگاه', f'ویدیو، متن خام و جزوهٔ {course["title"]}')
        + header(data)
        + "<main>"
        '<nav aria-label="مسیر صفحه"><a class="back-link" href="index.html">'
        '<span aria-hidden="true">→</span> همهٔ درس‌ها</a></nav>'
        f'<section class="hero hero-course {esc(course["visual"])}">'
        '<div class="hero-body">'
        f'<p class="eyebrow">{esc(data["semester"])}</p>'
        f'<h1>{esc(course["title"])}</h1>'
        f"{teacher}"
        f'<p class="stats stats-inline"><span class="stat"><b>{fa(count)}</b> جلسه</span>'
        f'<span class="stat"><b>{fa(sum(1 for s in course["sessions"] if s.get("transcript")))}</b> متن خام</span>'
        f'<span class="stat"><b>{fa(sum(1 for s in course["sessions"] if s.get("note")))}</b> جزوه</span></p>'
        "</div>"
        '<div class="hero-art" aria-hidden="true"></div>'
        "</section>"
        '<section class="panel" id="sessions">'
        f'<h2>جلسه‌ها <span class="count">{fa(count)}</span></h2>'
        f'<div class="session-grid">{sessions}{extras}</div>'
        f'<a class="button" href="{esc(course["driveFolder"])}" rel="noopener">'
        'پوشهٔ جزوه‌ها در گوگل درایو <span aria-hidden="true">↗</span></a>'
        "</section>"
        '<section class="panel">'
        "<h2>منابع معرفی‌شده</h2>"
        f'<ul class="resource-list">{resources}</ul>{resource_note}'
        "</section>"
        '<section class="panel">'
        "<h2>پروژه و تکلیف</h2>"
        f'<ul class="work-list">{work}</ul>'
        "</section>"
        '<section class="panel">'
        "<h2>گروه کلاس</h2>"
        f'<a class="button button-ghost" href="{esc(group["url"])}" rel="noopener">'
        f'{esc(group["label"])} <span aria-hidden="true">↗</span></a>{handle}'
        "</section>"
        '<section class="panel">'
        "<h2>درس‌های دیگر</h2>"
        f'<div class="course-pills">{others}</div>'
        "</section>"
        "</main>"
        + footer(data)
    )


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    (ROOT / "index.html").write_text(render_index(data), encoding="utf-8")
    for course in data["courses"]:
        (ROOT / course["page"]).write_text(render_course(data, course), encoding="utf-8")
    print(f"built index.html + {len(data['courses'])} course pages")


if __name__ == "__main__":
    main()
