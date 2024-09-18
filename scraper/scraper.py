from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv
from datetime import datetime
import os
from selenium.webdriver.chrome.options import Options
import re


class CustomScraper:
    def __init__(self,
                 target_directory='temp',
                 scroll_amount=500,
                 store='store',
                 page_count=1,
                 page_flag=False,
                 url='',
                 content_area_css='',
                 description_css='',
                 price_css='',
                 link_css=''):

        os.makedirs(target_directory, exist_ok=True)
        self.target_directory = target_directory
        self.scroll_amount = scroll_amount
        self.store = store
        self.page_count = page_count
        self.page_flag = page_flag
        self.url = url
        self.content_area_css = content_area_css
        self.description_css = description_css
        self.price_css = price_css
        self.link_css = link_css
        self.current_date = datetime.now().strftime('%Y-%m-%d')
        self.csv_file_path = os.path.join(target_directory,
                                          f'{self.current_date}_{store}.csv')

    def smooth_scroll(self, driver):
        current_scroll_position = 0
        last_scroll_height = driver.execute_script("return document.body.scrollHeight")

        while current_scroll_position < last_scroll_height:
            driver.execute_script(f"window.scrollBy(0, {self.scroll_amount});")
            current_scroll_position += self.scroll_amount
            time.sleep(1)
            new_scroll_height = driver.execute_script("return document.body.scrollHeight")
            last_scroll_height = new_scroll_height

    def scrape_data(self):
        # Set Chrome options to enable headless mode
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        with open(self.csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['store', 'date', 'link', 'description', 'price'])

            for page in range(1, self.page_count + 1):
                # Initialize WebDriver with headless mode
                driver = webdriver.Chrome(options=chrome_options)
                if self.page_flag:
                    driver.get(f"{self.url}")
                else:
                    driver.get(f"{self.url}{page}")

                self.smooth_scroll(driver)

                time.sleep(5)
                if self.content_area_css is not None:
                    content_area = driver.find_element(By.CSS_SELECTOR,
                                                       self.content_area_css)
                    text_elements = content_area.find_elements(By.CSS_SELECTOR,
                                                               self.description_css)
                    price_elements = content_area.find_elements(By.CSS_SELECTOR,
                                                                    self.price_css)
                    link_elements = content_area.find_elements(By.CSS_SELECTOR,
                                                                self.link_css)
                else:
                    text_elements = driver.find_elements(By.CSS_SELECTOR,
                                                               self.description_css)
                    price_elements = driver.find_elements(By.CSS_SELECTOR,
                                                                self.price_css)
                    link_elements = driver.find_elements(By.CSS_SELECTOR,
                                                                self.link_css)

                for text_element, price_element, link_element in zip(text_elements, price_elements, link_elements):

                    text = text_element.text.strip()
                    price = price_element.text.strip()
                    link = link_element.get_attribute('href')
                    writer.writerow([self.store,
                                     self.current_date,
                                     link,
                                     text,
                                     re.sub(r'[\n\s$%c/u.-]', '', price)])

                driver.quit()

        print(f"Data has been saved to {self.csv_file_path}")
