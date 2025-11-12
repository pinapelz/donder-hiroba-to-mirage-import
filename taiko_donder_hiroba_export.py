import requests
from bs4 import BeautifulSoup
import json
import time
import argparse
import os


SONG_CATEGORIES = ["pops", "kids", "anime", "vocaloid", "game", "variety", "classic", "namco"]
SONG_LIST_BASE_URL = "https://taiko.namco-ch.net/taiko/en/songlist/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}
PLAY_HISTORY_URL = "https://donderhiroba.jp/history_recent_score.php"
DIFFICULTIES = ["support", "easy", "normal", "hard", "oni", "ura_oni"]

DIFFICULTY_MAP = {
    "icon_course02_1_640.png": "EASY",
    "icon_course02_2_640.png": "NORMAL",
    "icon_course02_3_640.png": "HARD",
    "icon_course02_4_640.png": "ONI",
    "icon_course02_4_640.png": "URA_ONI"
}

CROWN_MAP = {
    "crown_02_640.png": "FULL COMBO",
    "crown_03_640.png": "CLEAR",
    "crown_04_640.png": "DONDERFUL COMBO",
}

LAMP_MAP = {
    "best_score_rank_2_640.png": "IKI 1",
    "best_score_rank_3_640.png": "IKI 2",
    "best_score_rank_4_640.png": "IKI 3",
    "best_score_rank_5_640.png": "MIYABI 1",
    "best_score_rank_6_640.png": "MIYABI 2",
    "best_score_rank_7_640.png": "MIYABI 3",
    "best_score_rank_8_640.png": "KIWAMI",
}

def load_chart_cache():
    with open("taiko_charts.json") as f:
        return dict(json.load(f))

def build_taiko_chart_metadata():
    """
    Unfortnatly Donder Hiroba doesn't store any data about the level, need to fetch this elsewhere
    """
    chart_data = {}
    for category in SONG_CATEGORIES:
        url = f"{SONG_LIST_BASE_URL}/{category}.php"
        print(f"[DATA] Getting {category} category charts")
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, 'html.parser')
        table = soup.find("tbody")
        if table is None:
            raise Exception("Unable to fetch chart data for ", category)
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 6:
                continue

            curr_song = {}
            song_metadata = row.find_all("th")
            if not song_metadata:
                continue

            title_th = song_metadata[0]
            artist_tag = title_th.find("p")
            song_artist = artist_tag.get_text(strip=True) if artist_tag else ""

            for tag in title_th.find_all(["p", "span"]):
                tag.decompose()
            song_title = title_th.get_text(strip=True)

            for i in range(len(DIFFICULTIES)):
                if DIFFICULTIES[i] == "support":
                    continue
                diff = str(cols[i].get_text())
                curr_song[DIFFICULTIES[i]] = None if diff == "-" else diff

            curr_song["artist"] = song_artist
            chart_data[song_title] = curr_song

    with open("taiko_charts.json", "w") as f:
        print("Writing charts to cache. Delete this file when new charts come out!")
        json.dump(chart_data, f)
    return chart_data

def get_play_hist(token: str, chart_data):
    """
    Fetch and parse Donder Hiroba play history page.
    Extracts scores, difficulty, ranks, and performance breakdowns.
    Handles pagination by going through all pages until duplicate results are found.
    """
    all_results = []
    page = 1
    previous_page_titles = set()

    while True:
        page_url = f"{PLAY_HISTORY_URL}?page={page}" if page > 1 else PLAY_HISTORY_URL
        print(f"[INFO] Fetching page {page}...")
        play_hist_page = requests.get(page_url, cookies={"_token_v2": token}, headers=headers)
        soup = BeautifulSoup(play_hist_page.text, "html.parser")
        scores = soup.find_all(class_="scoreUser")

        if not scores:
            print(f"[INFO] No scores found on page {page}. Ending pagination.")
            break

        current_page_titles = set()
        page_results = []

        for s in scores:
            title_tag = s.find("h2")
            title = title_tag.text.strip() if title_tag else None

            total_score_tag = s.find("div", class_="scoreScore")
            total_score = total_score_tag.text.strip().replace("点", "") if total_score_tag else None

            # Skip unknown songs
            if not title or chart_data.get(title) is None:
                print(f"[WARN] {title} is unknown in chart_data. Skipping.")
                continue

            current_page_titles.add(title)
            difficulty = crown = lamp = None
            score_element = s.find("div", class_="playDataArea", attrs={"style": True})
            img_tags = score_element.find_all("img") if score_element else []

            for img in img_tags:
                src = img["src"].split("/")[-1]
                if src in DIFFICULTY_MAP:
                    difficulty = DIFFICULTY_MAP[src]
                elif src in CROWN_MAP:
                    crown = CROWN_MAP[src]
                elif src in LAMP_MAP:
                    lamp = LAMP_MAP[src]

            judgements = {}
            combo = pound = None

            score_data_area = s.find("div", class_="scoreDataArea")
            if score_data_area:
                score_elements = score_data_area.find_all("div", class_="playDataArea", recursive=True)
                for el in score_elements:
                    img = el.find("img", class_="score_name")
                    val_tag = el.find("div", class_="playDataScore")
                    if not img or not val_tag:
                        continue

                    src = img["src"].split("/")[-1]
                    value = val_tag.get_text(strip=True).replace("回", "")
                    if not value.isdigit():
                        continue
                    value = int(value)

                    if "score_name_good" in src:
                        judgements["good"] = value
                    elif "score_name_ok" in src:
                        judgements["ok"] = value
                    elif "score_name_ng" in src:
                        judgements["bad"] = value
                    elif "score_name_combo" in src:
                        combo = value
                    elif "score_name_pound" in src:
                        pound = value

            result_entry = {
                "title": title,
                "timestamp": 0,
                "artist": chart_data[title]["artist"],
                "difficulty": difficulty,
                "level": int(chart_data[title].get(difficulty.lower(), 0)) if difficulty else None,
                "crown_rank": crown,
                "score_rank": lamp,
                "score": int(total_score) if total_score and total_score.isdigit() else total_score,
                "judgements": judgements,
                "optional": {
                    "combo": combo,
                    "pound": pound
                }
            }
            page_results.append(result_entry)
        if page > 1 and current_page_titles.issubset(previous_page_titles):
            print(f"[INFO] Page {page} contains duplicate results. Stopping pagination.")
            break

        all_results.extend(page_results)
        print(f"[INFO] Page {page} processed: {len(page_results)} scores found")

        previous_page_titles.update(current_page_titles)
        page += 1

    print(f"[INFO] Total scores collected: {len(all_results)} across {page - 1} pages")

    return {
        "meta": {
            "game": "taiko",
            "playtype": "Single",
            "service": "Donder Hiroba Export"
        },
        "scores": all_results,
    }


if __name__ == "__main__":
    print("[ALERT!] Please first refresh your scores on Donder Hiroba so that it has the latest info. Visit: https://donderhiroba.jp/score_list.php and click on the top right\n\n")
    print("!Your token will change after doing this!")
    parser = argparse.ArgumentParser(
        prog="taiko_donder_hiroba_export.py",
        description="Exports Taiko no Tatsujin scores from Donder Hiroba into a Mirage compatible JSON",
    )
    parser.add_argument("-t", "--token", help="Donder Hiroba _token_v2. See README for instructions on how to get this!")
    args = parser.parse_args()
    if not args.token:
        args.token = input("Please enter your Donder Hiroba _token_v2: ")
    chart_data = {}
    if os.path.exists("taiko_charts.json"):
        file_time = os.path.getmtime("taiko_charts.json")
        current_time = time.time()
        if current_time - file_time > 7 * 24 * 60 * 60:
            print("Chart cache is older than 1 week, regenerating...")
            chart_data = build_taiko_chart_metadata()
        else:
            print("Using cached chart data")
            chart_data = load_chart_cache()
    else:
        print("No chart cache found, generating...")
        chart_data = build_taiko_chart_metadata()
    score_data = get_play_hist(args.token, chart_data)
    with open("mirage_donder_hiroba_export.json", "w") as f:
        json.dump(score_data, f)
