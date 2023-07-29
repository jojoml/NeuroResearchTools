import cv2
import tqdm
import sys
import os
import csv
import numpy as np

from PIL import Image
from tifffile import imread

# 辅助函数，用于保存图像并打印输出路径
def save_and_open(img, output_path):
    cv2.imwrite(output_path, img)
    print(f"已将处理后的图像保存到: {output_path}")

# 主函数，用于处理图像
def process_image(image_path, connected_comp_threshold):
    # 读取图像，检查它是tif还是其他图像格式
    if image_path.endswith('.tif'):
        image = imread(image_path)
    else:
        image = cv2.imread(image_path)

    # 如果图像在任一维度上大于1500像素，则调整其大小
    if image.shape[0] > 1500 or image.shape[1] > 1500:
        scale = 1500 / max(image.shape[:2])
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    # 将图像分割成蓝色、绿色和红色通道
    blue_channel, green_channel, red_channel = cv2.split(image)
    
    # 将红色通道中的零强度像素改为非零像素的平均强度
    red_channel[red_channel==0] = int(np.mean(red_channel[red_channel>0]))

    # 对红色和蓝色通道应用自适应阈值
    thresh_red = cv2.adaptiveThreshold(red_channel, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 55, -31)
    thresh_blue = cv2.adaptiveThreshold(blue_channel, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 55, -21)

    # 合并红色和蓝色通道的掩码，并将其应用到图像上
    combined_mask = cv2.bitwise_and(thresh_blue, thresh_red)
    masked_img = cv2.bitwise_and(image, image, mask=combined_mask)
    img_with_stars = image.copy()

    # 获取掩码中的连通分量，并计算其数量超过一定大小的连通分量
    num_labels, _, stats, _ = cv2.connectedComponentsWithStats(combined_mask)

    count = 0
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] >= connected_comp_threshold:
            count += 1
            x = int(stats[i, cv2.CC_STAT_LEFT] + stats[i, cv2.CC_STAT_WIDTH] / 2)
            y = int(stats[i, cv2.CC_STAT_TOP] + stats[i, cv2.CC_STAT_HEIGHT] / 2)
            cv2.drawMarker(img_with_stars, (x, y), (255, 255, 255), markerType=cv2.MARKER_STAR, markerSize=4, thickness=1)

    # 垂直堆叠处理后的图像
    stacked_img = np.vstack((img_with_stars, image, masked_img))

    return stacked_img, count

# 函数用于计算灰度图像中非零像素的数量
def calculate_grayscale_non_zero_pixels(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    non_zero_pixels = cv2.countNonZero(image)
    return non_zero_pixels

# 函数用于处理文件夹中的所有图像
def process_all_images_in_folder(folder_path, csv_writer):
    # 需要处理的图像扩展名列表
    image_extensions = [".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"]

    # 遍历文件夹中的所有文件
    for file in os.listdir(folder_path):
        # 跳过隐藏文件
        if file[0] == '.':
            continue

        file_path = os.path.join(folder_path, file)
        file_extension = os.path.splitext(file)[1].lower()

        # 检查文件是否为图像
        if file_extension in image_extensions:
            # 计算灰度图像中的非零像素数量
            non_zero_pixels = calculate_grayscale_non_zero_pixels(file_path)
            print(f"正在处理图像: {file_path}，其中非零像素为{non_zero_pixels}个")

            # 遍历不同的阈值
          # 这里可以自己设置阈值 阈值代表联通量的像素数
            for threshold in range(5, 11):
                # 处理图像并保存输出
                processed_image, connected_components_count = process_image(file_path, threshold)
                dirname = os.path.dirname(file_path)
                output_path = os.path.join(dirname, "results")
                os.makedirs(output_path, exist_ok=True)
                output_path = os.path.join(output_path, os.path.basename(file_path) + f"_threshold_{threshold}.png")
                save_and_open(processed_image, output_path)

                # 将数据写入csv文件
                csv_writer.writerow({
                    "image_name": dirname,
                    "region_name": os.path.basename(file_path),
                    "threshold": threshold,
                    "connected_components": connected_components_count,
                    "non_zero_pixels": non_zero_pixels
                })


if __name__ == "__main__":
    # 验证命令行参数数量
    if len(sys.argv) < 3:
        print("使用方式: python process_images.py <folder_path> <output_csv_file>")
        sys.exit()

    folder_path = sys.argv[1]
    output_csv_file = sys.argv[2]

    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"文件夹 '{folder_path}' 不存在!")
        sys.exit()

    # 创建csv文件
    csvfile = open(output_csv_file, "w", newline='')
    fieldnames = ["image_name", "region_name", "threshold", "connected_components", "non_zero_pixels"]
    csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    csv_writer.writeheader()

    # 遍历文件夹处理所有图像
    for folder in tqdm.tqdm(os.listdir(folder_path)):
        if os.path.isdir(os.path.join(folder_path, folder)):
            process_all_images_in_folder(os.path.join(folder_path, folder), csv_writer)

    csvfile.close()
