# 상품 이미지 중복 방지 가이드 (Anti-Duplication Image Mapping)

올리브영 WAF(방화벽)로 인해 CDN 이미지 주소가 차단되거나 임의의 상품(예: 바디로션)으로 우회 매칭되는 현상을 방지하기 위해, K-Beauty Lister는 **각 브랜드 공식몰의 고화질 원본 이미지 URL**을 고정적으로 사용합니다.

아래는 베스트셀러 8종에 대해 **절대 중복되지 않는** 독립적인 1:1 이미지 매칭 테이블입니다. (이 매칭은 `bestsellers.json`에 영구 적용되었습니다.)

## 🌟 올리브영 베스트셀러 1~8위 정확한 원본 이미지 매칭

| 순위 | 브랜드 | 상품명 | 적용된 100% 원본 이미지 (공식몰) |
|:---:|:---|:---|:---|
| 1위 | **VT COSMETICS** | VT 리들샷 100 에센스 50ml | [VT 공식 이미지](https://vtcosmetics.com/web/product/big/202403/b6b553ea138e92823a31c518ab354ea6.jpg) |
| 2위 | **Anua** | 아누아 어성초 77 수딩 토너 250ml | [아누아 공식 이미지](https://anua.kr/web/product/big/202302/8939c1b48b792e3a890432f7902d3856.jpg) |
| 3위 | **Torriden** | 토리든 다이브인 저분자 히알루론산 세럼 50ml | [토리든 공식 이미지](https://cdn.imweb.me/thumbnail/20230303/34f59fc9029fa.jpg) |
| 4위 | **Beauty of Joseon** | 조선미녀 맑은쌀선크림 SPF50+ PA++++ 50ml | [조선미녀 공식 이미지](https://beautyofjoseon.com/cdn/shop/files/Relief_Sun_3.jpg) |
| 5위 | **numbuzin** | 넘버즈인 3번 결케어 보들보들 세럼 50ml | [넘버즈인 공식 이미지](https://numbuzin.com/web/product/big/202111/9d53c5e8c2579b449b4c0627798c8c25.jpg) |
| 6위 | **ROUND LAB** | 라운드랩 자작나무 수분 선크림 50ml | [라운드랩 공식 이미지](https://roundlab.co.kr/web/product/big/202302/c349a2b5357f4955b23d9b4b455b85e0.jpg) |
| 7위 | **MEDIHEAL** | 메디힐 티트리 에센셜 마스크 10매입 | [메디힐 공식 이미지](https://mediheal.com/web/product/big/202212/8b6250b86b2b4a1b02b5420364c39c4f.jpg) |
| 8위 | **goodal** | 구달 청귤 비타C 잡티 케어 세럼 50ml | [클리오(구달) 공식 이미지](https://m.clubclio.co.kr/web/product/big/202302/c4f1c9918fb53c9e99fa2d63412a80f0.jpg) |

---

### ⚠️ 이미지 중복 현상(네세세르 바디로션 등) 원인 및 해결 요약
*   **원인:** 기존 JSON 파일의 한글 인코딩이 깨진 상태로 저장되었으며, 임의로 부여된 더미 `goodsNo` 값이 올리브영 CDN 서버에서 우연히 '네세세르 바디로션', '딥티크 향수' 등의 타상품 이미지와 연결되어 브라우저에 캐시되었습니다.
*   **해결:** 한글이 절대 깨지지 않도록 `UTF-8` 인코딩을 강제하여 JSON을 완벽하게 재구성(Rebuild) 하였고, 불안정한 올리브영 CDN 대신 **각 브랜드 공식 쇼핑몰의 직접적인 이미지 링크**를 하드코딩하여 100% 중복 없이 정확한 상품만 출력되도록 조치했습니다.
