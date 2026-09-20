# RayCon-SLAM — Public Trajectory Utilities

功能受限的外围演示：回放已给定的平面里程计增量并导出轨迹。没有图像或 IMU 输入，不执行视觉跟踪、视觉惯性初始化、地图优化或回环；不是完整 RayCon-SLAM 系统。

## 运行

需要 Python 3.10 或更新版本，无第三方依赖。在本目录执行：

```bash
bash run.sh
python3 -B -m unittest discover -s tests -v
```

自定义输入：

```bash
python3 -B src/trajectory.py --input data/odometry.csv --output result/custom-run
```

`--output` 指定尚不存在的目录；省略时自动创建 `result/` 下的新时间目录。

## 数据与坐标约定

`data/odometry.csv` 是手写的理想正方形行走序列，不是传感器日志或论文轨迹。列为 `timestamp,dx_body_m,dy_body_m,dyaw_rad`。

- 时间戳以秒为单位，必须严格递增；样例从零秒开始，不代表真实日期。
- 首行是初始时刻，三个增量必须为零；初始位置和航向均为零。
- 每一后续行的平移是在上一时刻机体坐标系下表达的相邻位姿平移，单位米；不是速度，也不乘采样时长。
- 先用上一时刻航向将平移转到世界坐标，再更新当前航向。航向增量用弧度，绕竖直轴逆时针为正。
- 这是右手平面坐标系，水平两轴表示机体向前和向左，竖直轴向上；并非光学相机坐标系。输出高度为零。
- 输出平移是机体原点在世界中的位置；输出四元数表示机体到世界的旋转，顺序为 `qx qy qz qw`。

## 实际流程与文件

1. 校验首行、数值有限性和时间顺序。
2. 组合给定平移与航向增量。
3. 导出 CSV、TUM 文本及路径统计。

| 文件 | 含义 |
| --- | --- |
| `src/trajectory.py` | 平面轨迹组合和命令行入口 |
| `run.sh` | 合成数据快捷入口，可转发参数 |
| `tests/test_trajectory.py` | 机体系平移、轨迹闭合及输入校验 |
| `result/<运行目录>/trajectory.csv` | 带列名的逐时刻位姿 |
| `result/<运行目录>/trajectory.tum` | `timestamp tx ty tz qx qy qz qw` 文本 |
| `result/<运行目录>/summary.json` | 位姿数量、时间跨度、路程及末端位置统计 |

默认样例产生 9 个位姿，路程为 8 米，末端回到起点附近，浮点误差可能留下极小非零数。这里的闭合由给定的合成增量决定，不是回环检测结果。没有真实参考轨迹，不计算 ATE 或论文精度指标。
