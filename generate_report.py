import pandas as pd
import numpy as np
import glob
import os
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# ============ 配置 ============
HISTORICAL_DIR = "history"           # 歷史數據目錄
LATEST_PATTERN = "*.csv"             # 根目錄下所有 CSV（最新文件）
REPORT_DIR = "reports"               # 報告輸出目錄（可自行調整）
os.makedirs(REPORT_DIR, exist_ok=True)

# 讀取根目錄下最新的 CSV（排除子目錄）
all_csv = [f for f in glob.glob("*.csv")
           if os.path.isfile(f) and not f.startswith(("history", "reports"))]
if not all_csv:
    raise FileNotFoundError("根目錄下找不到 CSV 檔案")
latest_file = max(all_csv, key=os.path.getmtime)
today_str = datetime.now().strftime("%Y%m%d")

print(f"📄 當天數據：{latest_file}")

df_today = pd.read_csv(latest_file)
for col in ['PER', 'ForwardPE', 'PBR', 'ROE', 'MarketCap_B_USD', 'Sector_Avg_PER']:
    df_today[col] = pd.to_numeric(df_today[col], errors='coerce')

# ============ 讀取歷史數據（history/ 目錄） ============
hist_files = sorted(glob.glob(f"{HISTORICAL_DIR}/*.csv"))
print(f"📚 發現 {len(hist_files)} 個歷史檔案於 {HISTORICAL_DIR}/")

all_hist = []
for f in hist_files[-60:]:
    try:
        df_h = pd.read_csv(f)
        df_h['file_date'] = os.path.basename(f)
        for col in ['PER', 'ForwardPE', 'PBR', 'ROE']:
            df_h[col] = pd.to_numeric(df_h[col], errors='coerce')
        all_hist.append(df_h)
    except Exception as e:
        print(f"跳過 {f}: {e}")

df_hist = pd.concat(all_hist, ignore_index=True) if all_hist else pd.DataFrame()

# ============ 計算歷史分位數 ============
def calc_historical_percentile(ticker, metric, value):
    if df_hist.empty or pd.isna(value):
        return np.nan
    hist_vals = df_hist[df_hist['Ticker'] == ticker][metric].dropna()
    if len(hist_vals) < 5:
        return np.nan
    return (hist_vals < value).mean() * 100

# 為當天數據添加歷史分位數
df_today['PER_HistPct'] = df_today.apply(lambda r: calc_historical_percentile(r['Ticker'], 'PER', r['PER']), axis=1)
df_today['PBR_HistPct'] = df_today.apply(lambda r: calc_historical_percentile(r['Ticker'], 'PBR', r['PBR']), axis=1)

# ============ 篩選：具備安全邊際 ============
# 條件：PER < 12, ROE > 0, ForwardPE > 0, 且歷史 PER 分位 < 30%（相對自身歷史便宜）
candidates = df_today[
    (df_today['PER'] < 12) &
    (df_today['PER'].notna()) &
    (df_today['ROE'] > 0) &
    (df_today['ForwardPE'] > 0) &
    (df_today['ForwardPE'].notna())
].copy()

# 若歷史分位數可用，優先選擇歷史分位低的；否則按 PER 絕對值排序
if not df_hist.empty:
    candidates['Score'] = (
        candidates['PER_HistPct'].fillna(50) * 0.4 +   # 歷史分位越低越好
        candidates['PBR_HistPct'].fillna(50) * 0.3 +   # PBR 歷史分位越低越好
        (1 / candidates['PER']) * 100 * 0.2 +           # PER 絕對值越低越好
        candidates['ROE'] * 100 * 0.1                  # ROE 越高越好
    )
else:
    candidates['Score'] = (
        (1 / candidates['PER']) * 100 * 0.5 +
        (1 / candidates['PBR'].clip(lower=0.1)) * 10 * 0.3 +
        candidates['ROE'] * 100 * 0.2
    )

top5 = candidates.nlargest(5, 'Score')

# ============ 生成 Markdown 報告 ============
report_path = f"{REPORT_DIR}/valuation_report_{today_str}.md"

md = f"""# 📊 日經 225 估值掃描報告
**生成日期**：{datetime.now().strftime('%Y-%m-%d %H:%M')}  
**數據來源**：{os.path.basename(latest_file)}  
**歷史樣本**：{len(hist_files)} 個交易日

---

## 一、市場概況

| 指標 | 數值 |
|------|------|
| 總成分股 | {len(df_today)} 檔 |
| 有效 PER 樣本 | {df_today['PER'].notna().sum()} 檔 |
| 全樣本 PER 中位數 | {df_today['PER'].median():.2f} 倍 |
| PER > 25（高估警示） | {(df_today['PER'] > 25).sum()} 檔 ({(df_today['PER'] > 25).sum() / df_today['PER'].notna().sum() * 100:.1f}%) |
| PER < 12（安全邊際候選） | {(df_today['PER'] < 12).sum()} 檔 ({(df_today['PER'] < 12).sum() / df_today['PER'].notna().sum() * 100:.1f}%) |
| ROE < 0（虧損風險） | {(df_today['ROE'] < 0).sum()} 檔 |

---

## 二、🔥 估值過低 Top 5（具備安全邊際）

> **篩選邏輯**：PER < 12 倍、ROE > 0、Forward PE > 0，並結合歷史分位數與綜合評分排序。

"""

for i, (_, row) in enumerate(top5.iterrows(), 1):
    per_pct = f"{row['PER_HistPct']:.1f}%" if pd.notna(row['PER_HistPct']) else "N/A（歷史不足）"
    pbr_pct = f"{row['PBR_HistPct']:.1f}%" if pd.notna(row['PBR_HistPct']) else "N/A"
    md += f"""### {i}. {row['CompanyName']}（{row['Ticker']}）
| 指標 | 數值 | 備註 |
|------|------|------|
| **股價** | ¥{row['Price']:,.0f} | — |
| **PER（本益比）** | {row['PER']:.2f} 倍 | 歷史分位：{per_pct} |
| **Forward PE** | {row['ForwardPE']:.2f} 倍 | 預期盈餘方向 |
| **PBR（淨值比）** | {row['PBR']:.2f} 倍 | 歷史分位：{pbr_pct} |
| **ROE** | {row['ROE'] * 100:.2f}% | 股東權益報酬率 |
| **行業** | {row['Sector']} | 行業均值 PER：{row['Sector_Avg_PER']:.2f} |
| **市值** | {row['MarketCap_B_USD']:,.0f} 億美元 | — |

"""
    # 相對行業評估
    if row['PER'] < row['Sector_Avg_PER'] * 0.6:
        md += f"- ✅ **相對行業大幅折價**：PER 僅為行業均值 {row['Sector_Avg_PER']:.2f} 倍的 {(row['PER']/row['Sector_Avg_PER']*100):.0f}%\n"
    if row['PBR'] < 1.0:
        md += f"- ⚠️ **破淨邊緣**：PBR {row['PBR']:.2f} 倍，股價接近或低於每股淨值\n"
    md += "\n---\n\n"

# ============ 三、高風險警示區 ============
high_risk = df_today[
    ((df_today['PER'] > 50) & (df_today['PER'].notna())) |
    ((df_today['PBR'] > 10) & (df_today['PBR'].notna())) |
    ((df_today['ForwardPE'] < 0) & (df_today['ForwardPE'].notna()))
][['Ticker', 'CompanyName', 'PER', 'ForwardPE', 'PBR', 'ROE']].head(5)

md += """## 三、⚠️ 高風險警示（估值異常或盈餘惡化）

| 代碼 | 公司 | PER | Forward PE | PBR | ROE | 風險標籤 |
|------|------|-----|------------|-----|-----|----------|
"""
for _, r in high_risk.iterrows():
    tags = []
    if pd.notna(r['PER']) and r['PER'] > 50:
        tags.append("PER極高")
    if pd.notna(r['PBR']) and r['PBR'] > 10:
        tags.append("PBR極高")
    if pd.notna(r['ForwardPE']) and r['ForwardPE'] < 0:
        tags.append("預期虧損")
    md += f"| {r['Ticker']} | {r['CompanyName']} | {r['PER'] if pd.notna(r['PER']) else 'N/A'} | {r['ForwardPE'] if pd.notna(r['ForwardPE']) else 'N/A'} | {r['PBR'] if pd.notna(r['PBR']) else 'N/A'} | {r['ROE']*100 if pd.notna(r['ROE']) else 'N/A'}% | {', '.join(tags)} |\n"

md += f"""
---

## 四、使用說明

1. **歷史分位數**：低於 20% 表示當前估值處於自身歷史低位；高於 80% 表示相對昂貴。
2. **本報告僅供參考**，不構成投資建議。請結合宏觀環境、產業趨勢與公司基本面綜合判斷。
3. 前一日報告可於 `data/reports/` 目錄查閱，進行跨日比較。

---
*報告由 GitHub Action 自動生成*
"""

with open(report_path, 'w', encoding='utf-8') as f:
    f.write(md)

print(f"✅ 報告已生成：{report_path}")
print(f"📌 Top 5 低估標的：")
for _, r in top5.iterrows():
    print(f"   - {r['CompanyName']} ({r['Ticker']}): PER={r['PER']:.2f}, PBR={r['PBR']:.2f}, ROE={r['ROE']*100:.2f}%")
