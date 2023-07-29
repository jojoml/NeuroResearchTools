# 红蓝共定位分析python script

需要首先安装python 然后安装python的库依赖
## 依赖

该脚本需要以下的库：

- OpenCV
- numpy
- csv
- PIL
- tifffile

您可以通过运行以下命令来安装这些库：

```shell
pip install opencv-python numpy pillow tifffile
```

## 使用方法

您可以通过命令行参数来运行该脚本：

```shell
python process_images.py <folder_path> <output_csv_file>
```

其中：

- `<folder_path>` 是要处理的图像的文件夹路径。
目录结构为:
```shell
folder
--image_folder1
----image1.jpg
----image2.jpg
--image_folder2
....
```
- `<output_csv_file>` 是将要写入的输出 CSV 文件名。

脚本将遍历 `<folder_path>` 中的所有子文件夹，并将结果写入指定的 CSV 文件。
并且在每个image对应的文件夹中生成对应的image可视化result

## 输出

脚本的输出为一个 CSV 文件，其中包含以下字段：

- `image_name`: 包含图像的文件夹名称
- `region_name`: 图像文件的名称
- `threshold`: 用于图像处理的阈值
- `connected_components`: 在图像中发现的连通组件的数量
- `non_zero_pixels`: 灰度图像中非零像素的数量

CSV 文件中的每一行都对应于一个处理过的图像。

除了 CSV 文件，脚本还会在原始图像所在文件夹的 "results" 子文件夹中保存处理过的图像。每个处理过的图像都会以与原始图像相同的名称保存，后缀为用于处理的阈值。


