import os
import zipfile
import io
from mail_utils.send_mail import make_auto_clean_zip, collect_files_from_dir

def test_make_zip_from_folder():
    # 테스트 대상 디렉토리
    folder_path = "naver_m_screenshots/2025-04-03"
    files = collect_files_from_dir(folder_path)

    # zip 생성
    zip_bytes = make_auto_clean_zip(files)

    # zip이 생성되었는지 확인
    assert zip_bytes is not None
    assert isinstance(zip_bytes, bytes)

    # zip 내용을 메모리에서 바로 열어보기
    with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zipf:
        namelist = zipf.namelist()
        print("ZIP 파일 내용:")
        for name in namelist:
            print(" └──", name)

        # 최소 하나 이상의 파일이 들어있어야 정상
        assert len(namelist) > 0
