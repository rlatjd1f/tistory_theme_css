# tistory_black_theme
티스토리 Book Club 블랙 테마

## 구글 트렌드 기반 자동 포스팅 스크립트
- 환경변수: `OPENAI_API_KEY`, `TISTORY_ACCESS_TOKEN`, `TISTORY_BLOG_NAME` (옵션: `TISTORY_CATEGORY_ID_GAME`, `TISTORY_CATEGORY_ID_FINANCE`, `OPENAI_MODEL`)
- 의존성 설치: `pip install -r requirements.txt`
- 실행 예시: `python auto_post.py --dry-run` (생성만), `python auto_post.py` (실제 업로드)
- 스케줄 예시(crontab): `0 10 * * * /usr/bin/python3 /path/to/auto_post.py >> /path/to/cron.log 2>&1`
- 카테고리: 게임/주식·경제(대한민국 대상), 구글 트렌드 상위 키워드로 하루 1건 작성
