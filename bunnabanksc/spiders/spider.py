import scrapy

from scrapy.loader import ItemLoader

from ..items import BunnabankscItem
from itemloaders.processors import TakeFirst
import requests

base_url = "https://bunnabanksc.com/wp-admin/admin-ajax.php"

base_payload = "action=pagination_request&sid=c239936wcd&unid=&page={}&lang=&ajax_nonce=6ad426dd40"
headers = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'Accept': '*/*',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'Origin': 'https://bunnabanksc.com',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://bunnabanksc.com/about-us/news/?_page=2',
  'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8'
}


class BunnabankscSpider(scrapy.Spider):
	name = 'bunnabanksc'
	page = 1
	start_urls = ['https://bunnabanksc.com/about-us/news/']

	def parse(self, response):
		data = requests.request("POST", base_url, headers=headers, data=base_payload.format(self.page))
		raw_data = scrapy.Selector(text=data.text)

		post_links = raw_data.xpath('//div[@class="pt-cv-ifield"]')
		for post in post_links:
			url = post.xpath('.//h1/a/@href').get()
			date = post.xpath('.//time/text()').get()
			if url:
				yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		if post_links:
			self.page += 1
			yield response.follow(response.url, self.parse, dont_filter=True)

	def parse_post(self, response, date):
		title = response.xpath('//div[@class="jx-monex-title"]/text()').get()
		description = response.xpath('//div[@class="jx-monex-description"]//text()[normalize-space() and not(ancestor::span)]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=BunnabankscItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
