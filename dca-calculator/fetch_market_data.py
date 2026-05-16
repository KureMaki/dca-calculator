#!/usr/bin/env python3
"""
S&P 500 择时定投 — 市场数据抓取器
--------------------------------------
运行后在同目录生成 market_data.js，供 dca_calculator.html 自动填入
VIX / 10 年期美债收益率 / S&P 500 回撤 三项实时数据

依赖安装（仅需一次）：
    pip install yfinance

用法：
    python fetch_market_data.py
"""
import json, sys, os
from datetime import datetime

try:
    import yfinance as yf
except ImportError:
    print("❌  请先安装依赖：pip install yfinance")
    sys.exit(1)


def fetch():
    print("正在从 Yahoo Finance 抓取市场数据…")

    # ── VIX ──────────────────────────────────────────────────────
    vix_hist = yf.Ticker("^VIX").history(period="5d")
    if vix_hist.empty:
        raise RuntimeError("VIX 数据获取失败，请检查网络")
    vix = round(float(vix_hist["Close"].iloc[-1]), 2)

    # ── 10 年期美债收益率（^TNX，单位已是 % ，如 4.42）──────────
    tnx_hist = yf.Ticker("^TNX").history(period="5d")
    if tnx_hist.empty:
        raise RuntimeError("10Y Treasury 数据获取失败，请检查网络")
    yield10y = round(float(tnx_hist["Close"].iloc[-1]), 2)

    # ── S&P 500：当前价 + 近 10 年高点（作为 ATH 近似）──────────
    gspc = yf.Ticker("^GSPC")
    hist = gspc.history(period="10y")
    if hist.empty:
        raise RuntimeError("S&P 500 数据获取失败，请检查网络")
    current = round(float(hist["Close"].iloc[-1]), 2)
    ath     = round(float(hist["Close"].max()), 2)
    drawdown_pct = round(max(0.0, (ath - current) / ath * 100), 2)

    data = {
        "vix":          vix,
        "yield10y":     yield10y,
        "sp500_current": current,
        "sp500_ath":    ath,
        "drawdown_pct": drawdown_pct,   # 正数，距 10 年高点回撤百分比
        "updated":      datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    # ── 写入 market_data.js（与本脚本同目录）─────────────────────
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "market_data.js")
    js_content = (
        "// 由 fetch_market_data.py 自动生成，请勿手动修改\n"
        f"window.MARKET_DATA = {json.dumps(data, ensure_ascii=False, indent=2)};\n"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(js_content)

    # ── 控制台摘要 ────────────────────────────────────────────────
    print()
    print("✅  数据已写入 market_data.js")
    print(f"    VIX              = {vix}")
    print(f"    10Y 美债收益率   = {yield10y}%")
    print(f"    S&P 500 当前价   = {current:,.0f}")
    print(f"    S&P 500 10年高点 = {ath:,.0f}")
    print(f"    距高点回撤       = {drawdown_pct:.1f}%")
    print(f"    更新时间         = {data['updated']}")
    print()
    print("👉  刷新 dca_calculator.html 即可看到自动填入的数据")


if __name__ == "__main__":
    try:
        fetch()
    except Exception as e:
        print(f"❌  抓取失败：{e}")
        sys.exit(1)
