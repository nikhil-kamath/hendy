import time
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import hashlib
import os


def process_youtube_comments(link, amount=3):
    data = []
    title = ""
    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    op.add_argument("--mute-audio")

    with Chrome(executable_path='chromedriver.exe', options=op) as driver:
        wait = WebDriverWait(driver, 15)
        driver.get(link)
        print("opening link")
        time.sleep(10)
        
        title = driver.find_element_by_xpath('//*[@id="container"]/h1/yt-formatted-string').text
        print("title found: ", title)
        for i in range(amount):
            print(f"scrolling {i}/{amount}")
            wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.END)
            time.sleep(5)

        print("reading comments")
        data.extend(comment.text for comment in wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#content"))) if len(comment.text.strip()) != 0)

    print("creating dataframe")
    data = data[1:]
    df = pd.DataFrame(data, columns=['comment'])

    # titlehash = int(hashlib.sha1(link.encode("utf-8")).hexdigest(), 16) % (10 ** 8)
    outdir = './yt'
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    shortened_name = "".join(x for x in title if x.isalpha())
    print(f"creating pickle file {shortened_name}.pkl")
    df.to_pickle(os.path.join(outdir, f"{shortened_name}.pkl"))
    print("processing done")
    return df, title
    

