import scrapy
from datetime import datetime, timedelta


class UfcspiderSpider(scrapy.Spider):
    name = "ufcspider"
    allowed_domains = ["ufcstats.com"]
    start_urls = ["http://ufcstats.com/statistics/events/completed?page=all"]

    def parse(self, response):
        cards = response.css('tr.b-statistics__table-row')[2:]
        for card in cards:
            card_date = card.css('span.b-statistics__date::text').get().strip()
            given_date = datetime.strptime(card_date, '%B %d, %Y')
            today_date = datetime.today()
            four_years_ago = today_date - timedelta(days=4 * 365) 
            if given_date < four_years_ago:
                break
            else:
                card_url = card.css('td')[0].css('i a').attrib['href']
                yield response.follow(card_url, callback=self.parse_card)

    def parse_card(self, response):
        fights = response.css('tr.b-fight-details__table-row')[1:]
        event = response.css('span.b-content__title-highlight::text').get().strip()
        date = response.css('li.b-list__box-list-item::text')[1].get().strip()
        location = response.css('li.b-list__box-list-item::text')[3].get().strip()

        for fight in fights:
            fight_url = fight.attrib['data-link']
            yield response.follow(fight_url, callback=self.parse_fight, meta={'event':event, 'date':date, 'location':location})
    
    def parse_fight(self, response):
        fight_details = response.css('tbody.b-fight-details__table-body')[0]
        table_cols = fight_details.css('td')
        f1_sig_strikes = [int(i.strip()) for i in table_cols[2].css('p::text')[0].get().strip().split('of')]
        f2_sig_strikes = [int(i.strip()) for i in table_cols[2].css('p::text')[1].get().strip().split('of')]

        f1_total_strikes = [int(i.strip()) for i in table_cols[4].css('p::text')[0].get().strip().split('of')]
        f2_total_strikes = [int(i.strip()) for i in table_cols[4].css('p::text')[1].get().strip().split('of')]

        f1_takedowns = [int(i.strip()) for i in table_cols[5].css('p::text')[0].get().strip().split('of')]
        f2_takedowns= [int(i.strip()) for i in table_cols[5].css('p::text')[1].get().strip().split('of')]

        f1_takedowns = [int(i.strip()) for i in table_cols[5].css('p::text')[0].get().strip().split('of')]
        f2_takedowns= [int(i.strip()) for i in table_cols[5].css('p::text')[1].get().strip().split('of')]

        f1_control = [int(i.strip()) for i in table_cols[9].css('p::text')[0].get().strip().split(':')]
        f2_control = [int(i.strip()) for i in table_cols[9].css('p::text')[1].get().strip().split(':')]
        f1_control_time = f1_control[0]*60+f1_control[1]
        f2_control_time = f2_control[0]*60+f2_control[1]

        overview = response.css('div.b-fight-details__content')
        mov = overview.css('p')[0].css('i::text')[3].get().strip()
        round = int(overview.css('p')[0].css('i::text')[7].get().strip())
        round_time = [int(i) for i in overview.css('p')[0].css('i::text')[10].get().strip().split(':')]
        fight_format = int(overview.css('p')[0].css('i::text')[13].get().strip()[0])
        fight_duration = (round-1)*300 + round_time[0]*60+round_time[1]

        fight_res = response.css('i.b-fight-details__person-status::text')
        if fight_res[0].get().strip() == 'W':
            result = 1
        else:
            result = 0
    
        yield {
            'date': response.meta.get('date'),
            'event': response.meta.get('event'),
            'location': response.meta.get('location'),
            'result': result,
            'fighter1': table_cols[0].css('p a::text')[0].get().strip(),
            'fighter2': table_cols[0].css('p a::text')[1].get().strip(),
            'method_of_victory': mov,
            'fight_duration': fight_duration,
            'fight_format': fight_format,
            'f1_knockdown': int(table_cols[1].css('p::text')[0].get().strip()),
            'f2_knockdown': int(table_cols[1].css('p::text')[1].get().strip()),
            'f1_sig_strike_land': f1_sig_strikes[0],
            'f2_sig_strike_land': f2_sig_strikes[0],
            'f1_sig_strike_att': f1_sig_strikes[1],
            'f2_sig_strike_att': f2_sig_strikes[1],
            'f1_total_strike_land': f1_total_strikes[0],
            'f2_total_strike_land': f2_total_strikes[0],
            'f1_total_strike_att': f1_total_strikes[1],
            'f2_total_strike_att': f2_total_strikes[1],
            'f1_takedown_land': f1_takedowns[0],
            'f2_takedown_land': f2_takedowns[0],
            'f1_takedown_att': f1_takedowns[1],
            'f2_takedown_att': f2_takedowns[1],
            'f1_sub_att': int(table_cols[7].css('p::text')[0].get().strip()),
            'f2_sub_att': int(table_cols[7].css('p::text')[1].get().strip()),
            'f1_reversal': int(table_cols[8].css('p::text')[0].get().strip()),
            'f2_reversal': int(table_cols[8].css('p::text')[1].get().strip()),
            'f1_control_time': f1_control_time,
            'f2_control_time': f2_control_time
        }  

