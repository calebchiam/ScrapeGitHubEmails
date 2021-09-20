import pandas as pd
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm

INPUT_FILEPATH = 'ScrapeGitHubStars_PyTorch_1.csv'
OUTPUT_FILEPATH = 'ScrapeGitHubStars_PyTorch_1.csv'

def get_last_filled_email_index(df):
    completed_indices = list(df.index[df['email'].apply(lambda x: isinstance(x, str) and len(x) > 0)])
    # print(completed_indices)
    if len(completed_indices) == 0:
        return -1
    else:
        return max(completed_indices)


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
        BASE_URL = 'https://www.github.com/{}'
        driver = webdriver.Firefox()
        driver.get('https://github.com/login')
        time.sleep(30) # login manually
        print("Beginning scrape!")

        for name in tqdm(df['name'][start_idx:]):
            driver.get(BASE_URL.format(name))
            try:
                content = driver.find_element_by_css_selector('a.u-email')
                scraped_emails.append(content.text)
            except NoSuchElementException:
                scraped_emails.append('')
            time.sleep(3)

    finally:
        df['email'] = scraped_emails + [''] * (len(df) - len(scraped_emails))
        df.to_csv(OUTPUT_FILEPATH, index=False)
