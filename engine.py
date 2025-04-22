import time
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
import os
import timestamp
from dotenv import load_dotenv

SCREENSHOT_FOLDER = "naver_m_screenshots"
SAVE_FOLDER = "naver_m_snapshots"
DA_PAGE_URL = "https://m.naver.com/"

def banner_snooper():
    print("배너 스누퍼 시작 : engine.py 진입")

    os.makedirs(SAVE_FOLDER, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 375, 'height': 667},
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 13_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Mobile/15E148 Safari/604.1'
        )
        page = context.new_page()

        try:
            time_now = datetime.now()
            date_now = time_now.strftime("%Y-%m-%d")
            hour_now = time_now.strftime("%H")
            hour_next = (time_now + timedelta(hours=1)).strftime("%H")

            screenshot_folder_path = os.path.join(SCREENSHOT_FOLDER, date_now, f"{hour_now}~{hour_next}")
            os.makedirs(screenshot_folder_path, exist_ok=True)

            time_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            naver_screenshotpath = os.path.join(screenshot_folder_path, f"m_naver_{time_stamp}.png")

            take_screenshot(page, DA_PAGE_URL, naver_screenshotpath, is_landing_page=False)

            # 링크 추출
            try:
                frame = page.frame_locator("//iframe[starts-with(@id, 'main_search_specialda_1_')]")
                link_element = frame.locator("//a[@href]").first
                landing_page_url = link_element.get_attribute('href')
                print(f"iframe 링크 추출 성공: {landing_page_url}")
            except:
                print("iframe 링크 추출 실패, 메인 페이지에서 찾기 시도")
                try:
                    link_element = page.locator("//*[@id='main_search_specialda_1']//a[@href]").first
                    landing_page_url = link_element.get_attribute('href')
                    print(f"링크 추출 성공: {landing_page_url}")
                except:
                    print("링크 추출 실패")
                    return

            # 링크 저장
            link_log_path = os.path.join(screenshot_folder_path, "collected_link.txt")
            with open(link_log_path, "a") as f:
                f.write(f"[{time_stamp}] {landing_page_url}\n")

            # 랜딩 페이지 스크린샷
            landing_page_screenshotpath = os.path.join(screenshot_folder_path, f"m_landing_page_{time_stamp}.png")
            page.goto(landing_page_url)
            take_screenshot(page, landing_page_url, landing_page_screenshotpath, is_landing_page=True)

        finally:
            browser.close()
            print("브라우저 정상 종료")


def take_screenshot(page, target_url, save_path, is_landing_page=False):
    try:
        page.goto(target_url)
        time.sleep(20)  # 네트워크 속도에 맞춰 조정

        if is_landing_page:
            handle_cookie_banner(page)
        else:
            close_button_if_exists(page)

        page.screenshot(path=save_path)
        print(f"저장 완료: {save_path}")
        timestamp.overlay_time_with_header(save_path)

    except Exception as e:
        print(f"URL 접근 실패: {target_url}, 에러: {e}")


def send_today_screenshots():
    from mail_utils.send_mail import send_mail

    print("메일 발송 시작")
    gmail = os.getenv("GMAIL_ADDR")
    password = os.getenv("GMAIL_APP_PASSWORD")
    to = os.getenv("TO_ADDR")  # 보내야 하는 주소

    to_list = [to,gmail]

    today_folder = os.path.join("naver_m_screenshots", datetime.now().strftime("%Y-%m-%d"))

    if not os.path.isdir(today_folder):
        print("저장폴더 없음 :", today_folder)
        return

    send_mail(
        gmail_addr=gmail,
        gmail_app_password=password,
        to_address=to_list,
        subject=f"[자동 발송] {os.path.basename(today_folder)} naver 배너 모음",
        body=f" {os.path.basename(today_folder)} 의 네이버 배너와 랜딩 페이지 스크린샷입니다.",
        attachments=today_folder,
        make_zip=True,
        zip_filename=f"{os.path.basename(today_folder)}.zip"
    )


def close_button_if_exists(page):
    try:
        if page.locator(".lst_btn_close").is_visible():
            page.locator(".lst_btn_close").click()
            print("닫기 버튼 클릭 완료!")
    except Exception as e:
        print(f"닫기 버튼 처리 실패: {e}")


def handle_cookie_banner(page):
    try:
        # OneTrust
        if page.locator("#onetrust-accept-btn-handler").is_visible():
            page.locator("#onetrust-accept-btn-handler").click()
            print("OneTrust 쿠키 배너 클릭!")

        # Generic buttons
        buttons = page.locator("button")
        count = buttons.count()
        for i in range(count):
            btn = buttons.nth(i)
            text = btn.inner_text().strip()
            if "Accept" in text or "동의" in text or "허용" in text:
                btn.click()
                print(f"쿠키 버튼 클릭: {text}")
                break

    except Exception as e:
        print(f"쿠키 배너 처리 실패: {e}")


if __name__ == "__main__":
    load_dotenv()
    DELAY = os.getenv("DELAY", "true").lower() == "true"

    try:
        banner_snooper()

        if DELAY:
            if datetime.now().hour == 20:
                send_today_screenshots()
        else:
            print("딜레이 없이 메일 발송 (테스트 모드)")
            send_today_screenshots()

    except Exception as e:
        print(f"에러 발생: {e}")