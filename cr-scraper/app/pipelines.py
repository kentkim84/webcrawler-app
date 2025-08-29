class PreprocessPipeline:
    def process_item(self, item, spider):
        # Example: strip whitespace from title/body
        item['title'] = item['title'].strip() if item['title'] else ""
        item['body_text'] = item['body_text'].strip() if item['body_text'] else ""
        return item