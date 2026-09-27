# Treddit

뉴스 데이터를 크롤링·분석해 최신 트렌드와 관련 정보를 제공하는 웹 서비스입니다.
졸업작품 [KbyC](https://github.com/groom2hub/KbyC)를 기반으로 코드 개선과 배포 파이프라인 구축을 진행합니다.

## 구성

| 디렉터리 | 설명 |
|---|---|
| `frontend/` | React 웹 클라이언트 |
| `server/` | FastAPI 백엔드 (회원, 게시판, 트렌드 API) |
| `crawl/` | 네이버 뉴스·키워드 크롤러 |
| `nlp/` | 기사 전처리 → LDA 토픽 모델링 → 트렌드 선정 |

## 로드맵

- [x] Phase 0. 원본 이관 및 정리 (히스토리·비밀키·산출물 제외)
- [ ] Phase 1. 환경변수 기반 설정, Dockerfile/compose 재작성
- [ ] Phase 2. CSV → DB 전환, 버그 수정, 테스트 추가
- [ ] Phase 3. Jenkins CI
- [ ] Phase 4. Kubernetes (k3s) 배포 + ArgoCD
- [ ] Phase 5. 모니터링, 프론트엔드 Vite 전환

## 설정

`.env.example`을 `.env`로 복사한 뒤 값을 채웁니다.
