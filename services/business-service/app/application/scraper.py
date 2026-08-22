import scrapy
import json

class CompetitorSpider(scrapy.Spider):
    name = "competitor_spider"
    
    def __init__(self, query="", *args, **kwargs):
        super(CompetitorSpider, self).__init__(*args, **kwargs)
        self.start_urls = [f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}+price"]

    def parse(self, response):
        results = []
        for result in response.css('.result__body'):
            title = result.css('.result__title .result__a::text').get()
            snippet = result.css('.result__snippet::text').get()
            if title and snippet:
                results.append({"title": title.strip(), "snippet": snippet.strip()})
        
        yield {"results": results[:3]}
