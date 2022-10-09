import re
import os
import time
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


class ChromeDriver():
    def __init__(self, driver_path):
        self.opts = Options()
        self.driver = webdriver.Chrome(driver_path, options=self.opts)

    def click_element(self, *args, **kwargs):
        if kwargs['by_class_name']:
            try:
                element = self.driver.find_element(
                    By.CLASS_NAME, kwargs['by_class_name'])
                element.click()
            except:
                print('There was no button to click.')

    @ property
    def url(self):
        return self.__url

    @ url.setter
    def url(self, url):
        self.__url = url
        self.driver.get(url)

    @ property
    def html_content(self):
        return BeautifulSoup(self.driver.page_source, 'html.parser')


class Course():
    def __init__(self, course_name):
        self.__course_name = course_name

    @property
    def main_page_link(self):
        self.__base_url = 'https://www.coursera.org/learn/%s/reviews'
        return self.__base_url % self.__course_name

    def page_link(self, page_num):
        self.__page_num = page_num
        return self.main_page_link + '?page=%s' % self.__page_num

    def save_course_info_to_file(self, file_location):
        file_path = file_location + '/course_info.csv'

        info = pd.DataFrame()

        info.loc[0, 'name'] = self.__course_name
        info.loc[0, 'title'] = self.title
        info.loc[0, 'about_text'] = self.about_text
        info.loc[0, 'review_pages'] = len(self.available_review_pages)+1
        info.loc[0, 'link'] = self.main_page_link

        # if it is not the first making this file
        # get the previous and add to it

        if os.path.exists(file_path):
            original = pd.read_csv(file_path)
            info = pd.concat([original, info], ignore_index=True)

        info.to_csv(file_path, index=False)
        self.all_info = info

        prompt = 'Information about %s with title of %s was added.\n' \
            % (self.__course_name, self.title)

        print(prompt)

    def save_reviews_to_file(self, this_page_reviews, directory=None):

        file_name = directory + self.__course_name + '.csv'

        if not os.path.exists(directory):
            os.makedirs(directory)

        if os.path.exists(file_name):
            original = pd.read_csv(file_name)
            self.all_reviews = pd.concat(
                [original, this_page_reviews], ignore_index=True)
        else:
            self.all_reviews = this_page_reviews

        self.all_reviews.to_csv(file_name, index=False)

        prompt = '%s.csv now contains reviews from page %s\n' \
            % (self.__course_name, self.__page_num)

        print(prompt)


class WebScraper():
    def __init__(self, driver):
        self.__driver = driver

    def get_container_info(self, class_name, tag_type='div'):
        soup = self.__driver.html_content
        container = soup.find(tag_type, class_=class_name)
        return container

    def extract_course_info(self, what_is_needed):
        soup = self.__driver.html_content

        if what_is_needed == 'title':
            div_content = soup.find('div', class_='_1tu07i3a')
            self.__course_title = div_content.find('span').text
            return self.__course_title

        if what_is_needed == 'about_text':
            div_content = soup.find('div', class_='AboutCourse')
            output = div_content.find('span').text
            self.__course_about_text = output.replace('.... View All', '')
            return self.__course_about_text

        if what_is_needed == 'available_review_pages':
            div_content = soup.findAll('a', class_='_b0s5mt2')
            # get the last hyperlink (which represents the last available page)
            self.__course_last_review_page = int(div_content[-1].text)

            # Send a list of pages available.
            # None: Since range doesn't include last element, 1 needs to be added.
            return [page for page in range(1, self.__course_last_review_page + 1)]

        error_message = """
        This is not a valid entry. You can choose 'title', 'about_text', or 'available_review_pages'
        """
        raise ValueError(error_message)

    @property
    def available_review_pages(self):
        soup = self.__driver.html_content
        return soup.find("span", class_="_1lutnh9y").text

    def extract_reviews_from_current_page(self):
        df = pd.DataFrame()
        soup = self.__driver.html_content
        review_blocks = soup.find_all("div", class_="review-text")

        for idx, block in enumerate(review_blocks):
            self.block = block
            df.loc[idx, 'review_date'] = self.get_review_date(block)
            df.loc[idx, 'reviewer'] = self.get_reviewer_name(block)
            df.loc[idx, 'star'] = self.get_star_value(block)
            df.loc[idx, 'helpful'] = self.get_helpful_value(block)
            df.loc[idx, 'text'] = self.get_review_text(block)

            # convert to standard date format
            df['review_date'] = pd.to_datetime(df['review_date'])

        return df

    def get_review_text(self, block):
        review_block = block.find("div", class_="reviewText")
        all_lines = review_block.findAll("p")
        return '\n'.join([line.text for line in all_lines])

    def get_helpful_value(self, block):
        helpful_pattern = re.compile('This is helpful')
        helpful = block.find(text=helpful_pattern)
        value = re.findall('[0-9]+', helpful)
        return value[0] if value else 0

    def get_review_date(self, block):
        date_of_review = block.find("p", class_="dateOfReview").text
        date_of_review_formated = datetime.strptime(
            date_of_review, '%b %d, %Y').date()
        return date_of_review

    def get_reviewer_name(self, block):
        reviewer_block = block.find("p", class_="reviewerName").text
        name = re.findall('By (.*)$', reviewer_block)[0]
        return name

    def get_star_value(self, block):
        # ★: Filled Star    ☆: Star
        stars_div = block.find("div", class_="_1mzojlvw")
        stars_list = stars_div.findAll("span", class_="d-inline-block")
        star_count = \
            sum([1 for star in stars_list if star.text == 'Filled Star'])
        return star_count
