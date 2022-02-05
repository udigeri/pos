# # import os
import sqlite3
import requests
from requests.auth import HTTPBasicAuth
import json
from flask import Flask
from .api.pgs import Pgs
from .api.transaction import Transaction
from datetime import datetime

class Web():
    SECRET_KEY = 'my_uno-tuti_secret_things'

    def __init__(self, host='0.0.0.0', port=80, debug=False):
        self.host = host
        self.port = port
        self.debug = debug
        self.username = None
        self.password = None
        self.flsk = Flask(__name__)
        self.flsk.config.from_object(self)
        self.trxs = []
        self.tokens = []

    def run(self, config, logger):
        self.config = config
        self.logger = logger
        self.pgs = Pgs(self.config, self.logger)
        self.port = getattr(self.config, "web_port")
        logger.info(f"Web module started on {self.host} :{self.port}")
        # http
        self.flsk.run(host=self.host, port=self.port, debug=self.debug)
        # https
        # self.flsk.run(host=self.host, port=self.port, debug=self.debug, ssl_context='adhoc')

    def _getAuthenticationURL(self):
        return self.pgs._getHost()

    def getAuthentication(self, usr, pwd):
        self.username = usr
        self.password = pwd

        error = None
        self.pgs.setAuth(HTTPBasicAuth(usr, pwd))
        try:
            rsp = requests.get(self._getAuthenticationURL(), auth=HTTPBasicAuth(usr, pwd))
            if rsp.status_code != 404 & rsp.status_code != 200:
                error = "Authentication failed Status code {} {}".format(rsp.status_code, self._getAuthenticationURL())
                self.logger.warning(error)
            else:
                self.logger.info("Web Authentication success")
        except Exception as err:
            error = "Authentication failed {}".format(err)
            self.logger.error(error)
        return error

    def get_shoppingCart(self, pp, lpn, amount, tokenize):
        """This method creates a new shopping cart for a tenant and can generate token"""
        self.logger.info(f"Web shopping cart for {pp} {lpn} amount {amount}")
        trx = Transaction(pp, lpn, amount)
        if tokenize:
            trx = self.pgs.get_shopping_cart(trx, True)
        else:
            trx = self.pgs.get_shopping_cart(trx, False)
        try:
            if trx.rsp_status_code == 200:
                data = json.loads(trx.rsp_text)
                for key in data:
                    if key == 'cartId':
                        trx.shoppingCartUuid = data[key]
                        self.logger.info('Provided shopping cart {cartId}'.format(cartId=data[key])) 
                    elif key == 'pgsToken':
                        trx.pgsTokenUuid = data[key]
                        self.logger.info('Provided token {token}'.format(token=data[key])) 
            else:
                if trx.rsp_status_code == 500:
                    trx.rsp_status = str(trx.rsp_status_code)
                    trx.rsp_code = "Internal Server Error"
                else:
                    data = json.loads(trx.rsp_text)
                    for key in data:
                        if key == 'code':
                            trx.rsp_code = data[key]
                        elif key == 'status':
                            trx.rsp_status = data[key]
        finally:
            self.trxs.append(trx)
        return trx

    def get_tokenCart(self, pp, lpn, amount):
        """This method creates a new token cart for a tenant"""
        self.logger.info(f"Web token cart for {pp} {lpn} amount {amount}")
        trx = Transaction(pp, lpn, amount)
        trx = self.pgs.get_token_cart(trx)
        try:
            if trx.rsp_status_code == 200:
                data = json.loads(trx.rsp_text)
                for key in data:
                    if key == 'cartId':
                        trx.shoppingCartUuid = data[key]
                        self.logger.info('Provided token cart {cartId}'.format(cartId=data[key])) 
            else:
                if trx.rsp_status_code == 500:
                    trx.rsp_status = str(trx.rsp_status_code)
                    trx.rsp_code = "Internal Server Error"
                else:
                    data = json.loads(trx.rsp_text)
                    for key in data:
                        if key == 'code':
                            trx.rsp_code = data[key]
                        elif key == 'status':
                            trx.rsp_status = data[key]
        finally:
            self.trxs.append(trx)
        return trx

    def pay_tokenCart(self, trx, transInitiator):
        """This method pay token cart for a tenant with using token"""
        self.logger.info(f"Web pay token cart {trx.shoppingCartUuid} amount {trx.amount} with token {trx.pgsTokenUuid}")
        trx = self.pgs.pay_token_cart(trx, trx.shop, trx.correlationId, trx.shoppingCartUuid, trx.pgsTokenUuid, transInitiator)

        if trx.rsp_status_code == 200:
            data = json.loads(trx.rsp_text)
            for key in data:
                if key == 'status':
                    trx.status = data[key]
                elif key == 'payId':
                    trx.trxId = data[key]
                elif key == 'mediaType':
                    trx.mediaType = data[key]
                elif key == 'maskedMediaId':
                    trx.maskedMediaId = data[key]
                elif key == 'description':
                    trx.description = data[key]
            trx.author_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            self.logger.info(f"TokenCart: {trx.shoppingCartUuid} Transaction: {trx.trxId} {trx.mediaType} {trx.maskedMediaId} {trx.status} Info:{trx.description}")

        else:
            if trx.rsp_status_code == 500:
                trx.rsp_status = str(trx.rsp_status_code)
                trx.rsp_code = "Internal Server Error"
            else:
                data = json.loads(trx.rsp_text)
                for key in data:
                    if key == 'code':
                        trx.rsp_code = data[key]
                    elif key == 'status':
                        trx.rsp_status = data[key]
        return trx

    def do_refundCart(self, trx):
        """This method refund token cart for a tenant"""
        self.logger.info(f"Web refund cart {trx.shoppingCartUuid} amount {trx.amount}")
        trx = self.pgs.do_refund_cart(trx)

        if trx.rsp_status_code == 200:
            trx.status = "SUCCESS"
            trx.author_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            self.logger.info(f"TokenCart: {trx.shoppingCartUuid} Refund: {trx.status}")

        else:
            if trx.rsp_status_code == 500:
                trx.rsp_status = str(trx.rsp_status_code)
                trx.rsp_code = "Internal Server Error"
            else:
                data = json.loads(trx.rsp_text)
                for key in data:
                    if key == 'code':
                        trx.rsp_code = data[key]
                    elif key == 'status':
                        trx.rsp_status = data[key]
        return trx

    def get_tokenize(self, pp, lpn, amount):
        """This method generate clientHandle and pgsToken for a tenant"""
        self.logger.info(f"Web tokenization generate for {pp} {lpn} amount {amount}")
        trx = Transaction(pp, lpn, amount)
        trx = self.pgs.get_clientHandle(trx, False)
        try:
            if trx.rsp_status_code == 200:
                data = json.loads(trx.rsp_text)
                for key in data:
                    if key == 'clientHandle':
                        trx.clientHandleUuid = data[key]
                        self.logger.info('Provided clientHandle {clientHandle}'.format(clientHandle=data[key])) 
                    elif key == 'pgsToken':
                        trx.pgsTokenUuid = data[key]
                        self.logger.info('Provided token {token}'.format(token=data[key])) 
            else:
                if trx.rsp_status_code == 500:
                    trx.rsp_status = str(trx.rsp_status_code)
                    trx.rsp_code = "Internal Server Error"
                else:
                    data = json.loads(trx.rsp_text)
                    for key in data:
                        if key == 'code':
                            trx.rsp_code = data[key]
                        elif key == 'status':
                            trx.rsp_status = data[key]
        finally:
            self.trxs.append(trx)
        return trx

    def get_tokenValidity(self, trx):
        """This method check if pgsToken is valid for a tenant"""
        self.logger.info(f"Web token validity")
        trx = self.pgs.get_tokenvalidity(trx)
        if trx.rsp_status_code == 200:
            data = json.loads(trx.rsp_text)
            for key in data:
                if key == 'tokenStatus':
                    trx.tokenStatus = data[key]
                    self.logger.info('Provided TokenStatus {tokenStatus}'.format(tokenStatus=data[key])) 
                elif key == 'mediaType':
                    trx.mediaType = data[key]
                    self.logger.info('Provided CardCircuit {cardCircuit}'.format(cardCircuit=data[key])) 
                elif key == 'maskedMediaId':
                    trx.maskedMediaId = data[key]
                    self.logger.info('Provided PAN {pan}'.format(pan=data[key])) 
                elif key == 'mediaExpiryDate':
                    trx.mediaExpiry = data[key]
                    self.logger.info('Provided Expiry date {exp}'.format(exp=data[key])) 
        else:
            if trx.rsp_status_code == 500:
                trx.rsp_status = str(trx.rsp_status_code)
                trx.rsp_code = "Internal Server Error"
            else:
                data = json.loads(trx.rsp_text)
                for key in data:
                    if key == 'code':
                        trx.rsp_code = data[key]
                    elif key == 'status':
                        trx.rsp_status = data[key]
        return trx

    def get_tokenDelete(self, trx):
        """This method delete pgsToken for a tenant"""
        self.logger.info(f"Web token delete")
        trx = self.pgs.get_tokendelete(trx)
        if trx.rsp_status_code == 200:
            data = json.loads(trx.rsp_text)
            for key in data:
                if key == 'tokenStatus':
                    trx.tokenStatus = data[key]
                    self.logger.info('Provided TokenStatus {tokenStatus}'.format(tokenStatus=data[key])) 
                elif key == 'resultDetails':
                    trx.details = data[key]
                    self.logger.info('Provided Details {details}'.format(details=data[key])) 
        else:
            if trx.rsp_status_code == 500:
                trx.rsp_status = str(trx.rsp_status_code)
                trx.rsp_code = "Internal Server Error"
            else:
                data = json.loads(trx.rsp_text)
                for key in data:
                    if key == 'code':
                        trx.rsp_code = data[key]
                    elif key == 'status':
                        trx.rsp_status = data[key]
        return trx

    def get_pay_methods(self, trx):
        """This method gets available payment types for a regular payment"""
        self.logger.info(f"Web pay methods for {trx.shoppingCartUuid}")
        trx = self.pgs.get_payment_methods(trx)

        if trx.rsp_status_code == 200:
            data = json.loads(trx.rsp_text)

            # mandatory fields
            trx.trx_methods = [y[z] for x in data for y in data[x] for z in y if x=='offeredPaymentTypes' if z=='name']
            trx.trx_urls = [y[z] for x in data for y in data[x] for z in y if x=='offeredPaymentTypes' if z=='formUrl']
            trx.trx_fees = [y[z] for x in data for y in data[x] for z in y if x=='offeredPaymentTypes' if z=='fee']
            # optional fields
            for i in range(len(trx.trx_methods)) :
                method = data['offeredPaymentTypes'][i]
                if (method['name'] == trx.trx_methods[i]):
                    if 'imageUrl' in method:
                        trx.trx_imageUrls.append(method['imageUrl'])
                    else:
                        trx.trx_imageUrls.append("../static/none.png")
                    if 'isTokenizationPossible' in method:
                        trx.trx_possible_tokenization.append(method['isTokenizationPossible'])
                    else:
                        trx.trx_possible_tokenization.append("False")

            for id in range(len(trx.trx_methods)):
                self.logger.info(f'{trx.trx_methods[id]} {trx.trx_fees[id]} {trx.trx_urls[id]} {trx.trx_imageUrls[id]} {trx.trx_possible_tokenization[id]}')
        return trx

    def get_token_methods(self, trx):
        """This method gets available tokenization method types for a regular tokenization"""
        self.logger.info(f"Web tokenization methods for {trx.clientHandleUuid}")
        trx = self.pgs.get_tokenization_methods(trx)

        if trx.rsp_status_code == 200:
            data = json.loads(trx.rsp_text)

            # mandatory fields
            trx.trx_methods = [y[z] for x in data for y in data[x] for z in y if x=='offeredTokenizations' if z=='name']
            trx.trx_paymentIds = [y[z] for x in data for y in data[x] for z in y if x=='offeredTokenizations' if z=='paymentId']
            trx.trx_urls = [y[z] for x in data for y in data[x] for z in y if x=='offeredTokenizations' if z=='formUrl']
            trx.trx_fees = [y[z] for x in data for y in data[x] for z in y if x=='offeredTokenizations' if z=='fee']
            # optional fields
            for i in range(len(trx.trx_methods)) :
                method = data['offeredTokenizations'][i]
                if (method['name'] == trx.trx_methods[i]):
                    if 'imageUrl' in method:
                        trx.trx_imageUrls.append(method['imageUrl'])
                    else:
                        trx.trx_imageUrls.append("../static/none.png")

            for id in range(len(trx.trx_methods)):
                self.logger.info(f'{trx.trx_methods[id]} {trx.trx_fees[id]} {trx.trx_urls[id]} {trx.trx_imageUrls[id]} {trx.trx_paymentIds[id]}')
        return trx
