# 导入必要的库
import cv2
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# 定义一些全局变量
CROP_SIZE = 300  # 裁剪区域大小
SELECTED_FILE = 'CA1' # 选定的文件
padding_left = 20 # 左边距
padding_right = 20 # 右边距
text_height = 20 # 文本高度

# 打开并重新缩放图像
def open_and_rescale_images(folders):
    images = []
    for folder in folders:
        # 从文件夹中查找符合条件的图像
        image_path = [os.path.join(folder, f) for f in os.listdir(folder) if 'CA1' in f][0]
        img = Image.open(image_path)
        # 调整图像尺寸
        w_percent = 2000 / float(img.size[0])
        h_size = int(float(img.size[1]) * float(w_percent))
        img = img.resize((2000, h_size), Image.BICUBIC)
        images.append((folder, img))
    return images

# 选择矩形区域并合成图像
def choose_and_combine_squares(images):
    selected_rectangles = [(folder, (100, 100, 100+CROP_SIZE, 100+CROP_SIZE)) for folder, _ in images]
    cropped_images = []
    while True:
        for i, (folder, img) in enumerate(images):
            folder, rect = selected_rectangles[i]
            selected_rectangles[i] = (folder, draw_rectangle(cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR), rect))
            cropped_img = img.crop(selected_rectangles[i][1])
            cropped_images.append((folder, cropped_img))
            # 显示合成图像
            composite_image = combine_and_show_images(cropped_images, len_images=len(images))
            cv2.imshow('Composite Image', cv2.cvtColor(np.array(composite_image), cv2.COLOR_RGB2BGR))

            composite_image = composite_image.convert('RGB')
            cv2_image = cv2.cvtColor(np.array(composite_image), cv2.COLOR_RGB2BGR)

            # 将合成图像显示在左侧
            cv2.imshow('Composite Image', cv2_image)
            cv2.moveWindow('Composite Image', 0, 0)

        print("Press 'q' to quit or any other key to continue adjusting rectangles.")
        key = cv2.waitKey(0)
        cropped_images = []
        if key == ord('q'):
            cv2.destroyAllWindows()
            break

# 在图像上绘制矩形
def draw_rectangle(img, rect):
    # 初始化矩形参数
    rect = list(rect)
    dragging = False

    def mouse_event(event, x, y, flags, param):
        nonlocal rect, dragging
        if event == cv2.EVENT_LBUTTONDOWN:
            # 鼠标按下时开始拖拽
            rect[0], rect[1] = x - CROP_SIZE // 2, y - CROP_SIZE // 2
            rect[2], rect[3] = x + CROP_SIZE // 2, y + CROP_SIZE // 2
            dragging = True
        elif event == cv2.EVENT_MOUSEMOVE and dragging:
            # 鼠标移动时更新矩形位置
            rect[0], rect[1] = x - CROP_SIZE // 2, y - CROP_SIZE // 2
            rect[2], rect[3] = x + CROP_SIZE // 2, y + CROP_SIZE // 2
        elif event == cv2.EVENT_LBUTTONUP:
            # 鼠标释放时停止拖拽
            dragging = False

    cv2.namedWindow('Choose Region')
    cv2.setMouseCallback('Choose Region', mouse_event)

    while True:
        # 绘制矩形并显示
        img_with_rect = img.copy()
        cv2.rectangle(img_with_rect, (rect[0], rect[1]), (rect[2], rect[3]), (255, 255, 255), 2) # 线条粗细为2
        cv2.imshow('Choose Region', img_with_rect)
        # 将矩形选择窗口移动到右侧
        cv2.moveWindow('Choose Region', CROP_SIZE*2, 0)
        key = cv2.waitKey(1) & 0xFF
        if key == 27: # ESC键
            break

    cv2.destroyAllWindows()
    return tuple(rect)

# 创建合成图像
def create_composite_image(images, selected_rectangles):
    cropped_images = []
    for (folder, img), (_, rect) in zip(images, selected_rectangles):
        cropped_img = img.crop(rect)
        cropped_images.append((folder, cropped_img))

    combine_and_show_images([cropped_images])

# 合并并保存图像
def combine_and_save_images(crops, output_folder='output', len_images=0):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 填充和文本设置
    font = ImageFont.load_default()

    dummy_image = Image.new('RGB', (1, 1))
    draw_dummy = ImageDraw.Draw(dummy_image)
    max_text_width = max([draw_dummy.textlength(os.path.basename(folder), font=font) for folder, _ in crops])

    crops.sort(key=lambda x: x[0])
    width = crops[0][1].width + padding_left + padding_right + max_text_width
    composite_image = Image.new('RGB', (width, len_images * (crops[0][1].height + CROP_SIZE//10) + text_height), "white")
    draw = ImageDraw.Draw(composite_image)
    y_offset = 0
    for folder, img in crops:
        composite_image.paste(img, (padding_left, y_offset))
        draw.text((padding_left + img.width + 5, y_offset), os.path.basename(folder), fill="black", font=font)
        y_offset += img.height + CROP_SIZE//10 # 图像之间的间距

    # 保存合成图像
    composite_image.save(os.path.join(output_folder, f'region.png'))
    return composite_image

# 合并并显示图像
def combine_and_show_images(cropped_images, output_folder='output', len_images=0):
    # 类似于combine_and_save_images，但也显示图像
    composite_image = combine_and_save_images(cropped_images, output_folder, len_images)
    return composite_image

def main(metafolder):
    folders = [os.path.join(metafolder, folder) for folder in os.listdir(metafolder) if os.path.isdir(os.path.join(metafolder, folder))]
    images = open_and_rescale_images(folders)
    choose_and_combine_squares(images)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("请提供metafolder作为参数。")
        sys.exit(1)

    metafolder = sys.argv[1]
    main(metafolder)
