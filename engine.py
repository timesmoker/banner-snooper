import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import timestamp
import os

from selenium.webdriver.common.by import By

SCREENSHOT_FOLDER = "naver_m_screenshots"
SAVE_FOLDER = "naver_m_snapshots"
DA_PAGE_URL = "https://m.naver.com/"

def banner_snooper():
    print("배너 스누퍼 시작 : engine.py 진입")
    os.makedirs(SAVE_FOLDER, exist_ok=True)
    options = Options()

    options.add_argument("--headless")  # Run in headless mode
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_experimental_option("mobileEmulation", {"deviceName": "iPhone 8"})
    driver = webdriver.Chrome(options=options)

    time_now = datetime.now()

    date_now = time_now.strftime("%Y-%m-%d")
    hour_now = time_now.strftime("%H")
    hour_next = (time_now + timedelta(hours=1)).strftime("%H")

    screenshot_folder_path = os.path.join(SCREENSHOT_FOLDER,date_now, f"{hour_now}~{hour_next}")
    os.makedirs(screenshot_folder_path, exist_ok=True)

    time_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    naver_screenshotpath = os.path.join(screenshot_folder_path, f"m_naver_{time_stamp}.png")
    take_screenshot(driver, DA_PAGE_URL, naver_screenshotpath)

    link_element = None
    try:
        iframe = driver.find_element(By.XPATH, "//div[@id='main_search_specialda_1']//iframe[starts-with(@id, 'main_search_specialda_1_')]")
        print("iframe 찾기 성공")

        driver.switch_to.frame(iframe)
        print("iframe 전환 성공")

        link_element = driver.find_element(By.XPATH, "//a[@href]")
    except :
        print("iframe 찾기 실패")
        try:
            link_element = driver.find_element(By.XPATH, "//*[@id='main_search_specialda_1']//a[@href]")
            print("링크 찾기 성공")

        except:
            print("링크 찾기 마저 실패")


    landing_page_url = link_element.get_attribute('href')

    time_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    link_log_path = os.path.join(screenshot_folder_path, "collected_links.txt")
    with open(link_log_path, "a") as f:
        f.write(f"[{time_stamp}] {landing_page_url}\n")

    landing_page_screenshotpath = os.path.join(screenshot_folder_path, f"m_landing_page_{time_stamp}.png")
    take_screenshot(driver, landing_page_url, landing_page_screenshotpath)

    driver.quit()
    return


def take_screenshot(driver, target_url, save_path):
    driver.get(target_url)
    time.sleep(5)  # Adjust this sleep time as needed based on your network speed

    driver.get_screenshot_as_file(save_path)

    print(f"저장 완료: {save_path}")
    timestamp.overlay_time_with_header(save_path)
    return


def send_today_screenshots():
    from mail_utils.send_mail import send_mail
    from dotenv import load_dotenv

    load_dotenv()
    gmail = os.getenv("GMAIL_ADDR")
    password = os.getenv("GMAIL_APP_PASSWORD")
    to = gmail  # 보내야 하는 주소

    today_folder = os.path.join("naver_m_screenshots", datetime.now().strftime("%Y-%m-%d"))
    if not os.path.isdir(today_folder):
        print("오늘 폴더 없음:", today_folder)
        return

    result = send_mail(
        gmail_addr=gmail,
        gmail_app_password=password,
        to_address=to,
        subject=f"[자동 발송] {os.path.basename(today_folder)} naver 배너 모음",
        body=f" {os.path.basename(today_folder)} 의 네이버 배너와 랜딩 페이지 스크린샷입니다.",
        attachments=today_folder,
        make_zip=True,
        zip_filename=f"{os.path.basename(today_folder)}.zip"
    )


if __name__ == "__main__":

    run_immediately = os.getenv("DELAY", "true").lower() == "false"

    try:
        banner_snooper()

        if run_immediately:
            send_today_screenshots()
        else:
            if datetime.now().hour == 20:  # 정시 조건 (8시에만 실행)
                send_today_screenshots()

    except Exception as e:
        print(f"에러 발생: {e}")