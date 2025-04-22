import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options

import timestamp
import os
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SCREENSHOT_FOLDER = "naver_m_screenshots"
SAVE_FOLDER = "naver_m_snapshots"
DA_PAGE_URL = "https://m.naver.com/"

def banner_snooper():
    print("배너 스누퍼 시작 : engine.py 진입")

    os.makedirs(SAVE_FOLDER, exist_ok=True)
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument('--no-sandbox')
    options.add_experimental_option("mobileEmulation", {"deviceName": "iPhone 8"})
    driver = webdriver.Chrome(options=options)

    try:
        time_now = datetime.now()
        date_now = time_now.strftime("%Y-%m-%d")
        hour_now = time_now.strftime("%H")
        hour_next = (time_now + timedelta(hours=1)).strftime("%H")

        screenshot_folder_path = os.path.join(SCREENSHOT_FOLDER, date_now, f"{hour_now}~{hour_next}")
        os.makedirs(screenshot_folder_path, exist_ok=True)

        time_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        naver_screenshotpath = os.path.join(screenshot_folder_path, f"m_naver_{time_stamp}.png")
        take_screenshot(driver, DA_PAGE_URL, naver_screenshotpath, is_landing_page=False)

        link_element = None
        try:
            iframe = driver.find_element(By.XPATH, "//div[@id='main_search_specialda_1']//iframe[starts-with(@id, 'main_search_specialda_1_')]")
            print("iframe 찾기 성공")

            driver.switch_to.frame(iframe)
            print("iframe 전환 성공")

            link_element = driver.find_element(By.XPATH, "//a[@href]")
        except:
            print("iframe 찾기 실패")
            try:
                link_element = driver.find_element(By.XPATH, "//*[@id='main_search_specialda_1']//a[@href]")
                print("링크 찾기 성공")
            except:
                print("링크 찾기 마저 실패")

        landing_page_url = link_element.get_attribute('href')
        time_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        link_log_path = os.path.join(screenshot_folder_path, "collected_link.txt")
        with open(link_log_path, "a") as f:
            f.write(f"[{time_stamp}] {landing_page_url}\n")

        landing_page_screenshotpath = os.path.join(screenshot_folder_path, f"m_landing_page_{time_stamp}.png")

        driver.get(landing_page_url)
        take_screenshot(driver, landing_page_url, landing_page_screenshotpath, is_landing_page=True)

    finally:
        driver.quit()


def take_screenshot(driver, target_url, save_path, is_landing_page=False):

    try:
        driver.get(target_url)
        time.sleep(20)  # Adjust this sleep time as needed based on your network speed

        if is_landing_page:
            handle_cookie_banner(driver)
        else:
            close_button_if_exists(driver)
    except Exception as e:
        print(f"URL 접근 실패: {target_url}, 에러: {e}")

    driver.get_screenshot_as_file(save_path)

    print(f"저장 완료: {save_path}")
    timestamp.overlay_time_with_header(save_path)
    return


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


def close_button_if_exists(driver):
    try:
        close_btn = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "lst_btn_close"))
        )
        close_btn.click()
        print("Close button clicked!")

        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "lst_btn_close"))
        )
        print("Overlay gone!")

    except TimeoutException:
        print("No close button found, skipping overlay.")
    except Exception as e:
        print(f"Other error closing overlay: {e}")

def handle_cookie_banner(driver):
    try:
        driver.execute_script("""
            // OneTrust
            let btn1 = document.querySelector('#onetrust-accept-btn-handler');
            if (btn1) btn1.click();

            // TrustArc
            let btn2 = document.querySelector('#truste-consent-button');
            if (btn2) btn2.click();

            // Cookiebot
            let btn3 = document.querySelector('#CybotCookiebotDialogBodyLevelButtonAccept');
            if (btn3) btn3.click();

            // Generic buttons (contains text 'Accept' or '동의' or '허용')
            let buttons = document.querySelectorAll('button');
            buttons.forEach(btn => {
                if (btn.innerText.includes('Accept') || btn.innerText.includes('동의') || btn.innerText.includes('허용')) {
                    btn.click();
                }
            });
        """)
        print("Tried to accept all common cookie banners!")

    except Exception as e:
        print(f"Error handling cookie banners: {e}")


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