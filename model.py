
class Currency:
    def __init__(self, paramrssurl):
        self.fullname = paramrssurl.fullname.text
        self.title = paramrssurl.title.text
        self.description = paramrssurl.description.text
        self.quant = paramrssurl.quant.text
        # self.index = paramrssurl.index.text
        self.change = paramrssurl.change.text

    def get_currency_data(self):
        currency_data = {
            'fullname': self.fullname,
            'title': self.title,
            'description': self.description,
            'quant': self.quant,
            # 'index': self.index,
            'change': self.change
        }
        return currency_data
