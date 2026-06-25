# 텔레그램 API 수집 운용

> 역할: Telegram API로 소수몽키 채널 메시지와 원본 미디어를 수집해 후속 OCR/태그화용 인덱스를 만든다.
> 기준: API 수집을 기본 경로로 쓰고, Telegram Desktop Export는 보조/검증 경로로만 둔다.

## 준비값

| 항목 | 설명 |
|------|------|
| `TG_API_ID` | Telegram 개발자 앱의 API ID |
| `TG_API_HASH` | Telegram 개발자 앱의 API hash |
| `TG_ENTITY` | 공개 채널 username, 초대 링크, 또는 peer id |
| `TG_ENTITY_TITLE` | 초대 링크가 없는 비공개 채널을 제목 일부로 찾을 때 사용 |
| `TG_SESSION` | 선택값. Telethon 세션 파일 경로 |

환경변수 이름은 `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_ENTITY`, `TELEGRAM_ENTITY_TITLE`, `TELEGRAM_SESSION`도 사용할 수 있다.
값을 파일로 관리할 때는 `telegram_api.env.example`을 복사해 `.env`로 쓰되, 실제 값은 문서에 남기지 않는다.

초대 링크가 없는 비공개 채널은 `TG_ENTITY`를 비워두고 `TG_ENTITY_TITLE`에 Telegram 앱에서 보이는 채널명 일부를 넣는다.

```bash
TG_API_ID=12345678
TG_API_HASH=실제_hash
TG_ENTITY_TITLE=소수몽키
```

## 보안 원칙

- API ID/hash, 로그인 세션 파일, `.env` 파일은 문서에 기록하지 않는다.
- 기본 세션 위치는 `01_텔레그램_원천파서/API_수집/session/` 아래다.
- 세션 파일은 로그인 권한을 담고 있으므로 공유하거나 브리핑 폴더로 옮기지 않는다.

## 설치

```bash
python3 -m pip install -r 0_주식_에이전트/소수몽키_에이전트/requirements.txt
```

## 1차 로그인/수집

첫 실행 시 Telethon이 전화번호, Telegram 로그인 코드, 2단계 비밀번호를 물을 수 있다. 로그인에 성공하면 이후 같은 세션 파일을 재사용한다.

```bash
python3 0_주식_에이전트/소수몽키_에이전트/01_텔레그램_원천파서/telegram_api_collect.py \
  --env-file "0_주식_에이전트/소수몽키_에이전트/01_텔레그램_원천파서/.env" \
  --from-date 2026-05-28 \
  --to-date 2026-05-30 \
  --limit 1000 \
  --download-media
```

환경변수를 이미 셸에 넣었다면 `--env-file`은 생략한다.

## 비공개 채널 찾기

이메일 초대처럼 별도 `t.me` 링크가 없더라도, 같은 Telegram 계정이 이미 채널에 가입되어 있으면 dialog 목록에서 찾을 수 있다.

```bash
python3 0_주식_에이전트/소수몽키_에이전트/01_텔레그램_원천파서/telegram_api_collect.py \
  --env-file "0_주식_에이전트/소수몽키_에이전트/01_텔레그램_원천파서/.env" \
  --list-dialogs
```

출력에서 소수몽키 채널을 찾은 뒤 둘 중 하나를 쓴다.

```bash
# 방법 1: 제목 일부로 자동 탐색
TG_ENTITY_TITLE=소수몽키

# 방법 2: list-dialogs에 나온 peer_id를 직접 지정
TG_ENTITY=-1001234567890
```

제목 검색 결과가 여러 개면 수집기가 후보를 출력하고 멈춘다. 그때는 `TG_ENTITY`에 `peer_id`를 넣어 고정한다.

## 출력

| 파일 | 설명 |
|------|------|
| `API_수집/인덱스/소수몽키_API_원천인덱스.csv` | 메시지 단위 인덱스 |
| `API_수집/인덱스/소수몽키_API_원천인덱스.jsonl` | 후속 OCR/태그화용 구조화 인덱스 |
| `API_수집/인덱스/소수몽키_API_일자별_집계.csv` | 날짜별 메시지, 텍스트, 사진, 파일 수 |
| `API_수집/인덱스/소수몽키_API_최근3일_인덱스.md` | 사람이 읽는 최근 구간 인덱스 |
| `API_수집/photos/` | API로 내려받은 원본 사진 |
| `API_수집/files/` | API로 내려받은 첨부 파일 |

## OCR 연결

API 수집 후 OCR 샘플러는 `API_수집`을 원천 루트로 사용한다.

```bash
python3 0_주식_에이전트/소수몽키_에이전트/02_이미지_OCR_판독/run_ocr_sample.py \
  --index "0_주식_에이전트/소수몽키_에이전트/01_텔레그램_원천파서/API_수집/인덱스/소수몽키_API_원천인덱스.jsonl" \
  --export-dir "0_주식_에이전트/소수몽키_에이전트/01_텔레그램_원천파서/API_수집" \
  --output-dir "0_주식_에이전트/소수몽키_에이전트/02_이미지_OCR_판독/OCR_샘플" \
  --from-date 2026-05-28 \
  --to-date 2026-05-30 \
  --max-images 12
```

## 검증

- `indexed_messages`, `date_range`, `photo_links`, `file_links`가 예상 범위인지 확인한다.
- `--download-media`를 사용한 실행에서는 `API_수집/photos/`에 실제 파일이 생성되어야 한다.
- OCR 실행 시 `missing image` 오류가 나오면 API 수집을 `--download-media` 없이 돌렸는지 확인한다.
- Desktop Export와 병행 검증할 때는 같은 날짜 구간의 메시지 수와 사진 수 차이를 별도로 기록한다.
