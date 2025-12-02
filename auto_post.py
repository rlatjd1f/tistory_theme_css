#!/usr/bin/env python3
"""
매일 구글 트렌드 기반 주제를 선택해 LLM으로 SEO 지향 마크다운 글을 생성하는 스크립트.
- 실행: python auto_post.py --dry-run (콘솔 확인) / 크론 등으로 주기 실행
- 필요 env: OPENAI_API_KEY
- 선택 env: OPENAI_MODEL
"""

import argparse
import datetime as dt
import logging
import os
import random
import re
import sys
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from openai import OpenAI
from pytrends.request import TrendReq

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "game": ["게임", "공략", "패치", "신작", "랭킹", "배틀", "mmorpg", "fps", "콘솔", "모바일"],
    "finance": [
        "주식",
        "증시",
        "나스닥",
        "코스피",
        "금리",
        "환율",
        "공시",
        "실적",
        "ipo",
        "경제",
        "원자재",
        "채권",
    ],
}

CATEGORY_TAGS: Dict[str, List[str]] = {
    "game": ["게임", "공략", "트렌드"],
    "finance": ["주식", "경제", "마켓"],
}


def load_settings():
    load_dotenv()
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        sys.exit("OPENAI_API_KEY 가 설정되지 않았습니다.")

    return {
        "openai_key": openai_key,
        "openai_model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    }


def fetch_trending(limit: int = 20) -> List[str]:
    pt = TrendReq(hl="ko-KR", tz=540)
    df = pt.trending_searches(pn="south_korea")
    topics = [t for t in df[0].tolist() if isinstance(t, str)]
    logger.info("트렌딩 키워드 %d개 수집", len(topics))
    return topics[:limit]


def pick_topic(topics: List[str], preferred: Optional[str]) -> Tuple[str, str]:
    if preferred and preferred in CATEGORY_KEYWORDS:
        category = preferred
        topic = topics[0] if topics else "오늘의 핫이슈"
        return topic, category

    scored: List[Tuple[int, str, str]] = []
    for t in topics:
        for category, needles in CATEGORY_KEYWORDS.items():
            score = sum(1 for n in needles if n.lower() in t.lower())
            if score:
                scored.append((score, t, category))
    if scored:
        scored.sort(key=lambda x: (-x[0], x[1]))
        _, topic, category = scored[0]
        return topic, category

    fallback_category = preferred or random.choice(list(CATEGORY_KEYWORDS.keys()))
    fallback_topic = topics[0] if topics else "오늘의 핫이슈"
    return fallback_topic, fallback_category


def build_prompt(topic: str, category: str, date: str) -> List[Dict[str, str]]:
    system_prompt = (
        "당신은 검색 노출을 극대화하는 한국어 SEO 전문 작가입니다. "
        "주요 키워드를 제목과 H2/H3에 자연스럽게 배치하고, 스니펫·FAQ·목록을 활용한 "
        "마크다운 글을 작성합니다. 출처 링크는 신뢰도 높은 곳으로 최소 2개 제안하세요."
    )
    user_prompt = f"""
주제: {topic}
카테고리: {category} (game: 공략/신작/업데이트, finance: 국내외 주식/경제)
작성일: {date}
포함 사항:
- SEO 최적화된 H1 제목 1개(주요 키워드 포함)
- 120~180자 리드 요약에 핵심 키워드 1회 포함
- H2/H3 구조 본문: 배경→핵심 포인트→체크리스트/전략→FAQ 2문항(FAQ는 검색 의도형 질문)
- 3~5개 키워드 태그 제안(검색 노출용)
- 오늘 날짜를 포함한 짧은 마무리 문장
- 억측/루머 금지, 수치는 보수적으로 표현, 과장 금지
"""
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt.strip()},
    ]


def generate_markdown(client: OpenAI, prompt: List[Dict[str, str]], model: str) -> str:
    resp = client.chat.completions.create(model=model, messages=prompt, temperature=0.6)
    return resp.choices[0].message.content


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE)
    cleaned = re.sub(r"[-\s]+", "-", cleaned).strip("-").lower()
    return cleaned or "post"


def parse_args():
    parser = argparse.ArgumentParser(description="구글 트렌드 기반 SEO 마크다운 생성")
    parser.add_argument("--preferred-category", choices=list(CATEGORY_KEYWORDS.keys()), help="우선 카테고리 고정")
    parser.add_argument("--dry-run", action="store_true", help="실제 업로드 없이 생성 결과만 출력")
    parser.add_argument("--limit", type=int, default=20, help="트렌드 상위 몇 개까지 볼지")
    parser.add_argument("--output-dir", default="posts", help="생성된 마크다운 저장 경로")
    return parser.parse_args()


def main():
    args = parse_args()
    settings = load_settings()
    client = OpenAI(api_key=settings["openai_key"])

    try:
        trends = fetch_trending(limit=args.limit)
    except Exception as exc:
        logger.warning("구글 트렌드 수집 실패: %s", exc)
        trends = []

    topic, category = pick_topic(trends, args.preferred_category)
    today = dt.datetime.now().strftime("%Y-%m-%d")
    title = f"{topic} {category} 트렌드 브리핑 ({today})"
    prompt = build_prompt(topic, category, today)

    logger.info("선택된 주제: %s / 카테고리: %s", topic, category)
    md_text = generate_markdown(client, prompt, settings["openai_model"])
    tags = CATEGORY_TAGS.get(category, [])

    if args.dry_run:
        logger.info("[DRY RUN] 파일 저장 없이 결과를 출력합니다.")
        print("==== TITLE ====")
        print(title)
        print("\n==== MARKDOWN ====")
        print(md_text)
        return

    os.makedirs(args.output_dir, exist_ok=True)
    filename = f"{today}-{slugify(topic)}.md"
    path = os.path.join(args.output_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(md_text)

    logger.info("마크다운 저장 완료: %s", path)
    logger.info("참조 태그: %s", ", ".join(tags))


if __name__ == "__main__":
    main()
