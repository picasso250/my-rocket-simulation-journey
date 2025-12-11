# -*- coding: utf-8 -*-
"""
My Ten-Year Rocket Dream: 2D Rigid Body Rocket Simulator v3.0

This version elevates the simulation from a 1D point mass to a 2D rigid body.
It introduces rotational dynamics to simulate the rocket's attitude (angle).
We will use this to observe the rocket's passive stability.

Author: Your Name Here
Date: 2025-12-11
"""

import matplotlib.pyplot as plt
import numpy as np

# --- 1. 参数定义 (Parameters Definition) ---

# 物理常数
g = 9.81
rho = 1.225

# === 火箭参数 (从OpenRocket组件分析中获得) ===
# 发射总质量 (kg)
initial_mass = 0.931
# 俯仰/偏航轴的转动惯量 (kg*m^2)
moment_of_inertia_I = 0.22 # <<< 使用这个基于物理估算的、更合理的值
# 重心到压心的距离 (m). (CP - CG)
cg_to_cp_distance = 0.1005

# === 发动机参数 (从发动机型号和仿真图中获得) ===
# 燃料质量 (kg) -> !!!请查找发动机手册确认此值!!!
propellant_mass = 0.0985 # <--- 建议核对
# 发动机平均推力 (N)
thrust = 78.0
# 发动机燃烧时间 (s)
burn_time = 2.5

# === 空气动力学参数 ===
# 火箭最大直径 (m)
rocket_diameter = 0.09
# 平均阻力系数 -> !!!建议从仿真导出数据获得更精确的值!!!
C_d = 0.58             # <--- 建议核对

# 模拟设置
dt = 0.01
initial_angle_deg = 2.0 # 建议从一个较小的初始角度开始测试

# --- 2. 初始化模拟变量 ---

# 衍生参数
mass_flow_rate = propellant_mass / burn_time
burnout_mass = initial_mass - propellant_mass
A = np.pi * (rocket_diameter / 2)**2

# 初始化6个状态变量
x, y = 0.0, 0.0
vx, vy = 0.0, 0.0
theta = np.radians(initial_angle_deg) # 将角度转换为弧度
omega = 0.0

m = initial_mass
t = 0.0

# 初始化数据记录列表
time_l, x_l, y_l, vx_l, vy_l, theta_l, omega_l = [], [], [], [], [], [], []

print("--- 模拟开始 (V3 - 2D刚体动力学) ---")
print(f"转动惯量 (I): {moment_of_inertia_I} kg*m^2")
print(f"CG-CP 距离: {cg_to_cp_distance * 100:.1f} cm")
print(f"初始发射角: {initial_angle_deg} 度")

# --- 3. 模拟主循环 ---
while y >= 0 or t == 0:
    # 记录状态
    time_l.append(t); x_l.append(x); y_l.append(y)
    vx_l.append(vx); vy_l.append(vy)
    theta_l.append(np.degrees(theta)); omega_l.append(np.degrees(omega))

    # 更新推力和质量
    if t < burn_time:
        current_thrust = thrust
        m = initial_mass - mass_flow_rate * t
    else:
        current_thrust = 0
        m = burnout_mass

    # --- 物理核心：力和力矩计算 ---

    # 1. 计算合力 (Vector Sum of Forces)
    # 推力 (Thrust) - 作用于箭体方向
    Tx = current_thrust * np.sin(theta)
    Ty = current_thrust * np.cos(theta)
    
    # 重力 (Gravity) - 永远指向-y方向
    Fg_y = -m * g
    
    # 空气阻力 (Drag) - 作用于速度的反方向
    v_mag = np.sqrt(vx**2 + vy**2)
    F_drag = 0.5 * rho * v_mag**2 * C_d * A
    
    drag_Fx, drag_Fy = 0, 0
    if v_mag > 1e-6: # 避免除以零
        drag_Fx = -F_drag * (vx / v_mag)
        drag_Fy = -F_drag * (vy / v_mag)
        
    F_net_x = Tx + drag_Fx
    F_net_y = Ty + Fg_y + drag_Fy
    
    # 2. 计算合力矩 (Net Torque)
    # 空气动力产生的恢复力矩
    velocity_angle = np.arctan2(vx, vy)
    alpha = theta - velocity_angle # 攻角 = 箭体角 - 速度角
    
    # 这个力矩是让火箭保持稳定的关键
    torque = -F_drag * cg_to_cp_distance * np.sin(alpha)
    
    # 3. 计算加速度 (Linear & Angular)
    ax = F_net_x / m
    ay = F_net_y / m
    alpha_ang = torque / moment_of_inertia_I # 角加速度

    # 4. 更新状态 (Euler Integration)
    vx += ax * dt
    vy += ay * dt
    x += vx * dt
    y += vy * dt
    
    omega += alpha_ang * dt
    theta += omega * dt
    
    t += dt

print("--- 模拟结束 ---")
apogee_height = np.max(y_l)
print(f"最高点 (Apogee): {apogee_height:.2f} m")

# --- 4. 结果可视化 ---

plt.style.use('seaborn-v0_8-darkgrid')
fig = plt.figure(figsize=(12, 8))
fig.suptitle(f'二维火箭飞行模拟 (初始倾角 {initial_angle_deg}°)', fontsize=16)

# 图1: 飞行弹道 (Y vs X)
ax1 = plt.subplot(2, 2, 1)
ax1.plot(x_l, y_l)
ax1.set_title("飞行弹道")
ax1.set_xlabel("水平距离 (m)")
ax1.set_ylabel("高度 (m)")
ax1.axis('equal')
ax1.grid(True)

# 图2: 姿态角 vs. 时间
ax2 = plt.subplot(2, 2, 2)
ax2.plot(time_l, theta_l, label='姿态角 (度)')
ax2.axvline(x=burn_time, color='r', linestyle='--', label='发动机燃尽')
ax2.set_title("姿态角变化")
ax2.set_xlabel("时间 (s)")
ax2.set_ylabel("角度 (度)")
ax2.legend()
ax2.grid(True)

# 图3&4: 速度分量 vs. 时间
ax3 = plt.subplot(2, 2, 3)
ax3.plot(time_l, vy_l, label='垂直速度 Vy (m/s)')
ax3.plot(time_l, vx_l, label='水平速度 Vx (m/s)')
ax3.set_title("速度分量")
ax3.set_xlabel("时间 (s)")
ax3.set_ylabel("速度 (m/s)")
ax3.legend()
ax3.grid(True)

# 图4: 角速度 vs. 时间
ax4 = plt.subplot(2, 2, 4)
ax4.plot(time_l, omega_l, label='角速度 (度/s)')
ax4.set_title("角速度变化")
ax4.set_xlabel("时间 (s)")
ax4.set_ylabel("角速度 (度/s)")
ax4.legend()
ax4.grid(True)


plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False 
plt.show()