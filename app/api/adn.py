import json
from xmlrpc.client import boolean
from .rest import Restful
from .transaction import Transaction

class Adn(Restful):
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.auth = None

    def _url(self, path):
        return self._getHost() + self._getBaseUrl() + path

    def setAuth(self, auth):
        self.auth = auth

    def _getHost(self):
        return getattr(self.config, "provider_Adyen_host")

    def _getBaseUrl(self):
        return getattr(self.config, "provider_Adyen_baseURL")

    def _getVerifyFlag(self):
        return getattr(self.config, "provider_Adyen_verifyCA")

    def _getSaleId(self):
        return getattr(self.config, "provider_Adyen_SaleID")

    def _getServiceId(self):
        return getattr(self.config, "provider_Adyen_ServiceID")

    def _getPoiId(self):
        return getattr(self.config, "provider_Adyen_POIID")


    def pay_transaction(self, trx):
        featureURL = ""
        body = {
                "SaleToPOIRequest": {
                    "MessageHeader": {
                        "ProtocolVersion": "3.0",
                        "MessageClass": "Service",
                        "MessageCategory": "Payment",
                        "MessageType": "Request",
                        "SaleID": f"{self._getSaleId()}",
                        "ServiceID": f"{trx.timestamp.strftime('%m%d%H%M%S')}",
                        "POIID": f"{self._getPoiId()}"
                    },
                    "PaymentRequest": {
                        "SaleData": {
                            "SaleTransactionID": {
                                "TransactionID": f"{trx.timestamp.strftime('%m%d%H%M%S')}",
                                "TimeStamp": f"{trx.timestamp.strftime('%Y-%m-%dT%H:%M:%S')}"
                            }
                        },
                        "PaymentTransaction": {
                            "AmountsReq": {
                                "Currency": "EUR",
                                "RequestedAmount": float(trx.getFormattedAmount(trx.amount))
                            }
                        }
                    }
                }
                }

        self.logger.debug(self._url(featureURL) + " " + json.dumps(body))
        resp = self.post(self._url(featureURL), 
                        data=json.dumps(body), 
                        auth=self.auth,
                        verify=self._getVerifyFlag())
        trx.rsp_status_code = resp.status_code
        trx.rsp_text = resp.text
        if trx.rsp_status_code == 401:
            self.logger.warn(f"StatusCode:{trx.rsp_status_code} {json.dumps(json.loads(trx.rsp_text))}")
        else:
            self.logger.error(f"StatusCode:{trx.rsp_status_code} {trx.rsp_text}")
        return trx

    def abort_transaction(self, trx, serviceId):
        featureURL = ""
        serviceId = trx.timestamp.strftime('%m%d%H%M%S')
        body = {
                "SaleToPOIRequest": {
                    "MessageHeader": {
                        "ProtocolVersion": "3.0",
                        "MessageClass": "Service",
                        "MessageCategory": "Abort",
                        "MessageType": "Request",
                        "SaleID": f"{self._getSaleId()}",
                        "ServiceID": f"{trx.timestamp.strftime('%m%d%H%M%S')}",
                        "POIID": f"{self._getPoiId()}"
                    },
                    "AbortRequest":{
                        "AbortReason":"MerchantAbort",
                        "MessageReference":{
                            "MessageCategory":"Payment",
                            "SaleID":"POSiMac",
                            "ServiceID": f"{serviceId}"
                        }
                    }
                }
                }

        self.logger.debug(self._url(featureURL) + " " + json.dumps(body))
        resp = self.post(self._url(featureURL), 
                        data=json.dumps(body), 
                        auth=self.auth,
                        verify=self._getVerifyFlag())
        trx.rsp_status_code = resp.status_code
        trx.rsp_text = resp.text
        if trx.rsp_status_code == 401:
            self.logger.warn(f"StatusCode:{trx.rsp_status_code}")
        else:
            self.logger.error(f"StatusCode:{trx.rsp_status_code} {trx.rsp_text}")
        return trx

    def status_transaction(self, trx, serviceId):
        featureURL = ""
        serviceId = trx.timestamp.strftime('%m%d%H%M%S')
        body = {
                "SaleToPOIRequest": {
                    "MessageHeader": {
                        "ProtocolVersion": "3.0",
                        "MessageClass": "Service",
                        "MessageCategory": "TransactionStatus",
                        "MessageType": "Request",
                        "SaleID": f"{self._getSaleId()}",
                        "ServiceID": f"{trx.timestamp.strftime('%m%d%H%M%S')}",
                        "POIID": f"{self._getPoiId()}"
                    },
                    "AbortRequest":{
                        "AbortReason":"MerchantAbort",
                        "MessageReference":{
                            "MessageCategory":"Payment",
                            "SaleID":"POSiMac",
                            "ServiceID": f"{serviceId}"
                        }
                    }
                }
                }

        self.logger.debug(self._url(featureURL) + " " + json.dumps(body))
        resp = self.post(self._url(featureURL), 
                        data=json.dumps(body), 
                        auth=self.auth,
                        verify=self._getVerifyFlag())
        trx.rsp_status_code = resp.status_code
        trx.rsp_text = resp.text
        if trx.rsp_status_code == 401:
            self.logger.warn(f"StatusCode:{trx.rsp_status_code} {json.dumps(json.loads(trx.rsp_text))}")
        else:
            self.logger.error(f"StatusCode:{trx.rsp_status_code} {trx.rsp_text}")
        return trx

    def diagnose_terminal(self, trx):
        featureURL = ""
        serviceId = trx.timestamp.strftime('%m%d%H%M%S')
        body = {
                "SaleToPOIRequest": {
                    "MessageHeader": {
                        "ProtocolVersion": "3.0",
                        "MessageClass": "Service",
                        "MessageCategory": "Diagnosis",
                        "MessageType": "Request",
                        "SaleID": f"{self._getSaleId()}",
                        "ServiceID": f"{trx.timestamp.strftime('%m%d%H%M%S')}",
                        "POIID": f"{self._getPoiId()}"
                    },
                    "DiagnosisRequest": {
                        "HostDiagnosisFlag": boolean(False)
                    }
                }
                }

        self.logger.debug(self._url(featureURL) + " " + json.dumps(body))
        resp = self.post(self._url(featureURL), 
                        data=json.dumps(body), 
                        auth=self.auth,
                        verify=self._getVerifyFlag())
        trx.rsp_status_code = resp.status_code
        trx.rsp_text = resp.text
        if trx.rsp_status_code == 401:
            self.logger.warn(f"StatusCode:{trx.rsp_status_code} {json.dumps(json.loads(trx.rsp_text))}")
        else:
            self.logger.error(f"StatusCode:{trx.rsp_status_code} {trx.rsp_text}")
        return trx

