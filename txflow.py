#https://polygon-mumbai.infura.io/v3/30ad9316ff3b4c8c9b6448e673b842fe


class txflow():
    def __init__(self,
                 merchant_id="",
                 invoice_id="",
                 timestamp=0,
                 product_info="",
                 USD_amount=0,
                 blockchain="",
                 token="",
                 token_amount=0,
                 keypair=("",""),
                 status=False):
        self.merchant_id = merchant_id
        self.invoice_id = invoice_id
        self.timestamp = timestamp
        self.product_info = product_info
        self.USD_amount = USD_amount
        self.blockchain = blockchain
        self.id = invoice_id
        self.token = token
        self.token_amount = token_amount
        self.keypair = keypair
        self.status = status

        
    def driver(self):
        pass
