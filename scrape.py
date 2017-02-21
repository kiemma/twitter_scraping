from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from time import sleep
import json
import datetime
import urllib

def main():
    with open('search_template_config.json', 'rb') as infile:
        config = json.load(infile)
        query, start, end, max_per_day, retweets = process_config(config)

        # only edit these if you're having problems
        delay = 1  # time to wait on each page load before reading the page
        driver = webdriver.Chrome('/Users/kristeniemma/Documents/twitter_scraping/chromedriver')  # options are Chrome() Firefox() Safari()

        # don't mess with this stuff
        twitter_ids_filename = 'all_ids.json'
        days = (end - start).days + 1
        id_selector = '.time a.tweet-timestamp'
        tweet_selector = 'li.js-stream-item'
        ids = []

        for day in range(days):
            d1 = format_day(increment_day(start, 0))
            d2 = format_day(increment_day(start, 1))
            url = form_url(query, d1, d2)
            print(url)
            print(d1)
            driver.get(url)
            sleep(delay)

            try:
                found_tweets = driver.find_elements_by_css_selector(tweet_selector)
                increment = 10

                while len(found_tweets) >= increment:
                    print('scrolling down to load more tweets')
                    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                    sleep(delay)
                    found_tweets = driver.find_elements_by_css_selector(tweet_selector)
                    increment += 10

                print('{} tweets found, {} total'.format(len(found_tweets), len(ids)))

                for tweet in found_tweets:
                    try:
                        id = tweet.find_element_by_css_selector(id_selector).get_attribute('href').split('/')[-1]
                        ids.append(id)
                    except StaleElementReferenceException as e:
                        print('lost element reference', tweet)

            except NoSuchElementException:
                print('no tweets on this day')

            start = increment_day(start, 1)


        try:
            with open(twitter_ids_filename) as f:
                all_ids = ids + json.load(f)
                data_to_write = list(set(all_ids))
                print('tweets found on this scrape: ', len(ids))
                print('total tweet count: ', len(data_to_write))
        except FileNotFoundError:
            with open(twitter_ids_filename, 'w') as f:
                all_ids = ids
                data_to_write = list(set(all_ids))
                print('tweets found on this scrape: ', len(ids))
                print('total tweet count: ', len(data_to_write))

        with open(twitter_ids_filename, 'w') as outfile:
            json.dump(data_to_write, outfile)

        print('all done here')
        driver.close()


def format_day(date):
    day = '0' + str(date.day) if len(str(date.day)) == 1 else str(date.day)
    month = '0' + str(date.month) if len(str(date.month)) == 1 else str(date.month)
    year = str(date.year)
    return '-'.join([year, month, day])

def form_url(query, since, until):
    BASE_URL = "https://twitter.com/search?l=&{}%20since%3A{}%20until%3A{}&src=typd"
    url = BASE_URL.format(query, since, until)
    return url

def increment_day(date, i):
    return date + datetime.timedelta(days=i)

def process_config(config):
    search_query = config['search_query']
    username     = config['username']
    since_raw    = config['since'].split('-')
    until_raw    = config['until'].split('-')
    max_per_day  = config['max_per_day']
    retweets     = config['retweets']

    since = datetime.datetime(int(since_raw[0]), int(since_raw[1]), int(since_raw[2]))
    until = datetime.datetime(int(until_raw[0]), int(until_raw[1]), int(until_raw[2]))

    if username:
        query = "from={}".format(username)
        return query, since, until, max, retweets
    if search_query:
        query = 'q="{}"'.format(urllib.parse.quote_plus(search_query))
        return query, since, until, max, retweets
    else:
        return None, None, None, None, None


if __name__ == '__main__':
    main()
