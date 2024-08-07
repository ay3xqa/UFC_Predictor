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
            #div.c-listing-fight__country-text::text
            country_text = fight.css("div.c-listing-fight__country-text")
            if country_text[0].css("::text").get():
                f1_flag = fight.css("div.c-listing-fight__country--red img").attrib["src"]
            else:
                f1_flag = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Unknown_flag.svg/2560px-Unknown_flag.svg.png"
            if country_text[1].css("::text").get():
                f2_flag = fight.css("div.c-listing-fight__country--blue img").attrib["src"]
            else:
                f2_flag = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Unknown_flag.svg/2560px-Unknown_flag.svg.png"
            ranks = fight.css("div.c-listing-fight__corner-rank")
            f1_rank = ranks[0].css("span::text").get()
            f2_rank = ranks[1].css("span::text").get()
            if f1_rank:
                if "C" not in f1_rank:
                    f1_rank = f1_rank[1:]
            else:
                f1_rank = ""
            if f2_rank:
                if "C" not in f2_rank:
                    f2_rank = f2_rank[1:]
            else:
                f2_rank = ""
            odds = fight.css("span.c-listing-fight__odds-amount")
            f1_ml = odds[0].css("::text").get()
            f2_ml = odds[1].css("::text").get()


            f1_info = {"f1_flag": f1_flag,
                       "f1_rank": f1_rank,
                       "f1_ml": f1_ml}
            
            f2_info = {"f2_flag": f2_flag,
                        "f2_rank": f2_rank,
                        "f2_ml": f2_ml}

            # fight.css("div.c-listing-fight__corner-rank span")
            res.append((fight.css("div.c-listing-fight__corner-name--red a").attrib["href"],f1_info))
            res.append((fight.css("div.c-listing-fight__corner-name--blue a").attrib["href"],f2_info))

            # res.append(fight.css("div.c-listing-fight__corner-name--red a").attrib["href"])
            # res.append(fight.css("div.c-listing-fight__corner-name--blue a").attrib["href"])
        for i in range(0, len(res), 2):
            if i + 1 < len(res):
                f1 = self.fetch_and_parse_fight(res[i][0], "f1_")
                f2 = self.fetch_and_parse_fight(res[i + 1][0], "f2_")
                f1.update(f2)
                f1.update(res[i][1])
                f1.update(res[i+1][1])
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
        if len(selector.css("div.c-bio__text")) > 4:
            height = selector.css("div.c-bio__text")[-5].css("::text").get()
            height = f"{int(float(height) // 12)}'{int(float(height) % 12)}"

            weight = selector.css("div.c-bio__text")[-4].css("::text").get()
            weight = f"{float(weight):.1f}"

            reach = selector.css("div.c-bio__text")[-2].css("::text").get()
            reach = f'{float(reach):.1f}"'
        else:
            height = "N/A"
            weight = "N/A"
            reach = "N/A"

        record_line = selector.css("p.hero-profile__division-body::text").get()
        record_line = record_line.split(" ")
        record = record_line[0]
        return {
            prefix+"name": name,
            prefix+"age": age,
            prefix+"height": height,
            prefix+"weight": weight,
            prefix+"reach": reach,
            prefix+"image": img,
            prefix+"record": record
        } 