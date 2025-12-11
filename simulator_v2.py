# -*- coding: utf-8 -*-
"""
My Ten-Year Rocket Dream: Simple 1D Rocket Simulator v2.0

This version adds a crucial element of realism: Air Drag.
The simulation results should now be much closer to OpenRocket.

Author: Your Name Here
Date: 2025-12-11
"""

import matplotlib.pyplot as plt
import numpy as np

# --- 1. 参数定义 (Parameters Definition) ---

# 物理常数 (Physical Constants)
g = 9.81      # 重力加速度 (m/s^2)
rho = 1.225   # 海平面空气密度 (kg/m^3)

# 火箭参数 (Rocket Parameters) - <<< 在此输入您从OpenRocket获得的数据 >>>
initial_mass = 0.095  # 火箭装上发动机后的总质量 (kg)
propellant_mass = 0.024 # 发动机推进剂（燃料）的质量 (kg)
burn_time = 1.9       # 发动机工作时间 (s)
thrust = 5.0          # 发动机平均推力 (N)

# 空气动力学参数 (Aerodynamics Parameters) - <<< 在此输入 >>>
rocket_diameter = 0.05 # 箭体直径 (m)
C_d = 0.55             # 阻力系数 (从OpenRocket图表中估算的平均值)

# 模拟参数 (Simulation Parameters)
dt = 0.01  # 时间步长 (s)

# --- 2. 初始化模拟变量 (Initialize Simulation Variables) ---

# 计算衍生参数
mass_flow_rate = propellant_mass / burn_time
burnout_mass = initial_mass - propellant_mass
A = np.pi * (rocket_diameter / 2)**2 # 火箭横截面积 (m^2)

# 初始化状态变量
t = 0.0
h = 0.0
v = 0.0
m = initial_mass

# 创建列表存储数据
time_list, height_list, velocity_list, acceleration_list = [], [], [], []

print("--- 模拟开始 (V2 - 包含空气阻力) ---")
print(f"阻力系数 (Cd): {C_d}")
print(f"横截面积 (A): {A:.5f} m^2")

# --- 3. 模拟主循环 (Main Simulation Loop) ---

while h >= 0 or t == 0:
    time_list.append(t)
    height_list.append(h)
    velocity_list.append(v)

    if t < burn_time:
        current_thrust = thrust
        m = initial_mass - mass_flow_rate * t
    else:
        current_thrust = 0
        m = burnout_mass

    # === 物理核心升级: 计算空气阻力 ===
    # F_drag = 0.5 * rho * v^2 * Cd * A
    # v**2 会丢失速度的方向信息，所以我们用 v * abs(v) 来保留方向
    # 或者用 np.sign(v) 在最后修正方向
    F_drag = 0.5 * rho * (v**2) * C_d * A
    
    # 计算合力 (Net Force)
    # 合力 = 推力 - 重力 - 阻力 (阻力方向与速度相反)
    F_net = current_thrust - m * g - (F_drag * np.sign(v))
    
    # 计算加速度
    a = F_net / m
    acceleration_list.append(a)

    # 更新速度和高度
    v = v + a * dt
    h = h + v * dt

    # 时间前进
    t = t + dt

print("--- 模拟结束 ---")

# --- 4. 数据处理与分析 (Data Processing & Analysis) ---

height_array = np.array(height_list)
apogee_index = np.argmax(height_array)
apogee_height = height_array[apogee_index]
apogee_time = time_list[apogee_index]

print(f"最高点 (Apogee):")
print(f"  - 时间: {apogee_time:.2f} s")
print(f"  - 高度: {apogee_height:.2f} m") # <--- 对比这个值与OpenRocket的结果

# --- 5. 结果可视化 (Results Visualization) ---

plt.style.use('seaborn-v0_8-darkgrid')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
fig.suptitle('一维火箭飞行模拟 (包含空气阻力)', fontsize=16)

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
ax2.set_xlabel('时间 (s)')
ax2.set_ylabel('速度 (m/s)')
ax2.legend()
ax2.grid(True)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False 
plt.show()