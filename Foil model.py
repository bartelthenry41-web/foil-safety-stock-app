
import streamlit as st
import pandas as pd
import openpyxl as op

# 设置页面标题
st.title("Foil model：Optimal Safety Stock & OverFC% Calculator")


# 读取 Excel 文件
file_path = "Shelf Life.xlsx"
df = pd.read_excel(file_path, engine="openpyxl")

# 强制 SKU 列为字符串
df["SKU"] = df["SKU"].astype(str)

# SKU 下拉选择框：拼接 SKU 和 Description
sku_list = [f"{row['SKU']} - {row['Description']}" for _, row in df.iterrows()]
selected_option = st.selectbox("请选择 SKU", sku_list)

# 提取 SKU
selected_sku = selected_option.split(" - ")[0]

# 获取对应 SKU 数据
sku_data = df[df["SKU"] == selected_sku].iloc[0]

# 显示默认值并允许修改
st.subheader("默认值（可修改）")

lead_time = st.number_input("Lead_time（交货期）", value=float(sku_data["Lead_time"]), key="lead_time_input")
qc = float(sku_data["QC"])  # QC保持只读
order_size = st.number_input("Order_Size（一次订货量）", value=float(sku_data["Order_Size"]), key="order_size_input")

shelf_life = float(sku_data["Shelf_life"])
safety_stock_default = float(sku_data["Safety_stock"])
over_fc_default = float(sku_data["overFC%"]) / 100
safety_stock_moren = float(sku_data["Safety_stock默认"])
foil_description = sku_data["Description"]

# 显示其他信息
st.write(f"**Description（铝箔描述）**: {foil_description}")
st.write(f"**Shelf_life（总效期）**: {shelf_life}")
st.write(f"**QC（质检时间）**: {qc}")
st.write(f"**Safety_stock（安全库存推荐值）**: {safety_stock_moren}")

# 输入框和两个按钮
st.subheader("输入并计算")

col1, col2 = st.columns(2)

with col1:
    safety_stock_input = st.number_input("请输入 Safety_stock（安全库存）", value=safety_stock_default, key="safety_stock_input")
    if st.button("开始计算 ForecastBias%", key="calc_overfc"):
        denominator = lead_time + qc + safety_stock_input + order_size
        if denominator > 0:
            over_fc_calc = (shelf_life / denominator) - 1
            st.success(f"根据 Safety_stock 计算的最大 overFC%: {over_fc_calc * 100:.2f}%")
        else:
            st.error("计算错误：分母为零或负数，请检查输入值。")

with col2:
    over_fc_input_percent = st.number_input("请输入 ForecastBias%（偏差系数）", value=float(sku_data["overFC%"]), key="over_fc_input")
    over_fc_input = over_fc_input_percent / 100
    if st.button("开始计算 Safety_stock", key="calc_safety_stock"):
        numerator = shelf_life / (1 + over_fc_input)
        safety_stock_calc = numerator - (lead_time + qc + order_size)
        st.success(f"根据 ForecastBias% 计算的最长 Safety_stock: {safety_stock_calc:.2f}")

# 显示公式提示
st.caption("公式: Shelf_life = (Lead_time + QC + Safety_stock + Order_Size) × (1 + ForecastBias%)")

import numpy as np
import matplotlib.pyplot as plt

st.subheader("Safety Stock 与 ForecastBias% 的关系图")
# 生成 ForecastBias% 范围
bias_range = np.arange(-0.5, 0.5, 0.05)  # -0.50% 到 50%
safety_stock_values = [shelf_life / (1 + b) - (lead_time + qc + order_size) for b in bias_range]

# 绘制折线图
fig, ax = plt.subplots()
ax.plot(bias_range * 100, safety_stock_values, marker='o')
ax.set_xlabel("ForecastBias%")
ax.set_ylabel("Safety Stock")
ax.set_title("Safety Stock vs ForecastBias%")
ax.grid(True)

st.pyplot(fig)


