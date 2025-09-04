import urllib.request
import json
import pandas as pd
import time

def fetch_with_retry(url, retries=3, delay=5):
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url) as response:
                return response.read().decode('utf-8').splitlines()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(f"Rate limit hit, retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise
    raise Exception("Failed to fetch data after retries")

def rank_lichess_bots_all_variants():
    url = 'https://lichess.org/api/bot/online'
    data = fetch_with_retry(url)
    
    bots = []
    for line in data:
        if line.strip():
            try:
                bots.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    
    variants = ['bullet', 'blitz', 'rapid', 'classical', 'chess960', 'crazyhouse',
                'antichess', 'kingOfTheHill', 'threeCheck', 'horde', 'racingKings']
    
    rankings = {}
    for variant in variants:
        bot_list = []
        for bot in bots:
            if 'username' in bot and 'perfs' in bot and variant in bot['perfs']:
                rating = bot['perfs'][variant].get('rating', 0)
                bot_list.append({'username': bot['username'], 'rating': rating})
        if bot_list:
            df = pd.DataFrame(bot_list)
            # Sắp xếp theo rating từ cao đến thấp và thêm cột rank bắt đầu từ 1
            df_sorted = df.sort_values(by='rating', ascending=False)
            df_sorted['rank'] = df_sorted.index + 1  # Bắt đầu từ 1
            df_sorted = df_sorted[['rank', 'username', 'rating']]  # Sắp xếp lại cột
            rankings[variant] = df_sorted
            df_sorted.to_csv(f'lichess_bots_ranking_{variant}.csv', index=False, encoding='utf-8')
            print(f"Ranking for {variant} stored to 'lichess_bots_ranking_{variant}.csv' with {len(df_sorted)} bots")
    
    return rankings

if __name__ == "__main__":
    rankings = rank_lichess_bots_all_variants()
    if rankings:
        print("\nLichess Bots Rankings (All Bots by Variant):\n")
        # Hiển thị toàn bộ Bullet ranking với số thứ tự
        if 'bullet' in rankings:
            print("\nBullet Ranking (Full List with Rank):\n")
            for idx, row in rankings['bullet'].iterrows():
                print(f"{row['rank']}. {row['username']} {row['rating']}")
        else:
            print("No Bullet ranking available.")
        # Hiển thị top 5 cho các variant khác với số thứ tự
        for variant, ranking in rankings.items():
            if variant != 'bullet':
                print(f"\n{variant.capitalize()} Ranking (Top 5 with Rank):\n")
                for idx, row in ranking.head(5).iterrows():
                    print(f"{row['rank']}. {row['username']} {row['rating']}")
    else:
        print("No bots found or no valid data.")
