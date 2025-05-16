from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os
import locale
import logging

logger = logging.getLogger(__name__)

# 한글 요일 출력을 위해 locale 설정
try:
    locale.setlocale(locale.LC_TIME, 'ko_KR.UTF-8')
except locale.Error:
    logger.error("한글 locale 설정 실패 → 영어로 출력됩니다.")

def get_font(size=18):
    font_paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def format_time_korean(dt):
    hour = dt.hour
    minute = dt.minute
    ampm = "오전" if hour < 12 else "오후"
    hour12 = hour % 12
    if hour12 == 0:
        hour12 = 12
    return f"{ampm} {hour12}:{minute:02d}"

def overlay_time_with_header(image_path):
    original_image = Image.open(image_path)
    now = datetime.now()

    # 헤더에 표시할 텍스트
    time_text = format_time_korean(now)
    date_text = now.strftime("%m월 %d일 %A")

    font = get_font(18)
    header_height = 40

    # 고정 배경색/텍스트색
    header_bg_color = (0, 0, 0)         # Always black
    text_color = (255, 255, 255)        # Always white

    new_width = original_image.width
    new_height = original_image.height + header_height
    new_image = Image.new("RGB", (new_width, new_height), header_bg_color)

    draw = ImageDraw.Draw(new_image)

    # 위치 계산
    time_bbox = draw.textbbox((0, 0), time_text, font=font)
    date_bbox = draw.textbbox((0, 0), date_text, font=font)

    time_y = (header_height - (time_bbox[3] - time_bbox[1])) // 2
    date_y = (header_height - (date_bbox[3] - date_bbox[1])) // 2

    draw.text((10, time_y), time_text, font=font, fill=text_color)

    date_text_width = date_bbox[2] - date_bbox[0]
    draw.text((new_width - date_text_width - 10, date_y), date_text, font=font, fill=text_color)

    new_image.paste(original_image, (0, header_height))
    new_image.save(image_path)
