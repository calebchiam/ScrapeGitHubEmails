import pandas as pd
import time
from tqdm import tqdm
import requests
import json
from collections import Counter
from config import USERNAME, TOKEN

INPUT_FILEPATH = 'CleanlabStargazersNamesEmails.csv'
OUTPUT_FILEPATH = 'CleanlabStargazersNamesEmails.csv'

ACTIVITY_URL = 'https://api.github.com/users/{}/events/public'
USER_URL = 'https://api.github.com/users/{}'
SCRAPE_EMAIL = True

def get_reset_time(res):
    return int(res.headers['X-RateLimit-Reset'])

def check_ratelimit(res):
    remaining = int(res.headers['X-RateLimit-Remaining'])
    if remaining % 50 == 0:
        print(f"RateLimit-Remaining is {remaining}")
    if remaining == 1:
        print("RateLimit is now 1. Sleeping until reset...")
        time.sleep(get_reset_time(res) - int(time.time()) + 100)

def get_last_filled_email_index(df):
    completed_indices = list(df.index[df['email'].apply(lambda x: isinstance(x, str) and len(x) > 0)])
    # print(completed_indices)
    if len(completed_indices) == 0:
        return -1
    else:
        return max(completed_indices)

def get_email_from_entry(entry):
    commits = entry['payload'].get('commits', None)
    if commits is not None:
        return [c['author']['email'] for c in commits]
    else:
        return []

def get_email_from_activity(username):
    """
    Get the most common email address from activity
    """
    res = requests.get(ACTIVITY_URL.format(username), auth=(USERNAME, TOKEN))
    check_ratelimit(res)
    if res.status_code != 200:
        raise ValueError(f'Invalid status code of {res.status_code} for {username}, check internet connection or verify that you have not been rate-limited')
    user_activity = json.loads(res.content)

    all_addrs = []
    for entry in user_activity:
        all_addrs += get_email_from_entry(entry)
    all_addrs = [x for x in all_addrs if '@users.noreply.git' not in x]
    most_common_emails = Counter(all_addrs).most_common()
    if len(most_common_emails) == 0:
        return ''
    else:
        return most_common_emails[0][0]

def get_name_email_from_profile(username):
    res = requests.get(USER_URL.format(username), auth=(USERNAME, TOKEN))
    check_ratelimit(res)
    if res.status_code != 200:
        raise ValueError(f'Invalid status code of {res.status_code} for {username}, check internet connection or verify that you have not been rate-limited')
    user_profile = json.loads(res.content)
    return user_profile.get('name', None), user_profile.get('email', None)


if __name__ == '__main__':
    df = pd.read_csv(INPUT_FILEPATH)
    for new_col in ['email', 'name']:
        if new_col not in df.columns:
            df[new_col] = ''
    scraped_emails = []
    scraped_names = []

    start_idx = get_last_filled_email_index(df) + 1
    if start_idx >= 1:
        print(f"Found previously completed entries, starting from index {start_idx}...")

    scraped_emails = list(df['email'])[:start_idx]
    scraped_names = list(df['name'])[:start_idx]

    try:
        print("Beginning scrape!")
        for username in tqdm(df['username'][start_idx:]):
            name, email = get_name_email_from_profile(username)
            if email is None:
                email = get_email_from_activity(username)
            if name is None:
                name = ''
            scraped_emails.append(email)
            scraped_names.append(name)
        print("Completed scrape!")
    finally:
        df['email'] = scraped_emails + [''] * (len(df) - len(scraped_emails))
        df['name'] = scraped_names + [''] * (len(df) - len(scraped_names))
        df.to_csv(OUTPUT_FILEPATH, index=False)
