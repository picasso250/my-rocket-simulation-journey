# -*- coding: utf-8 -*-
"""
My Ten-Year Rocket Dream: Simple 1D Rocket Simulator v1.0

This script simulates the vertical flight of a model rocket, considering
only thrust and gravity. It does not yet account for air resistance (drag).

Author: Your Name Here
Date: 2025-12-11
"""

import matplotlib.pyplot as plt
import numpy as np

# --- 1. 参数定义 (Parameters Definition) ---
#    请根据您的 OpenRocket 设计文件修改这些值

# 物理常数 (Physical Constants)
g = 9.81  # 重力加速度 (m/s^2)

# 火箭参数 (Rocket Parameters) - <<< 在此输入您从OpenRocket获得的数据 >>>
initial_mass = 0.095  # 火箭装上发动机后的总质量 (kg)
propellant_mass = 0.024 # 发动机推进剂（燃料）的质量 (kg)
burn_time = 1.9       # 发动机工作时间 (s)
thrust = 5.0          # 发动机平均推力 (N) - Estes C6发动机的平均推力约为5N

# 模拟参数 (Simulation Parameters)
dt = 0.01  # 时间步长 (s), 减小这个值会提高精度，但会增加计算时间

# --- 2. 初始化模拟变量 (Initialize Simulation Variables) ---

# 计算衍生参数
mass_flow_rate = propellant_mass / burn_time  # 质量秒流量 (kg/s)
burnout_mass = initial_mass - propellant_mass # 燃尽后火箭的质量 (kg)

# 初始化状态变量
t = 0.0      # 时间 (s)
h = 0.0      # 高度 (m)
v = 0.0      # 速度 (m/s)
m = initial_mass # 当前质量 (kg)

# 创建列表来存储每个时间步的数据以供后续绘图
time_list = []
height_list = []
velocity_list = []
acceleration_list = []

print("--- 模拟开始 ---")
print(f"初始质量: {initial_mass:.3f} kg")
print(f"燃尽质量: {burnout_mass:.3f} kg")
print(f"发动机工作时间: {burn_time} s")

# --- 3. 模拟主循环 (Main Simulation Loop) ---

# 循环条件：只要火箭还在空中（高度大于等于0）就继续模拟
# 加上 t==0 是为了确保循环至少执行一次
while h >= 0 or t == 0:
    
    # 记录当前时刻的状态
    time_list.append(t)
    height_list.append(h)
    velocity_list.append(v)

    # 判断发动机状态并计算当前推力和质量
    if t < burn_time:
        current_thrust = thrust
        # 质量随时间线性减少
        m = initial_mass - mass_flow_rate * t
    else:
        current_thrust = 0
        m = burnout_mass

    # 计算合力 (Net Force)
    # 合力 = 推力 - 重力
    F_net = current_thrust - m * g
    
    # 根据牛顿第二定律 (F=ma) 计算加速度
    a = F_net / m
    acceleration_list.append(a)

    # 更新下一时间步的速度和高度 (欧拉积分法)
    # v_new = v_old + a * dt
    # h_new = h_old + v_old * dt
    v = v + a * dt
    h = h + v * dt

    # 时间前进
    t = t + dt

print("--- 模拟结束 ---")

# --- 4. 数据处理与分析 (Data Processing & Analysis) ---

# 将列表转换为Numpy数组以便于进行数学运算
height_array = np.array(height_list)
velocity_array = np.array(velocity_list)

# 寻找关键飞行事件
apogee_index = np.argmax(height_array) # 找到最大高度的索引
apogee_height = height_array[apogee_index]
apogee_time = time_list[apogee_index]

max_velocity = np.max(velocity_array)

print(f"发动机燃尽点 (Burnout):")
print(f"  - 时间: {burn_time:.2f} s")
print(f"  - 高度: {np.interp(burn_time, time_list, height_list):.2f} m") # 使用插值法估算燃尽时的精确高度
print(f"  - 速度: {np.interp(burn_time, time_list, velocity_list):.2f} m/s")

print(f"最高点 (Apogee):")
print(f"  - 时间: {apogee_time:.2f} s")
print(f"  - 高度: {apogee_height:.2f} m")

print(f"最大速度: {max_velocity:.2f} m/s")

# --- 5. 结果可视化 (Results Visualization) ---

plt.style.use('seaborn-v0_8-darkgrid') # 使用一个好看的绘图风格
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
fig.suptitle('一维火箭飞行模拟 (仅考虑推力和重力)', fontsize=16)

# 图1: 高度 vs. 时间
ax1.plot(time_list, height_list, 'b-', label='高度 (m)')
ax1.axvline(x=burn_time, color='r', linestyle='--', label=f'发动机燃尽 ({burn_time:.2f}s)')
ax1.plot(apogee_time, apogee_height, 'go', markersize=8, label=f'最高点 ({apogee_height:.2f}m)')
ax1.set_ylabel('高度 (m)')
ax1.legend()
ax1.grid(True)

# 图2: 速度 vs. 时间
ax2.plot(time_list, velocity_list, 'g-', label='速度 (m/s)')
ax2.axvline(x=burn_time, color='r', linestyle='--', label='发动机燃尽')
ax2.set_ylabel('速度 (m/s)')
ax2.legend()
ax2.grid(True)

# 图3: 加速度 vs. 时间
ax3.plot(time_list, acceleration_list, 'm-', label='加速度 (m/s²)')
ax3.axvline(x=burn_time, color='r', linestyle='--', label='发动机燃尽')
ax3.set_xlabel('时间 (s)')
ax3.set_ylabel('加速度 (m/s²)')
ax3.legend()
ax3.grid(True)

plt.tight_layout(rect=[0, 0, 1, 0.96])
# 解决中文显示问题，如果您的系统没有这个字体，可以换成其他支持中文的字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False 
plt.show()