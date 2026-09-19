# -*- coding: utf-8 -*-
"""Pencarian web terpisah melalui Tavily dengan konteks yang dibatasi."""
from __future__ import annotations

from html import unescape
from urllib.parse import urlparse
import re

import requests

from config import TAVILY_API_KEY

TAVILY_SEARCH_URL = "https://api.tavily.com/search"
MAX_RESULTS = 5
MAX_CONTENT_PER_RESULT = 3600
MAX_TOTAL_CONTEXT = 12000


class WebSearchError(RuntimeError):
    """Error publik yang aman untuk fitur pencarian web."""


def _preferred_domains(
    query: str,
) -> list[str]:
    """Pilih domain resmi ketika entitasnya jelas dari query."""
    lowered = query.lower()

    if any(
        term in lowered
        for term in (
            "bank indonesia",
            "kurs transaksi bi",
            "jisdor",
        )
    ):
        return [
            "bi.go.id",
        ]

    if "presiden indonesia" in lowered:
        return [
            "presidenri.go.id",
            "setneg.go.id",
            "setkab.go.id",
            "indonesia.go.id",
        ]

    return []


def _valid_url(value: object) -> str:
    url = str(value or "").strip()
    parsed = urlparse(url)

    if (
        parsed.scheme != "https"
        or not parsed.netloc
    ):
        return ""

    return url


def _domain_allowed(
    url: str,
    preferred_domains: list[str],
) -> bool:
    """Pastikan hasil tidak keluar dari domain resmi yang diminta."""
    if not preferred_domains:
        return True

    hostname = (
        urlparse(url).hostname
        or ""
    ).lower()

    return any(
        (
            hostname == domain
            or hostname.endswith(
                "."
                + domain
            )
        )
        for domain in preferred_domains
    )

def _fetch_official_page(
    url: str,
    preferred_domains: list[str],
) -> str:
    """Ambil teks halaman resmi secara langsung agar data dinamis tidak basi."""
    if not _domain_allowed(
        url,
        preferred_domains,
    ):
        return ""

    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "AmperaTrinityAI/1.0"
                ),
            },
            timeout=15,
        )

        response.raise_for_status()

        if not _domain_allowed(
            response.url,
            preferred_domains,
        ):
            return ""

        content_type = response.headers.get(
            "content-type",
            "",
        ).lower()

        if "html" not in content_type:
            return ""

        source = response.text[
            :2_000_000
        ]

    except requests.RequestException:
        return ""

    source = re.sub(
        r"<script\b[^>]*>.*?</script>",
        " ",
        source,
        flags=re.I | re.S,
    )

    source = re.sub(
        r"<style\b[^>]*>.*?</style>",
        " ",
        source,
        flags=re.I | re.S,
    )

    source = re.sub(
        r"<[^>]+>",
        " ",
        source,
    )

    return " ".join(
        unescape(source).split()
    )


def _relevant_excerpt(
    raw: str,
    query: str,
) -> str:
    """Ambil bagian halaman di sekitar kata query."""
    normalized = " ".join(
        str(raw or "").split()
    )

    if len(normalized) <= MAX_CONTENT_PER_RESULT:
        return normalized

    lowered = normalized.lower()

    tokens = [
        token.lower().strip(
            ".,:;!?()[]"
        )
        for token in query.split()
        if len(token) >= 3
    ]

    priorities: list[str] = []

    if "usd" in tokens:
        priorities.append(
            "usd"
        )

    if "presiden" in tokens:
        priorities.append(
            "presiden"
        )

    priorities.extend(
        reversed(tokens)
    )

    position = next(
        (
            lowered.find(token)
            for token in priorities
            if lowered.find(token) >= 0
        ),
        0,
    )

    start = max(
        0,
        position - 700,
    )

    return normalized[
        start:start + MAX_CONTENT_PER_RESULT
    ]


def search_web(
    query: str,
    max_results: int = MAX_RESULTS,
) -> list[dict]:
    """Cari web dan kembalikan hasil Tavily yang sudah dibersihkan."""
    query = " ".join(
        str(query or "").split()
    ).strip()

    if not query:
        raise WebSearchError(
            "Pertanyaan pencarian masih kosong."
        )

    if not TAVILY_API_KEY:
        raise WebSearchError(
            "Web Search belum dikonfigurasi. "
            "Tambahkan TAVILY_API_KEY ke Streamlit Secrets."
        )

    preferred_domains = _preferred_domains(
        query
    )

    request_payload = {
        "api_key": TAVILY_API_KEY,
        "query": query[:1000],
        "search_depth": "advanced",
        "topic": "general",
        "max_results": max(
            1,
            min(
                int(max_results),
                MAX_RESULTS,
            ),
        ),
        "chunks_per_source": 3,
        "include_answer": False,
        "include_raw_content": "markdown",
    }

    if preferred_domains:
        request_payload[
            "include_domains"
        ] = preferred_domains

    try:
        response = requests.post(
            TAVILY_SEARCH_URL,
            json=request_payload,
            timeout=20,
        )

        response.raise_for_status()
        payload = response.json()

    except requests.Timeout as exc:
        raise WebSearchError(
            "Pencarian web melewati batas waktu. Coba lagi."
        ) from exc

    except requests.RequestException as exc:
        raise WebSearchError(
            "Layanan pencarian web sedang tidak tersedia."
        ) from exc

    except ValueError as exc:
        raise WebSearchError(
            "Respons layanan pencarian web tidak valid."
        ) from exc

    cleaned: list[dict] = []

    for item in payload.get("results") or []:
        if not isinstance(item, dict):
            continue

        url = _valid_url(
            item.get("url")
        )

        if (
            not url
            or not _domain_allowed(
                url,
                preferred_domains,
            )
        ):
            continue

        live_content = (
            _fetch_official_page(
                url,
                preferred_domains,
            )
            if preferred_domains
            else ""
        )

        raw_content = str(
            item.get("raw_content")
            or ""
        )

        snippet = str(
            item.get("content")
            or ""
        )

        content = _relevant_excerpt(
            (
                live_content
                or raw_content
                or snippet
            ),
            query,
        )

        if not content:
            continue

        cleaned.append({
            "title": " ".join(
                str(
                    item.get("title")
                    or url
                ).split()
            )[:240],
            "url": url,
            "content": content,
        })

    if not cleaned:
        raise WebSearchError(
            "Tidak ada sumber yang dapat diverifikasi "
            "untuk pencarian ini."
        )

    return cleaned


def history_with_web_context(
    history: list[dict],
    results: list[dict],
) -> list[dict]:
    """Tambahkan bukti pencarian tanpa mengubah riwayat yang terlihat."""
    copied = [
        dict(item)
        for item in history
    ]

    last_user_index = next(
        (
            index
            for index in range(
                len(copied) - 1,
                -1,
                -1,
            )
            if copied[index].get("role") == "user"
        ),
        None,
    )

    if last_user_index is None:
        return copied

    original = str(
        copied[last_user_index].get("content")
        or ""
    )

    sections: list[str] = []
    used = 0

    for index, result in enumerate(
        results,
        start=1,
    ):
        section = (
            f"SUMBER [{index}]\n"
            f"Judul: {result['title']}\n"
            f"URL: {result['url']}\n"
            f"Cuplikan: {result['content']}"
        )

        remaining = (
            MAX_TOTAL_CONTEXT
            - used
        )

        if remaining <= 0:
            break

        section = section[:remaining]
        sections.append(
            section
        )
        used += len(section)

    evidence = "\n\n".join(
        sections
    )

    copied[last_user_index]["content"] = (
        f"{original}\n\n"
        "HASIL PENCARIAN WEB TERVERIFIKASI:\n"
        f"{evidence}\n\n"
        "ATURAN JAWABAN WEB:\n"
        "- Gunakan hanya fakta yang didukung cuplikan di atas.\n"
        "- Jangan membuat angka, tanggal, kutipan, atau URL.\n"
        "- Cantumkan [1], [2], dan seterusnya setelah klaim terkait.\n"
        "- Tulis daftar sumber dengan URL persis seperti di atas.\n"
        "- Jika bukti tidak cukup, katakan tidak dapat memverifikasi."
    )

    return copied
