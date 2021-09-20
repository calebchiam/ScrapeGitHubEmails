## Instructions

1. Run `pip install -r requirements.txt`
2. Download Firefox and `brew install geckodriver` (for Mac users), `npm install geckodriver` might work too. For linux users, run `sudo apt-get install firefox-geckodriver`
3. Set filepaths in `scrape.py` (specifically add your specific 'github_starrers.csv' file and update the filepath so scrape.py can find it)
4. Run `python scrape.py` or  `python3 scrape.py`. A Firefox browser should pop up. You have 30 seconds to log in to your GitHub account manually. After that, the program will start scraping and you can safely ignore it.
5. If, for some reason, you exit or terminate the program prematurely, just run `scrape.py` again and it should pick up from where you stopped.
