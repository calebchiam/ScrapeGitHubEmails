import pandas as pd
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm

INPUT_FILEPATH = 'github_starrers.xlsx'
INPUT_TYPE = INPUT_FILEPATH.split('.')[-1]

OUTPUT_FILEPATH = 'github_starrers.xlsx'
OUTPUT_TYPE = OUTPUT_FILEPATH.split('.')[-1]

if __name__ == '__main__':
    assert INPUT_TYPE in ['xlsx', 'csv']
    assert OUTPUT_TYPE in ['xlsx', 'csv']

    df = pd.read_excel(INPUT_FILEPATH) if INPUT_TYPE == 'xlsx' else pd.read_csv(INPUT_FILEPATH)
    df['email'] = ''
    scraped_emails = []

    try:
        BASE_URL = 'https://www.github.com/{}'
        driver = webdriver.Firefox()
        driver.get('https://github.com/login')
        time.sleep(30) # login manually
        print("Beginning scrape!")

        for name in tqdm(df['name']):
            driver.get(BASE_URL.format(name))
            try:
                content = driver.find_element_by_css_selector('a.u-email')
                scraped_emails.append(content.text)
            except NoSuchElementException:
                scraped_emails.append('')
            time.sleep(3)

    finally:
        df['email'] = scraped_emails + [''] * (len(df) - len(scraped_emails))

        if OUTPUT_TYPE == 'xlsx':
            df.to_excel(OUTPUT_FILEPATH)
        else:
            df.to_csv(OUTPUT_FILEPATH)
