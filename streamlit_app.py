import streamlit as st
import os
import tempfile
import random
from find_and_visualize import calculate_phash, parse_graphml, draw_visualization

# 页面配置
st.set_page_config(page_title="PID 图像可视化 Demo", layout="wide")
st.title("PID 图像可视化工具")

# ---------------------- 侧边栏：参数配置 ----------------------
st.sidebar.header("配置项")
perturb_value = st.sidebar.slider("Bounding Box 扰动值（像素）", 0, 20, 0, help="随机扰动标注框位置/大小")
use_example = st.sidebar.checkbox("使用示例数据（跳过上传）", True)

# ---------------------- 主区域：图片上传/处理 ----------------------
# 临时目录（处理上传文件）
temp_dir = tempfile.TemporaryDirectory()

# 1. 图片上传/示例图片加载
if use_example:
    # 示例图片（需提前放在仓库根目录）
    target_img_path = "example_target.jpg"
    match_img_path = "example_matched.jpg"  # 示例匹配图片
    graphml_path = "example_combined.graphml"  # 示例 GraphML 文件
    st.sidebar.image(target_img_path, caption="示例目标图片", width=200)
else:
    # 上传目标图片
    target_image = st.file_uploader("上传目标图片", type=["jpg", "jpeg", "png", "bmp"])
    if not target_image:
        st.warning("请上传图片或勾选「使用示例数据」")
        st.stop()
    # 保存上传的图片到临时文件
    target_img_path = os.path.join(temp_dir.name, target_image.name)
    with open(target_img_path, "wb") as f:
        f.write(target_image.getbuffer())

# 2. 计算 pHash（模拟匹配逻辑，Demo 简化为直接用示例匹配图）
st.subheader("1. 图像哈希匹配")
target_hash = calculate_phash(target_img_path)
if not target_hash:
    st.error("图片哈希计算失败！")
    st.stop()
st.success(f"目标图片哈希值：{hex(target_hash)}")
st.info("Demo 模式：直接使用预置的匹配图片（真实场景会遍历数据集匹配）")

# 3. 解析 GraphML
st.subheader("2. 解析 GraphML（节点/边信息）")
nodes, edges = parse_graphml(graphml_path)
st.success(f"解析完成：{len(nodes)} 个节点，{len(edges)} 条边")
# 展示节点示例
with st.expander("查看节点示例"):
    st.write(nodes[:3])

# 4. 生成可视化图片
st.subheader("3. 生成可视化结果")
output_path = os.path.join(temp_dir.name, "visualized_result.jpg")
draw_visualization(match_img_path, nodes, edges, output_path, perturb_value)

# 展示结果
if os.path.exists(output_path):
    st.image(output_path, caption="可视化结果（绿色=OCR/蓝色=符号/黄色=边）", width=800)
    # 提供下载
    with open(output_path, "rb") as f:
        st.download_button(
            label="下载可视化图片",
            data=f,
            file_name="pid_visualized.jpg",
            mime="image/jpeg"
        )

# 清理临时文件
temp_dir.cleanup()

# ---------------------- 附加：代码说明 ----------------------
with st.expander("查看核心代码"):
    st.code(open("find_and_visualize.py", "r").read(), language="python")
