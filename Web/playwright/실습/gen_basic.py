"""
Playwright 동기(Sync) 방식 예제
- 초보자가 자동화 흐름을 이해하기 가장 좋은 구조
"""

import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    # =====================================================
    # 1. Browser Launch
    # =====================================================
    # 실제 크롬 기반 브라우저를 실행
    # headless=False → 자동화 과정을 눈으로 확인
    browser = playwright.chromium.launch(headless=False)

    # =====================================================
    # 2. Browser Context 생성
    # =====================================================
    # Context는 독립된 브라우저 세션
    # (쿠키, 캐시, 로그인 정보가 다른 실행과 분리됨)
    context = browser.new_context()

    # =====================================================
    # 3. Page 생성
    # =====================================================
    # 실제로 클릭·입력·검증을 수행하는 탭(Tab)
    page = context.new_page()

    try:
        # =====================================================
        # 4. 자동화 동작 시작
        # =====================================================

        # Step 1. 사이트 접속
        # 지정한 URL로 이동
        print("Step 1: 사이트 접속")
        page.goto("https://playwright.dev/")

        # 메인 페이지로 정상 접속했는지 URL로 확인
        expect(page).to_have_url(re.compile(r"^https://playwright\.dev/?$"), timeout=15000)

        # Step 2. Docs 메뉴 클릭
        # 사용자 행동(메뉴 클릭)을 코드로 재현
        print("Step 2: Docs 메뉴 클릭")
        page.get_by_role("link", name="Docs").click()

        # Docs 페이지로 이동했는지 URL로 확인
        expect(page).to_have_url(re.compile(r".*/docs/.*"), timeout=15000)

        # Step 3. 검색 실행
        # 검색창에 포커스를 주고 검색어 입력 후 Enter
        print("Step 3: 검색어 입력")
        page.get_by_label("Search").click()
        page.get_by_placeholder("Search docs").fill("Locators")
        page.get_by_placeholder("Search docs").press("Enter")

        # Step 4. 결과 페이지 확인
        # 검색 결과 중 "Locators" 항목을 클릭
        print("Step 4: 결과 페이지 확인")
        page.get_by_role("link", name="Locators").first.click()

        # Locators 페이지로 실제 이동했는지 URL로 확인
        expect(page).to_have_url(re.compile(r".*/docs/locators.*", re.IGNORECASE), timeout=15000)

        # Locators 페이지의 h1 제목이 보이는지 확인
        # strict mode에서 heading이 여러 개 잡힐 수 있으므로 exact=True로 1개만 매칭
        locators_h1 = page.get_by_role("heading", name="Locators", exact=True).first
        expect(locators_h1).to_be_visible(timeout=15000)

        # 자동화 완료 후 화면을 유지하기 위해 사용자 입력 대기
        print("자동화 완료. 화면을 확인하세요.")
        input("엔터를 누르면 종료됩니다...")

    except Exception as e:
        # 자동화 실패 시에도 브라우저를 바로 닫지 않고
        # 현재 화면을 확인할 수 있도록 대기
        print("\n에러 발생:", e)
        input("에러 화면을 확인하세요. 엔터를 누르면 종료됩니다...")
        raise

    # =====================================================
    # 5. 정리 (Teardown)
    # =====================================================
    # 사용이 끝난 리소스 정리
    context.close()
    browser.close()


# =====================================================
# 6. 실행 진입점 (Entry Point)
# =====================================================
# sync_playwright()가 Playwright 객체를 생성하고
# run() 함수에 주입하여 전체 자동화를 실행
with sync_playwright() as playwright:
    run(playwright)
