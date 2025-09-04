import urllib.request
import json
import pandas as pd

def rank_lichess_bots_all_variants(top_n=50):
    url = 'https://lichess.org/api/bot/online'
    with urllib.request.urlopen(url) as response:
        data = response.read().decode('utf-8').splitlines()
    
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
            df_sorted = df.sort_values(by='rating', ascending=False).reset_index(drop=True)
            rankings[variant] = df_sorted.head(top_n)
            df_sorted.to_csv(f'lichess_bots_ranking_{variant}.csv', index=False)
            print(f"Ranking for {variant} stored to 'lichess_bots_ranking_{variant}.csv'")
    
    return rankings

if __name__ == "__main__":
    rankings = rank_lichess_bots_all_variants(top_n=10)
    if rankings:
        print("\nTop Lichess Bots Rankings (by Variant):\n")
        for variant, ranking in rankings.items():
            print(f"\n{variant.capitalize()} Ranking:\n")
            print(ranking)
    else:
        print("No bots found or no valid data.")
