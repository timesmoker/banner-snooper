import os
import logging
import smtplib
from email.message import EmailMessage
import mimetypes
from typing import Union
from .zip_utils import make_auto_clean_zip, collect_files_from_dir

logger = logging.getLogger(__name__)

def send_mail(
    gmail_addr: str,
    gmail_app_password: str,
    to_address: Union[str, list[str]],
    subject: str,
    body: str,
    *,
    attachments: Union[str,list[str]] = None,
    make_zip: bool = False,
    zip_filename: str = "attachments.zip"
) -> bool:

    msg = EmailMessage()
    msg["From"] = gmail_addr


    if isinstance(to_address, list):
        msg["To"] = ", ".join(addr.strip() for addr in to_address)
    elif isinstance(to_address, str):
        msg["To"] = to_address.strip()


    msg["Subject"] = subject
    msg.set_content(body)

    if attachments :
        ## 첨부파일이 문자열인 경우, 디렉토리인지 확인, 디렉토리라면 파일 목록으로 변환, 파일이면 리스트로 변환
        if isinstance(attachments, str):
            if os.path.isdir(attachments):
                attachments = collect_files_from_dir(attachments)
            else:
                attachments = [attachments]


        ## 압축여부 확인후 압축파일로 변환 -> bytes 이후 첨부
        if make_zip:
            if not zip_filename.endswith(".zip"):
                zip_filename += ".zip"
            zip_file = make_auto_clean_zip(attachments)
            if zip_file:
                msg.add_attachment(zip_file, maintype="application", subtype="zip", filename=zip_filename)


        ## 압축 안하면 파일 그대로 첨부
        elif not make_zip:
            for path in attachments:
                try :
                    with open(path, "rb") as f:
                        file_data = f.read()
                        mime_type, _ = mimetypes.guess_type(path)
                        maintype, subtype = mime_type.split("/") if mime_type else ("application", "octet-stream")
                    msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=os.path.basename(path))
                except Exception as e:
                    logger.error(f"첨부파일 {path} 추가 실패: {e}")
                    continue

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(gmail_addr, gmail_app_password)
            smtp.send_message(msg)
            logger.info("메일 전송 성공")
            return True

    except Exception as e:
        logger.error(f"메일 전송 실패: {e}")
        return False