import logging
import random
import timestamp
import os
import time

from dotenv import load_dotenv
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

"""

도커 사용시 컨테이너로 환경변수 주입하는것을 권장합니다!!
도커 사용시 저장할 경로를 마운트 해주세요!!

"""

load_dotenv()



ENABLE_GPU = os.getenv("USE_GPU", "false").lower() == "true"
DELAY = os.getenv("DELAY", "true").lower() == "true"
SCREENSHOT_FOLDER = "naver_m_screenshots"
DA_PAGE_URL = "https://m.naver.com/"

# 저장폴더 생성
os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)

#로깅
log_filename = os.path.join(SCREENSHOT_FOLDER, f"banner_snooper_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler()  # 콘솔에도 출력
    ]
)

logger = logging.getLogger(__name__)


def banner_snooper():
    logger.info("배너 스누퍼 시작 : engine.py 진입")

    options = Options()
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')    # 격리환경에서 작동을 전제로 sandbox를 비활성화
    if ENABLE_GPU:                          # GPU 있으면 활성화... 기본은
        options.add_argument("--disable-gpu")

    # 화면 크기 설정
    options.add_experimental_option("mobileEmulation", {"deviceName": "iPhone 8"})
    driver = webdriver.Chrome(options=options)

    try:
        # 폴더 생성
        time_now = datetime.now()
        date_now = time_now.strftime("%Y-%m-%d")
        hour_now = time_now.strftime("%H")
        hour_next = (time_now + timedelta(hours=1)).strftime("%H")

        screenshot_folder_path = os.path.join(SCREENSHOT_FOLDER, date_now, f"{hour_now}~{hour_next}")
        os.makedirs(screenshot_folder_path, exist_ok=True)

        time_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        naver_screenshotpath = os.path.join(screenshot_folder_path, f"m_naver_{time_stamp}.png")

        #메인 페이지 스크린샷 촬영
        take_screenshot(driver, DA_PAGE_URL, naver_screenshotpath, is_landing_page=False)

        # 랜딩 URL 찾기
        link_element = None
        try:

            link_element = driver.find_element(By.XPATH, "//*[@id='main_search_specialda_1']//a[@href]")
            logger.info("링크 찾기 성공")

        except:
            logger.info("iframe 찾기 시도")

            try:
                iframe = driver.find_element(By.XPATH,
                                             "//div[@id='main_search_specialda_1']//iframe[starts-with(@id, 'main_search_specialda_1_')]")
                logger.info("iframe 찾기 성공")

                driver.switch_to.frame(iframe)
                logger.info("iframe 전환 성공")

                link_element = driver.find_element(By.XPATH, "//a[@href]")
                logger.info("링크 찾기 성공")

            except:
                logger.error("링크 찾기 실패")

        # 랜딩 URL 전환 및 스크린샷 촬영
        if link_element:

            landing_page_url = link_element.get_attribute('href')

            #랜딩 URL 수집 및 저장

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
        time.sleep(20)                  # 페이지 로딩까지 대기

        if is_landing_page:             # 랜딩 페이지에서는 쿠키동의
            handle_cookie_banner(driver)

        else: #is_naver_main            # 네이버에서는 닫기 버튼 -> 네이버 업데이트하면 한동안 업데이트 확인창이 나와서 닫아줘야 함
            close_button_if_exists(driver)

        driver.get_screenshot_as_file(save_path)
        logger.info(f"저장 완료: {save_path}")
        timestamp.overlay_time_with_header(save_path)

    except Exception as e:
        logger.error(f"URL 접근 실패: {target_url}, 에러: {e}")

    return

def send_today_screenshots():
    from mail_utils.send_mail import send_mail

    logger.info("메일 발송 시작")
    gmail = os.getenv("GMAIL_ADDR")
    password = os.getenv("GMAIL_APP_PASSWORD")
    to = os.getenv("TO_ADDR")

    to_list = [to,gmail]

    today_folder = os.path.join("naver_m_screenshots", datetime.now().strftime("%Y-%m-%d"))

    if not os.path.isdir(today_folder):
        logger.error("저장폴더 없음 :", today_folder)
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

        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "lst_btn_close"))
        )
        logger.info("네이버 업데이트 찾 닫기 성공")
    except TimeoutException:
        logger.info("닫기버튼 없음.")

    except Exception as e:
        logger.error(f"닫기 버튼 누르기 중 오류 : {e}")

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
        logger.info("랜딩 페이지 쿠키 동의")

    except Exception as e:
        logger.error(f" 쿠키 동의중 에러 : {e}")

if __name__ == "__main__":
    try:
        # 랜덤 대기
        if DELAY:
            delay_seconds = random.randint(0, 20 * 60)
            logger.info(f"랜덤 대기 {delay_seconds // 60}분 {delay_seconds % 60}초")
            time.sleep(delay_seconds)
            banner_snooper()

            if datetime.now().hour == 20:
                logger.info("메일 발송 시작")
                send_today_screenshots()
        else:
            logger.info("테스트 모드로 시작")
            banner_snooper()
            logger.info("딜레이 없이 메일 발송 (테스트 모드)")
            send_today_screenshots()

    except Exception as e:
        logger.error("실행 중 에러 발생", exc_info=True)