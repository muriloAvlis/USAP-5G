from ngap_compiled import NGAP_PDU_Descriptions
import os
import base64


class ngap_packer(object):
    def __init__(self) -> None:
        tmp = base64.b64decode("NzI2NTcxNzA2MTcyNzQ=")
        print(tmp)
        # self.test = NGAP_PDU_Descriptions.InitiatingMessage.from_aper(bta)


test = ngap_packer()

# print(test.test)
