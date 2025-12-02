# Repository Guidelines

## Project Structure & Module Organization
- Theme CSS: `Tistory_black.css` (primary) and `Tistory_white.css` (alternate); keep section comments (`01. Web Font` etc.) intact so future edits stay navigable.
- Templates: `TistoryHtml.html` and `reference.html` are preview pages for local testing or screenshots.
- Assets: `images/` holds packaged icons referenced by the themes; optimize additions and keep filenames lowercase with underscores.

## Build, Test, and Development Commands
- `python -m http.server 8000` (run in repo root) — serve the static files locally; open `http://localhost:8000/reference.html` to verify layout and typography.
- If you add external fonts or assets, confirm their URLs resolve while the server is running to catch CORS or mixed-content issues.

## Coding Style & Naming Conventions
- Match existing CSS style: tab indentation inside blocks, blank lines between sections, and section headers in block comments for quick scanning.
- Use descriptive, hyphenated class names (e.g., `.comment-list`, `.post-title`) and keep color tokens consistent between black/white themes when adding variants.
- Prefer shorthands sparingly (e.g., keep `font-family` declarations explicit) to avoid overriding theme-specific tweaks. Preserve `@font-face` ordering to limit flashes of unstyled text.

## Testing Guidelines
- No automated tests; rely on visual verification in modern browsers (Chrome, Firefox, Safari) and at least one mobile viewport using dev tools.
- Compare both themes when changing shared components: check readability, hover/focus states, and contrast against the dark (`#202124`) and light backgrounds.
- When adjusting typography, validate that Hangul and Latin glyphs render as expected with the bundled font stack.

## Commit & Pull Request Guidelines
- Commits: write concise, imperative subjects (`Adjust sidebar spacing`, `Fix code block font`). Group related style changes together; avoid mixing cosmetic tweaks with structural edits.
- PRs: include a short summary, before/after screenshots from `reference.html`, and note any external asset or font additions. Reference linked issues where applicable and call out any known visual regressions or follow-up items.

## Security & Configuration Tips
- External fonts are loaded from public CDNs; verify sources are HTTPS and stable before adding new ones.
- Avoid embedding secrets in CSS URLs or HTML templates. If using third-party scripts for previews, keep them pinned to exact versions and document their purpose in the PR.

## Agent Notes
- 사용자 요청에 대한 답변은 한글로 제공합니다.

