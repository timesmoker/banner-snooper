import os
from dotenv import load_dotenv
from mail_utils.send_mail import send_mail


load_dotenv()

GMAIL = os.getenv("GMAIL_ADDR")
PASS = os.getenv("GMAIL_APP_PASSWORD")
TO = os.getenv("GMAIL_ADDR")

def test_plain_email():
    assert send_mail(
        gmail_addr=GMAIL,
        gmail_app_password=PASS,
        to_address=TO,
        subject="테스트 1: 첨부 없음",
        body="이메일 본문 테스트입니다. 첨부 없음."
    )

def test_folder_no_zip():
    assert send_mail(
        gmail_addr=GMAIL,
        gmail_app_password=PASS,
        to_address=TO,
        subject="테스트 2: 폴더 첨부 (압축 X)",
        body="2025-04-03 폴더 첨부합니다. 압축 없음.",
        attachments="naver_m_screenshots/2025-04-03",
        make_zip=False
    )
def test_folder_with_zip():
    assert send_mail(
        gmail_addr=GMAIL,
        gmail_app_password=PASS,
        to_address=TO,
        subject="테스트 3: 폴더 첨부 (압축 O)",
        body="2025-04-03 폴더 첨부합니다. 압축됨.",
        attachments="naver_m_screenshots/2025-04-03",
        make_zip=True,
        zip_filename="2025-04-03.zip"
    )
def test_single_file():
    single_file = "naver_m_screenshots/2025-04-03/16~17/m_naver_20250403_163349.png"
    assert send_mail(
        gmail_addr=GMAIL,
        gmail_app_password=PASS,
        to_address=TO,
        subject="테스트 4: 단일 파일 첨부",
        body="단일 PNG 파일 첨부 테스트입니다.",
        attachments=single_file
    )

if __name__ == "__main__":
    test_folder_with_zip()
