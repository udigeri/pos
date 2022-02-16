# # import os
import sqlite3
import requests
from requests.auth import HTTPBasicAuth
import json
from flask import Flask
from .api.adn import Adn
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
        self.adn = Adn(self.config, self.logger)
        self.port = getattr(self.config, "web_port")
        logger.info(f"Web module started on {self.host} :{self.port}")
        # http
        self.flsk.run(host=self.host, port=self.port, debug=self.debug)
        # https
        # self.flsk.run(host=self.host, port=self.port, debug=self.debug, ssl_context='adhoc')

    def _getAuthenticationURL(self):
        return self.adn._getHost()

    def getAuthentication(self, usr, pwd):
        self.username = usr
        self.password = pwd

        error = None
        self.adn.setAuth(HTTPBasicAuth(usr, pwd))
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

    def payParkingTicket(self, pp, lpn, amount):
        """This method pay parking ticket"""
        self.logger.info(f"Web parking ticket for {pp} {lpn} amount {amount}")
        trx = Transaction(pp, lpn, amount)
        trx = self.adn.pay_transaction(trx)

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
            self.logger.info(f"Transaction: {trx.trxId} {trx.mediaType} {trx.maskedMediaId} {trx.status} Info:{trx.description}")

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

    def abortTransaction(self, pp, lpn, amount):
        """This method pay parking ticket"""
        self.logger.info(f"Web parking ticket for {pp} {lpn} amount {amount}")
        trx = Transaction(pp, lpn, amount)
        trx = self.adn.abort_transaction(trx, self.trxs[-1].timestamp.strftime('%m%d%H%M%S'))

        if trx.rsp_status_code == 200:
            trx.author_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            self.logger.info(f"Transaction: {trx.trxId} {trx.mediaType} {trx.maskedMediaId} {trx.status} Info:{trx.description}")

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

    def statusTransaction(self, pp, lpn, amount):
        """This method pay parking ticket"""
        self.logger.info(f"Web parking ticket for {pp} {lpn} amount {amount}")
        trx = Transaction(pp, lpn, amount)
        trx = self.adn.status_transaction(trx, self.trxs[-1].timestamp.strftime('%m%d%H%M%S'))

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
            self.logger.info(f"Transaction: {trx.trxId} {trx.mediaType} {trx.maskedMediaId} {trx.status} Info:{trx.description}")

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

    def diagnoseTerminal(self, pp, lpn, amount):
        """This method diagnose terminal"""
        self.logger.info(f"Web Diagnose for {pp} {lpn} amount {amount}")
        trx = Transaction(pp, lpn, amount)
        trx = self.adn.diagnose_terminal(trx)

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
            self.logger.info(f"Diagnose: {trx.trxId} {trx.mediaType} {trx.maskedMediaId} {trx.status} Info:{trx.description}")

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
