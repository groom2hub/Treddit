# Treddit

뉴스 데이터를 크롤링·분석해 최신 트렌드와 관련 정보를 제공하는 웹 서비스입니다.
졸업작품 [KbyC](https://github.com/groom2hub/KbyC)를 기반으로 코드 개선과 배포 파이프라인 구축을 진행합니다.

## 구성

| 디렉터리 | 설명 |
|---|---|
| `frontend/` | React 웹 클라이언트 |
| `server/` | FastAPI 백엔드 (회원, 게시판, 트렌드 API) |
| `pipeline/` | 데이터 파이프라인: 네이버 뉴스 수집 → 명사 추출 → LDA 토픽 모델링 → 트렌드 선정 → DB 저장 |

## 로드맵

- [x] Phase 0. 원본 이관 및 정리 (히스토리·비밀키·산출물 제외)
- [x] Phase 1. 환경변수 기반 설정, Dockerfile/compose 재작성
- [ ] Phase 2. CSV → DB 전환, 버그 수정, 테스트 추가
- [ ] Phase 3. Jenkins CI
- [ ] Phase 4. Kubernetes (k3s) 배포 + ArgoCD
- [ ] Phase 5. 모니터링, 프론트엔드 Vite 전환

## 로컬 실행

```bash
cp .env.example .env   # 값 채우기
docker compose up -d --build
```

- 웹: http://localhost:3000 (nginx가 `/api/*`를 백엔드로 프록시)
- API 문서: http://localhost:8000/docs

### 데이터 파이프라인

배치 작업이라 `up`으로는 뜨지 않고 필요할 때 실행합니다.

```bash
# 어제(KST) 뉴스 수집 + 분석
docker compose run --rm pipeline run

# 특정 날짜 / 수집 없이 저장된 기사로 재분석
docker compose run --rm pipeline run --date 20260926
docker compose run --rm pipeline run --date 20260926 --skip-crawl

# KbyC 시절 CSV 결과(data/outputs/{YYYYMMDD}/)를 DB로 이관
docker compose run --rm pipeline import-csv /data/outputs
```

프론트엔드 개발 서버(`npm start`)는 `package.json`의 `proxy` 설정으로 `/api` 요청을 `localhost:8000`에 전달합니다.
