#!/usr/bin/env python3
"""
S&P 500 择时定投 — 市场数据抓取器
--------------------------------------
运行后在同目录生成：
  - market_data.js              供 dca_calculator.html 自动填入（本地使用）
  - dca_calculator_snapshot_YYYYMMDD.html  数据内嵌版，可直接发给他人

依赖安装（仅需一次）：
    pip install yfinance

用法：
    python fetch_market_data.py
"""
import json, sys, os
from datetime import datetime

# Windows 终端默认 GBK 编码不支持 emoji，强制使用 UTF-8 输出
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

try:
    import yfinance as yf
except ImportError:
    print("❌  请先安装依赖：pip install yfinance")
    sys.exit(1)

# 脚本所在目录（与 dca_calculator.html 同级）
_DIR = os.path.dirname(os.path.abspath(__file__))


def fetch_data() -> dict:
    """从 Yahoo Finance 抓取市场数据，返回数据字典。"""
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

    return {
        "vix":           vix,
        "yield10y":      yield10y,
        "sp500_current": current,
        "sp500_ath":     ath,
        "drawdown_pct":  drawdown_pct,   # 正数，距 10 年高点回撤百分比
        "updated":       datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def write_js(data: dict) -> None:
    """将数据写入 market_data.js（供本地 dca_calculator.html 使用）。"""
    out_path = os.path.join(_DIR, "market_data.js")
    js_content = (
        "// 由 fetch_market_data.py 自动生成，请勿手动修改\n"
        f"window.MARKET_DATA = {json.dumps(data, ensure_ascii=False, indent=2)};\n"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(js_content)


def generate_snapshot(data: dict) -> None:
    """生成数据内嵌版独立 HTML，无需 market_data.js，可直接发给他人。"""
    html_src = os.path.join(_DIR, "dca_calculator.html")
    if not os.path.exists(html_src):
        print("⚠️   找不到 dca_calculator.html，跳过快照生成")
        return

    with open(html_src, "r", encoding="utf-8") as f:
        html = f.read()

    # 替换原有的 3 行数据加载块（精确字符串匹配）
    original_block = (
        "<!-- market_data.js 由 fetch_market_data.py 生成，若不存在则静默降级为手动填写模式 -->\n"
        "<script>window.MARKET_DATA = null;</script>\n"
        '<script src="market_data.js" onerror="window.MARKET_DATA=null;"></script>'
    )
    inline_block = (
        f"<!-- 数据已内嵌（由 fetch_market_data.py 于 {data['updated']} 生成） -->\n"
        f"<script>window.MARKET_DATA = {json.dumps(data, ensure_ascii=False)};</script>"
    )

    if original_block not in html:
        print("⚠️   未找到数据加载标记，快照生成跳过（HTML 结构可能已变更）")
        return

    snapshot_html = html.replace(original_block, inline_block, 1)

    date_str = datetime.now().strftime("%Y%m%d")
    out_path = os.path.join(_DIR, f"dca_calculator_snapshot_{date_str}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(snapshot_html)

    print(f"📦  快照已生成 dca_calculator_snapshot_{date_str}.html（可直接发给他人）")


def print_summary(data: dict) -> None:
    """打印数据摘要。"""
    print()
    print("✅  数据已写入 market_data.js")
    print(f"    VIX              = {data['vix']}")
    print(f"    10Y 美债收益率   = {data['yield10y']}%")
    print(f"    S&P 500 当前价   = {data['sp500_current']:,.0f}")
    print(f"    S&P 500 10年高点 = {data['sp500_ath']:,.0f}")
    print(f"    距高点回撤       = {data['drawdown_pct']:.1f}%")
    print(f"    更新时间         = {data['updated']}")
    print()
    print("👉  刷新 dca_calculator.html 即可看到自动填入的数据")


if __name__ == "__main__":
    try:
        data = fetch_data()
        write_js(data)
        print_summary(data)
        generate_snapshot(data)
    except Exception as e:
        print(f"❌  抓取失败：{e}")
        sys.exit(1)
