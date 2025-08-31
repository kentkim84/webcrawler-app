import logging

class CollectItemsPipeline:
    def __init__(self, results_list):
        self.results_list = results_list
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Pipeline initialized with results_list ID: {id(results_list)}")

    @classmethod
    def from_crawler(cls, crawler):
        results_list = crawler.settings.get('COLLECT_ITEMS_LIST', [])
        logger = logging.getLogger(__name__)
        logger.info(f"Pipeline from_crawler with results_list ID: {id(results_list)}")
        return cls(results_list)

    def process_item(self, item, spider):
        self.logger.info(f"Processing item: {dict(item)}, appending to list ID: {id(self.results_list)}")
        self.results_list.append(dict(item))  # Convert Scrapy Item to dict
        self.logger.info(f"After append, results_list: {self.results_list}")
        return item