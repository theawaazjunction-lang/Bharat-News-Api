import os
import json
import pandas as pd
from datetime import datetime, timezone
import pytz

def process_and_push_to_db(news_data):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    locations_path = os.path.join(BASE_DIR, "india_locations_cities.csv")
    output_path = os.path.join(BASE_DIR, "data.json")

    if not os.path.exists(locations_path):
        print(f"❌ Error: Could not find '{locations_path}'.")
        return

    try:
        df_locations = pd.read_csv(locations_path)
    except Exception as e:
        print(f"❌ Error reading locations CSV: {e}")
        return

    articles = news_data.get('articles', [])
    print(f"Loaded {len(articles)} articles into memory. Processing...")

    processed_articles = []
    for article in articles:
        t = article['title'] if article['title'] else ""
        d = article['description'] if article['description'] else ""
        searchable = f"{t} {d}".lower()
        display = t.strip()
        if display:
            processed_articles.append((searchable, display))

    def get_state_stats(row):
        state_name = str(row['State']).lower()
        valid_names = [state_name]
        cities_str = str(row['cities'])
        if cities_str and cities_str != "nan":
            city_list = [c.strip().lower() for c in cities_str.split(',')]
            valid_names.extend([c for c in city_list if c])

        found_headlines = []
        for search_text, display_headline in processed_articles:
            for term in valid_names:
                if f" {term} " in f" {search_text} ":
                    if display_headline not in found_headlines:
                        found_headlines.append(display_headline)
                    break

        count = len(found_headlines)
        return pd.Series([count, found_headlines])

    print("Scanning headlines against States & Cities...")
    df_locations[['news_count', 'headlines']] = df_locations.apply(get_state_stats, axis=1)

    df_final = df_locations[df_locations['news_count'] > 0].copy()
    df_final.sort_values(by='news_count', ascending=False, inplace=True)

    if "cities" in df_final.columns:
        df_final.drop("cities", axis=1, inplace=True)

    current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    last_updated = pytz.utc.localize(datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')).astimezone(pytz.timezone("Asia/Kolkata")).strftime('%Y-%m-%d %I:%M:%S %p')
    df_final['last_updated'] = last_updated

    records = df_final.to_dict(orient='records')

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        print(f"✅ DONE. Wrote {len(records)} active regions to {output_path}")
    except Exception as e:
        print(f"❌ File Write Error: {e}")
