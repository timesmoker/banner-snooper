import logging
import os
import zipfile
import io


logger = logging.getLogger(__name__)

def make_auto_clean_zip(files: list[str]) -> bytes:
    buffer = io.BytesIO()
    try:
        common_root = os.path.commonpath(files)  #  공통 경로 추출

        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for file in files:
                arcname = os.path.relpath(file, start=common_root)
                zip_file.write(file, arcname=arcname)

        buffer.seek(0)
        return buffer.read()

    except Exception as e:
        logger.error(f"zip 파일 생성 실패: {e}")
        return None


def collect_files_from_dir(directory: str) -> list[str]:
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            full_path = os.path.abspath(os.path.join(root, filename))
            files.append(full_path)
    return files