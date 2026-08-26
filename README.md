---
title: K-Beauty Global Lister
emoji: 🧴
colorFrom: blue
colorTo: pink
sdk: docker
app_port: 8501
pinned: false
---

# K-Beauty Global Lister (K-뷰티 글로벌 리스터)

다이소 및 올리브영 화장품 대량 수집, AI 번역 및 최적화, 마진 계산 및 플랫폼(쇼피, 쇼피파이) 업로드용 템플릿 생성 자동화 웹 서비스입니다.

## 🚀 Hugging Face Spaces 24시간 무료 배포 방법

이 프로젝트는 Hugging Face Spaces에 **Docker** 컨테이너 기반으로 배포하여 24시간 컴퓨터를 켜두지 않고 사용할 수 있습니다.

### 배포 순서

1.  **GitHub 리포지토리 준비**:
    *   로컬 코드를 본인의 개인 GitHub 리포지토리에 푸시합니다.
2.  **Hugging Face 가입 및 스페이스 생성**:
    *   [Hugging Face](https://huggingface.co/)에 가입 및 로그인합니다.
    *   우상단 프로필 클릭 후 **`New Space`** 버튼을 누릅니다.
    *   **Space name** 입력 (예: `k-beauty-lister`)
    *   **SDK** 선택에서 **`Docker`**를 선택합니다.
    *   **Space hardware**는 기본 `Cpu basic (Free)`를 유지합니다.
    *   공개 범위는 **`Private`**으로 설정하는 것을 권장합니다 (개인용 툴이므로).
    *   하단의 **`Create Space`** 버튼을 누릅니다.
3.  **GitHub 연동 또는 파일 수동 업로드**:
    *   생성된 Space의 **`Files and versions`** 탭에서 `Upload files`를 눌러 이 프로젝트 폴더 안의 모든 파일(Dockerfile, app.py, templates/ 등)을 직접 업로드하거나,
    *   Hugging Face Space와 GitHub 리포지토리를 연동하여 메인 브랜치를 푸시하면 자동으로 빌드 및 배포가 시작됩니다.
4.  **사용 완료**:
    *   배포가 완료되면 Hugging Face에서 상시 가동되는 전용 주소를 발급해 줍니다. 폰이나 태블릿으로 언제든 접속하여 비밀번호 `635835`를 누르고 사용하시면 됩니다!
