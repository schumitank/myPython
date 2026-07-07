import yfinance as yf
import pandas as pd
import numpy as np
import os
import shutil
import time
from datetime import datetime, timedelta

tickers = ["4151.T"
,"4502.T"
,"4503.T"
,"4506.T"
,"4507.T"
,"4519.T"
,"4523.T"
,"4568.T"
,"4578.T"
,"285A.T"
,"4062.T"
,"6479.T"
,"6501.T"
,"6503.T"
,"6504.T"
,"6506.T"
,"6526.T"
,"6645.T"
,"6701.T"
,"6702.T"
,"6723.T"
,"6724.T"
,"6752.T"
,"6753.T"
,"6758.T"
,"6762.T"
,"6770.T"
,"6841.T"
,"6857.T"
,"6861.T"
,"6902.T"
,"6920.T"
,"6954.T"
,"6963.T"
,"6971.T"
,"6976.T"
,"6981.T"
,"7735.T"
,"7751.T"
,"7752.T"
,"8035.T"
,"543A.T"
,"7201.T"
,"7202.T"
,"7203.T"
,"7211.T"
,"7261.T"
,"7267.T"
,"7269.T"
,"7270.T"
,"7272.T"
,"4543.T"
,"4902.T"
,"6146.T"
,"7731.T"
,"7733.T"
,"7741.T"
,"9432.T"
,"9433.T"
,"9434.T"
,"9984.T"
,"5831.T"
,"7186.T"
,"8304.T"
,"8306.T"
,"8308.T"
,"8309.T"
,"8316.T"
,"8331.T"
,"8354.T"
,"8411.T"
,"8253.T"
,"8591.T"
,"8697.T"
,"8601.T"
,"8604.T"
,"8630.T"
,"8725.T"
,"8750.T"
,"8766.T"
,"8795.T"
,"1332.T"
,"2002.T"
,"2269.T"
,"2282.T"
,"2501.T"
,"2502.T"
,"2503.T"
,"2801.T"
,"2802.T"
,"2871.T"
,"2914.T"
,"3086.T"
,"3092.T"
,"3099.T"
,"3382.T"
,"7453.T"
,"7532.T"
,"8233.T"
,"8252.T"
,"8267.T"
,"9843.T"
,"9983.T"
,"2413.T"
,"2432.T"
,"3659.T"
,"3697.T"
,"4307.T"
,"4324.T"
,"4385.T"
,"4661.T"
,"4689.T"
,"4704.T"
,"4751.T"
,"4755.T"
,"6098.T"
,"6178.T"
,"6532.T"
,"7974.T"
,"9602.T"
,"9735.T"
,"9766.T"
,"1605.T"
,"3401.T"
,"3402.T"
,"3861.T"
,"3405.T"
,"3407.T"
,"4004.T"
,"4005.T"
,"4021.T"
,"4042.T"
,"4043.T"
,"4061.T"
,"4063.T"
,"4183.T"
,"4188.T"
,"4208.T"
,"4452.T"
,"4901.T"
,"4911.T"
,"6988.T"
,"5019.T"
,"5020.T"
,"5101.T"
,"5108.T"
,"5201.T"
,"5214.T"
,"5233.T"
,"5301.T"
,"5332.T"
,"5333.T"
,"5401.T"
,"5406.T"
,"5411.T"
,"3436.T"
,"5706.T"
,"5711.T"
,"5713.T"
,"5714.T"
,"5801.T"
,"5802.T"
,"5803.T"
,"2768.T"
,"8001.T"
,"8002.T"
,"8015.T"
,"8031.T"
,"8053.T"
,"8058.T"
,"1721.T"
,"1801.T"
,"1802.T"
,"1803.T"
,"1808.T"
,"1812.T"
,"1925.T"
,"1928.T"
,"1963.T"
,"5631.T"
,"6103.T"
,"6113.T"
,"6273.T"
,"6301.T"
,"6302.T"
,"6305.T"
,"6326.T"
,"6361.T"
,"6367.T"
,"6471.T"
,"6472.T"
,"6473.T"
,"7004.T"
,"7011.T"
,"7013.T"
,"7012.T"
,"7832.T"
,"7911.T"
,"7912.T"
,"7951.T"
,"3289.T"
,"8801.T"
,"8802.T"
,"8804.T"
,"8830.T"
,"9001.T"
,"9005.T"
,"9007.T"
,"9008.T"
,"9009.T"
,"9020.T"
,"9021.T"
,"9022.T"
,"9064.T"
,"9147.T"
,"9101.T"
,"9104.T"
,"9107.T"
,"9201.T"
,"9202.T"
,"9501.T"
,"9502.T"
,"9503.T"
,"9531.T"
,"9532.T"]

data_list = []

for ticker in tickers:
    stock = yf.Ticker(ticker)
    info = stock.info

    # 提取所需的基础财务指标
    data = {
        "Ticker": ticker.replace(".T", ""),
        "CompanyName": info.get("shortName", "N/A"),
        "Sector": info.get("sector", "N/A"),
        "Industry": info.get("industry", "N/A"),
        "Price": info.get("currentPrice", np.nan),
        "PER": info.get("trailingPE", np.nan),
        "ForwardPE": info.get("forwardPE", np.nan),
        "PBR": info.get("priceToBook", np.nan),
        "ROE": info.get("returnOnEquity", np.nan),
        "MarketCap_B_USD": info.get("marketCap", 0) / 1e9
    }
    data_list.append(data)
    print(f"Processed: {ticker}")

df = pd.DataFrame(data_list)


# 3. core calculation: calculate average PER
def add_sector_benchmarks(df):
    # 将 'N/A' 或 np.nan 视为有效数值前的处理：只对数值列计算平均
    # 仅保留有效行业分组
    valid_df = df[df['Sector'] != 'N/A'].copy()

    # 计算每个 Sector 的平均 PER (忽略 NaN)
    sector_means = valid_df.groupby('Sector')['PER'].mean().reset_index()
    sector_means.rename(columns={'PER': 'Sector_Avg_PER'}, inplace=True)

    # 将行业平均值合并回主表
    df = pd.merge(df, sector_means, on='Sector', how='left')

    # 四舍五入保留两位小数
    df['Sector_Avg_PER'] = df['Sector_Avg_PER'].round(2)
    return df


df = add_sector_benchmarks(df)

# 1. 定义文件名
main_file = "Nikkei225_Live_Data.csv"
history_dir = "history"

# 2. 确保 history 目录存在
if not os.path.exists(history_dir):
    os.makedirs(history_dir)

# 3. 生成带日期的备份文件名 (例如: Nikkei225_Live_Data_2026-07-07.csv)
date_str = datetime.now().strftime("%Y-%m-%d")
backup_file = os.path.join(history_dir, f"Nikkei225_Live_Data_{date_str}.csv")

# 4. 保存主文件 (latest)
df.to_csv(main_file, index=False)

# 5. 复制一份到 history 目录作为备份
shutil.copy2(main_file, backup_file)

print(f"数据已更新: {main_file}")
print(f"备份已创建: {backup_file}")


# 6. 自动清理 30 天以前的历史备份文件
def clean_old_backups(history_dir, days_to_keep=30):
    now = time.time()
    # 计算 30 天前的截止时间戳
    cutoff_time = now - (days_to_keep * 86400)

    for filename in os.listdir(history_dir):
        file_path = os.path.join(history_dir, filename)

        # 确保只删除文件（避免误删文件夹）
        if os.path.isfile(file_path):
            # 获取文件最后修改时间
            file_mtime = os.path.getmtime(file_path)

            if file_mtime < cutoff_time:
                os.remove(file_path)
                print(f"已清理过期备份: {filename}")


# 执行清理
clean_old_backups(history_dir, days_to_keep=30)

# 在清理逻辑之后，生成索引
with open("history_index.md", "w", encoding="utf-8") as f:
    f.write("# 歴史データ一覧\n")
    for filename in sorted(os.listdir(history_dir), reverse=True):
        f.write(f"- {filename}\n")
