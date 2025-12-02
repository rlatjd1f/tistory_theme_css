# tistory_black_theme
티스토리 Book Club 블랙 테마

## 구글 트렌드 기반 자동 포스팅 스크립트
- 기능: 구글 트렌드 상위 키워드로 게임/주식·경제 카테고리를 판별한 뒤, SEO 최적화 마크다운 글을 LLM으로 생성해 로컬 `.md` 파일로 저장합니다. (티스토리 API 사용 없음)
- 환경변수: `OPENAI_API_KEY` (필수), `OPENAI_MODEL` (옵션, 기본 `gpt-4o-mini`)
- 의존성 설치: `pip install -r requirements.txt`
- 실행 예시:
  - 생성만 콘솔로 보기: `python auto_post.py --dry-run`
  - 마크다운 저장(기본 `posts/`): `python auto_post.py`
  - 저장 경로 지정: `python auto_post.py --output-dir articles`
- 출력 파일: `posts/YYYY-MM-DD-<키워드-슬러그>.md`에 제목(H1)+본문이 기록됩니다.
- 스케줄 예시(crontab): `0 10 * * * /usr/bin/python3 /path/to/auto_post.py >> /path/to/cron.log 2>&1`
