import scrapy
from datetime import datetime, timedelta
from scrapy.selector import Selector
import requests

class MaincardspiderSpider(scrapy.Spider):
    name = "maincardspider"    
    allowed_domains = ["www.ufc.com"]
    start_urls = ["https://www.ufc.com/events"]

    def parse(self, response):
        current_card = response.css("article.c-card-event--result")[0]
        current_card_url = current_card.css("h3 a").attrib["href"]
        yield response.follow(current_card_url, callback = self.parse_event)
        # {"url":current_card_url}

    def parse_event(self, response):
        #get all the expandable content identifiers

        main_card_fights = response.css("div.main-card li.l-listing__item")

        # #get the number of fights in main card
        identifiers = [x.css("div.c-listing-fight").attrib["data-fmid"] for x in main_card_fights]
        res = []
        for fight in main_card_fights:
            res.append(fight.css("div.c-listing-fight__corner-name--red a").attrib["href"])
            res.append(fight.css("div.c-listing-fight__corner-name--blue a").attrib["href"])
        for i in range(0, len(res), 2):
            if i + 1 < len(res):
                f1 = self.fetch_and_parse_fight(res[i], "f1_")
                f2 = self.fetch_and_parse_fight(res[i + 1], "f2_")
                f1.update(f2)
                yield f1
        # for fight in main_card_fights:
        #     f1_name = fight.css("div.c-listing-fight__corner-name--red span.c-listing-fight__corner-given-name::text").get() + fight..css("div.c-listing-fight__corner-name--red span.c-listing-fight__corner-given-name::text").get()

    def fetch_and_parse_fight(self, url, prefix):
        # Fetch the HTML content synchronously
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse the content using a Selector
        selector = Selector(text=response.text)
        img = selector.css("div.hero-profile__image-wrap img").attrib["src"]
        name = selector.css("h1.hero-profile__name::text").get()
        age = selector.css("div.field--name-age::text").get()        
        height = selector.css("div.c-bio__text")[-5].css("::text").get()
        height = f"{int(float(height) // 12)}'{int(float(height) % 12)}"

        weight = selector.css("div.c-bio__text")[-4].css("::text").get()
        weight = f"{float(weight):.1f}"

        reach = selector.css("div.c-bio__text")[-2].css("::text").get()
        reach = f'{reach}"'

        return {
            prefix+"name": name,
            prefix+"age": age,
            prefix+"height": height,
            prefix+"weight": weight,
            prefix+"reach": reach,
            prefix+"image": img
        } 