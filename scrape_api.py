import pandas as pd
import time
from tqdm import tqdm
import requests
import json
from collections import Counter

INPUT_FILEPATH = 'ScrapeGitHubStars_PyTorch.csv'
OUTPUT_FILEPATH = 'ScrapeGitHubStars_PyTorch.csv'
USERNAME = 'calebchiam'
# generate personal access token here: https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token
TOKEN = ''
ACTIVITY_URL = 'https://api.github.com/users/{}/events/public'
USER_URL = 'https://api.github.com/users/{}'

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
    most_common_emails = Counter(all_addrs).most_common()
    if len(most_common_emails) == 0:
        return ''
    else:
        return most_common_emails[0][0]

def get_email_from_profile(username):
    res = requests.get(USER_URL.format(username), auth=(USERNAME, TOKEN))
    check_ratelimit(res)
    if res.status_code != 200:
        raise ValueError(f'Invalid status code of {res.status_code} for {username}, check internet connection or verify that you have not been rate-limited')
    user_profile = json.loads(res.content)
    return user_profile.get('email', None)


if __name__ == '__main__':
    df = pd.read_csv(INPUT_FILEPATH)
    if 'email' not in df.columns:
        df['email'] = ''
    scraped_emails = []

    start_idx = get_last_filled_email_index(df) + 1
    if start_idx >= 1:
        print(f"Found previously completed entries, starting from index {start_idx}...")

    scraped_emails = list(df['email'])[:start_idx]

    try:
        print("Beginning scrape!")
        for name in tqdm(df['name'][start_idx:]):
            email = get_email_from_profile(name)
            if email is None:
                email = get_email_from_activity(name)
            scraped_emails.append(email)
        print("Completed scrape!")
    finally:
        df['email'] = scraped_emails + [''] * (len(df) - len(scraped_emails))
        df.to_csv(OUTPUT_FILEPATH, index=False)
