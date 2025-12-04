#!/usr/bin/env python3
"""
입력한 주제로 LLM이 SEO 지향 마크다운 글을 생성하는 스크립트.
- 실행: python auto_post.py --topic "주제" [--category game|finance|general] --dry-run
- 필요 env: OPENAI_API_KEY
- 선택 env: OPENAI_MODEL
"""

import argparse
import datetime as dt
import logging
import os
import re
import sys
from typing import Dict, List

from dotenv import load_dotenv
from openai import OpenAI

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

CATEGORY_TAGS: Dict[str, List[str]] = {
    "game": ["게임", "공략", "트렌드"],
    "finance": ["주식", "경제", "마켓"],
    "general": [],
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


def build_prompt(topic: str, category: str, date: str) -> List[Dict[str, str]]:
    system_prompt = (
        "당신은 검색 노출을 극대화하는 한국어 SEO 전문 작가입니다. "
        "주요·변형 키워드를 제목과 H2/H3에 자연스럽게 배치하고, 스니펫·FAQ·목록을 활용한 "
        "마크다운 글을 작성합니다. 과장·확정적 표현·투자/의료/법률 조언을 금지하고, 수치는 범위/추정으로 "
        "보수적으로 적습니다. 최근 기사·블로그·커뮤니티·보고서에서 드러난 핵심 사실을 최대한 반영하고 5~7개로 "
        "묶어 전달하세요. 모든 주장에는 근거를 달며, 출처 링크는 신뢰도 높은 곳으로 최소 2개 제안하세요. "
        "본문 분량은 약 3,000자(±10%)로 맞추고, 제목/단락 구성은 SEO에 적합한 H1/H2/H3 체계를 따릅니다."
    )
    user_prompt = f"""
주제: {topic}
카테고리: {category}
작성일: {date}
포함 사항:
- SEO 최적화된 H1 제목 1개(주요 키워드 포함)
- 120~180자 리드 요약에 핵심 키워드 1회 포함
- H2/H3 구조 본문: 배경→핵심 포인트(최근 보도된 사실·인물·수치·일정)→체크리스트/전략→FAQ 2문항(FAQ는 검색 의도형 질문, 각 2~3문장), 전체 분량 약 3,000자(±10%)
- H2/H3마다 주요/변형 키워드를 자연스럽게 1회 포함, 제목/소제목도 검색 의도를 반영해 작성
- 출처 링크 2곳 이상(한국/영문 신뢰도 높은 매체) 제안
- 3~5개 키워드 태그 제안(검색 노출용, '태그: ...' 한 줄로 표기)
- 오늘 날짜를 포함한 짧은 마무리 문장
- 억측/루머 금지, 과장 금지, 투자·의료·법률 조언 금지, 수치는 범위/추정으로 보수적 표현
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
    parser = argparse.ArgumentParser(description="입력 주제로 SEO 마크다운 생성")
    parser.add_argument("--topic", required=True, help="작성할 주제 텍스트")
    parser.add_argument("--category", choices=list(CATEGORY_TAGS.keys()), default="general", help="카테고리 (기본: general)")
    parser.add_argument("--dry-run", action="store_true", help="실제 업로드 없이 생성 결과만 출력")
    parser.add_argument("--output-dir", default="posts", help="생성된 마크다운 저장 경로")
    return parser.parse_args()


def main():
    args = parse_args()
    settings = load_settings()
    client = OpenAI(api_key=settings["openai_key"])

    topic = args.topic
    category = args.category
    today = dt.datetime.now().strftime("%Y-%m-%d")
    title = f"{topic} {category} 브리핑 ({today})"
    prompt = build_prompt(topic, category, today)

    logger.info("입력 주제: %s / 카테고리: %s", topic, category)
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
