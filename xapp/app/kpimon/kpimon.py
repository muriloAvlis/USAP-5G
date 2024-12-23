import sys
import time
import json
import logging
import threading
import ricxappframe.xapp_subscribe as subscribe
import ricxappframe.xapp_rest as ricrest

from ricxappframe.xapp_frame import rmr
from ricxappframe.e2ap.asn1 import IndicationMsg
from ricxappframe.xapp_frame import _BaseXapp
from ..e2sm.kpm_module import e2sm_types, e2sm_kpm_module


class SubscriptionWrapper(object):
    def __init__(self):
        self.e2sm_type = e2sm_types.E2SM_UNKNONW
        self.subscription_id = None  # Subscription ID used in RIC indication msgs
        self.e2_event_instance_id = None
        self.callback_func = None


class Kpimon(object):
    def __init__(self, config=None, http_server_port=8080, rmr_port=4560, rmr_flags=0x00):
        # Default config
        self.xAppEndpoint = "service-ricxapp-usap-xapp-http.ricxapp"
        self.MY_HTTP_SERVER_ADDRESS = "0.0.0.0"  # bind to all interfaces
        self.MY_HTTP_SERVER_PORT = http_server_port  # web server listen port
        self.MY_RMR_PORT = rmr_port  # rmr data port
        # Subscription manager address
        self.SUB_MGR_URI = "http://service-ricplt-submgr-http:8088/ric/v1"

        if config is not None:
            # TODO: check config vars in Config class
            pass

        self.baseXappFrame = _BaseXapp(
            self.MY_RMR_PORT, rmr_wait_for_ready=False, use_fake_sdl=True)

    def get_gnb_list(self) -> list:
        return self.baseXappFrame.get_list_gnb_ids()
