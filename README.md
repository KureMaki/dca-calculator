# S&P 500 量化择时定投工具

基于席勒 CAPE、股权风险溢价（ERP）、VIX 恐慌指数、距前高回撤四个维度，对标普500定投节奏进行动态调整的量化策略工具集。

---

## 功能概览

### 📊 定投参数计算器 (`dca_calculator.html`)

无需安装，直接用浏览器打开的单文件工具。

计算器分两个 Tab：

**📊 定投计算器 Tab**
- **参数设置**：输入本金、现金底线、定投频率（月/双周/周/日），以及"希望几年布局完"（3/5★/7/10/15年），自动换算每月执行金额 Z
- **信号速查表**：根据当前参数实时生成 7 档操作金额对照表
- **当前信号判断**：VIX / 10Y 收益率 / 回撤自动填入，手动输入 CAPE，ERP 自动计算，即时给出操作建议和金额
- **货币切换**：支持人民币 / 美元显示

**⚙️ 策略后台 Tab**
- **动态逻辑总览**：以可视化图展示完整判断流程（减仓路径 + 买入路径），随参数修改实时更新
- **全参数可调**：所有判断阈值（CAPE 三条线、ERP 阈值、VIX、回撤）和操作倍数均可修改，改完立即反映到计算器
- **持久化保存**：点击「💾 保存设置」将参数存入浏览器本地，下次打开自动恢复；「↺ 恢复默认值」一键清除

### 🐍 实时数据抓取脚本 (`fetch_market_data.py`)

从 Yahoo Finance 拉取最新市场数据，写入 `market_data.js`，供计算器自动读取。

---

## 文件结构

```
dca-calculator/
├── README.md
├── .gitignore
└── dca-calculator/              # 📊 DCA 择时计算器
    ├── dca_calculator.html      #   计算器主文件，直接浏览器打开
    ├── fetch_market_data.py     #   市场数据抓取脚本
    ├── strategy_handbook.md     #   策略完整说明文档
    ├── requirements.txt         #   Python 依赖（yfinance）
    └── 刷新数据.bat              #   Windows 一键抓取快捷方式
```

> `dca-calculator/market_data.js` 为本地运行脚本后自动生成，已加入 `.gitignore`，不纳入版本控制。

---

## 快速开始

### 第一步：安装 Python 依赖（仅需一次）

```bash
pip install -r dca-calculator/requirements.txt
```

### 第二步：抓取最新市场数据

```bash
python dca-calculator/fetch_market_data.py
```

Windows 用户也可以直接双击 `dca-calculator/刷新数据.bat`。

运行成功后会输出：

```
✅ 数据已写入 market_data.js
   VIX              = 17.2
   10Y 美债收益率   = 4.42%
   S&P 500 当前价   = 5,831
   距高点回撤       = 0.0%
   更新时间         = 2026-05-15 09:30
```

### 第三步：打开计算器

用浏览器打开 `dca_calculator.html`，数据自动填入，输入 CAPE 值即可获得当前操作建议。

> **CAPE 查询**：每日访问 [multpl.com/shiller-pe](https://www.multpl.com/shiller-pe) 手动填入。CAPE 每日更新，建议每次使用前确认最新值。

---

## 策略逻辑简介

### 核心思路

"平时装死赚慢钱，高位定卖收子弹，Y×X底线不能碰，股灾一出干满仓"

### 四维信号体系

| 指标 | 作用 |
|------|------|
| CAPE（席勒市盈率） | 判断市场整体估值高低 |
| ERP（股权风险溢价）= 1/CAPE − 10Y收益率 | 相对无风险资产的性价比 |
| VIX（恐慌指数） | 市场短期情绪 |
| S&P 500 距前高回撤 | 实际下跌幅度 |

### 七档操作体系

| 档位 | 触发条件 | 操作 |
|------|----------|------|
| 暂停·撤退 | AND触发 + CAPE > 44 | 卖出 1.5Z |
| 暂停·轻减 | AND触发 + CAPE 41–44 | 卖出 1Z |
| 缓投 | AND触发 + CAPE 38–41 | 买入 0.5Z |
| 正常定投 | 无特殊信号 | 买入 1Z |
| 加仓 A | 弱买入信号 | 买入 2Z |
| 加仓 B | 中强信号 | 买入 4Z |
| 满仓 | 强信号共振 | 买入 6Z |

> AND 条件：CAPE > 38 **且** ERP < −1%，两者同时满足才触发减仓路径。

详细策略说明见 [`dca-calculator/strategy_handbook.md`](./dca-calculator/strategy_handbook.md)。

---

## 免责声明

本工具及策略手册仅供个人学习和研究参考，不构成任何投资建议。投资有风险，决策需谨慎。
