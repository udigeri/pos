import json
from datetime import datetime, timedelta
from random import randrange

class Transaction():
    def __init__(self, pp, lpn, amount):
        self.timestamp = datetime.now()

        self.action = None
        self.shoppingCartUuid = None
        self.clientHandleUuid = None
        self.pgsTokenUuid = None
        self.tokenStatus = None
        self.status = None
        self.details = None
        self.amount = int(amount)
        self.fee = None
        self.currency = "EUR"
        self.local_time = self.timestamp.strftime("%m%d%H%M%S")
        self.exit_time = self.timestamp - timedelta(seconds=1)
        self.exit_time = self.exit_time.strftime("%d.%m.%Y %H:%M:%S")
        self.entry_time = self.timestamp - timedelta(hours=randrange(23), minutes=randrange(59))
        self.entry_time = self.entry_time.strftime("%d.%m.%Y %H:%M:%S")
        self.author_time = None
        self.trxId = None
        self.mediaType = None
        self.maskedMediaId = None
        self.mediaExpiry = None
        self.description = None
        self.correlationId = "0123456789"
        self.costCentre = None
        self.imageColor = "false"
        self.lpn = lpn
        self.reason = "Parking fee"
        self.reference = "Parking Place " + pp
        self.shop = None
        self.shop_info = None
        self.vat_percent = 19
        self.vat_amount = int(int(amount) * self.vat_percent / 100)

        self.rsp_status_code = 0
        self.rsp_text = None
        self.rsp_code = None
        self.rsp_status = None
        self.trx_method_choosen = None
        self.trx_methods = []
        self.trx_paymentIds = []
        self.trx_urls = []
        self.trx_fees = []
        self.trx_imageUrls = []
        self.trx_possible_tokenization = []
        self.trx = []

    def getFormattedAmount(self, amount):
        return '{}.{:0<2}'.format(int(amount/100), int(amount%100) )

    def getTrx(self):
        self.trx.append(self.action)
        self.trx.append(self.shoppingCartUuid)
        self.trx.append(self.clientHandleUuid)
        self.trx.append(self.pgsTokenUuid)
        self.trx.append(self.tokenStatus)
        self.trx.append(self.status)
        self.trx.append(self.details)
        self.trx.append(self.amount)
        self.trx.append(self.currency)
        self.trx.append(self.local_time)
        self.trx.append(self.entry_time)
        self.trx.append(self.exit_time)
        self.trx.append(self.author_time)
        self.trx.append(self.trxId)
        self.trx.append(self.mediaType)
        self.trx.append(self.maskedMediaId)
        self.trx.append(self.mediaExpiry)
        self.trx.append(self.description)
        self.trx.append(self.correlationId)
        self.trx.append(self.costCentre)
        self.trx.append(self.imageColor)
        self.trx.append(self.lpn)
        self.trx.append(self.reason)
        self.trx.append(self.reference)
        self.trx.append(self.shop)
        self.trx.append(self.shop_info)
        self.trx.append(self.vat_percent)
        self.trx.append(self.vat_amount)

        self.trx.append(self.rsp_status_code)
        self.trx.append(self.rsp_text)
        self.trx.append(self.rsp_code)
        self.trx.append(self.rsp_status)

        self.trx.append(self.trx_method_choosen)
        self.trx.append(self.trx_methods)
        self.trx.append(self.trx_paymentIds)
        self.trx.append(self.trx_urls)
        self.trx.append(self.trx_fees)
        self.trx.append(self.trx_imageUrls)
        self.trx.append(self.trx_possible_tokenization)
        return self.trx
