import time
import json
import threading
import os
import requests

import ricxappframe.xapp_subscribe as subscribe
import ricxappframe.xapp_rest as ricrest

from ricxappframe.xapp_frame import rmr
from usap.config.config import Config
from usap.usap_xapp.kpimon import Kpimon
from usap.asn1coder.e2sm_kpm_packer import e2sm_kpm_packer
from usap.rnib.rnib import Rnib


class UsapXapp(object):
    def __init__(self, http_server_port=8080, rmr_port=4560):
        self._config = Config()

        # Logger
        self.logger = Config.get_logger()

        # Default config
        self.xAppEndpoint = "service-ricxapp-usap-xapp-http.ricxapp"
        self.rmr_endpoint = "service-ricxapp-usap-xapp-rmr.ricxapp"

        self.MY_HTTP_SERVER_ADDRESS = "0.0.0.0"  # bind to all interfaces
        self.MY_HTTP_SERVER_PORT = http_server_port  # web server listen port
        self.MY_RMR_PORT = rmr_port  # rmr data port

        # Subscription manager address # TODO: how do it be dinamyc?
        self.SUB_MGR_URI = 'http://service-ricplt-submgr-http.ricplt:8088/ric/v1'
        self.APP_MGR_URL = 'http://service-ricplt-appmgr-http.ricplt:8080/ric/v1'

        # HTTP server
        self.http_server = None

        # RMR thread
        self.rmr_loop_thread = None

        self.kpimon = None

        self.e2sm_kpm = e2sm_kpm_packer()
        self.rnib = Rnib()

        self.my_subscriptions = {}  # stores subscriptions
        # TODO: ugly ugly, it need be better
        self.running = [False]  # control variable | list is mutable

    def init_rmr(self):
        initbind = str(self.MY_RMR_PORT).encode('utf-8')
        self.rmr_client = rmr.rmr_init(
            initbind, rmr.RMR_MAX_RCV_BYTES, 0x00)
        # wait for RMR ready
        while rmr.rmr_ready(self.rmr_client) == 0 and self.running[0] == True:
            self.logger.info('RMR is not ready, waiting...')
            time.sleep(1)

        rmr.rmr_set_stimeout(self.rmr_client, 1)  # msg timeout

        self.rmr_sbuf = rmr.rmr_alloc_msg(self.rmr_client, 2000)  # rmr buffer
        time.sleep(0.1)

    def init_subscriber(self):
        # Initialize Subscriber
        self.subscriber = subscribe.NewSubscriber(self.SUB_MGR_URI)
        # Initialize subEndPoint with my IP and ports
        self.subEndpoint = self.subscriber.SubscriptionParamsClientEndpoint(
            self.xAppEndpoint, self.MY_HTTP_SERVER_PORT, self.MY_RMR_PORT)

    def init_http_server(self):
        # Create a HTTP server and set the URI handler callbacks
        self.http_server = ricrest.ThreadedHTTPServer(
            self.MY_HTTP_SERVER_ADDRESS, self.MY_HTTP_SERVER_PORT)

        # handlers
        self.http_server.handler.add_handler(
            self.http_server.handler, "GET", "healthAlive", "/ric/v1/health/alive", self._healthyGetAliveHandler)
        self.http_server.handler.add_handler(
            self.http_server.handler, "GET", "healthReady", "/ric/v1/health/ready", self._healthyGetReadyHandler)

        # subscription CB
        if self.subscriber.ResponseHandler(self._subscription_response_callback, self.http_server) is not True:
            self.logger.error(
                'Error when trying to set the subscription reponse callback')

        # Start server
        self.http_server.start()

    def _subscription_response_callback(self, name, path, data, ctype):
        data = json.loads(data)
        SubscriptionId = data['SubscriptionId']
        print(SubscriptionId)
        # subscription ID used in RIC indication
        E2EventInstanceId = data['SubscriptionInstances'][0]['E2EventInstanceId']
        self.logger.info('Received Subscription ID to E2EventInstanceId mapping: {} -> {}'.format(
            SubscriptionId, E2EventInstanceId))
        if SubscriptionId in self.my_subscriptions:
            self.my_subscriptions[SubscriptionId].e2_event_instance_id = E2EventInstanceId
            # update the key, as it is more convenient to use E2EventInstanceId that is used in RIC indication msgs
            self.my_subscriptions[E2EventInstanceId] = self.my_subscriptions.pop(
                SubscriptionId)

        response = self._create_http_response()
        response['payload'] = ("{}")
        return response

    def _healthyGetReadyHandler(self, name, path, data, ctype):
        response = self._create_http_response()
        response['payload'] = ("{'status': 'ready'}")
        return response

    def _healthyGetAliveHandler(self, name, path, data, ctype):
        response = self._create_http_response()
        response['payload'] = ("{'status': 'alive'}")
        return response

    def _create_http_response(self, status=200, response="OK"):
        return {'response': response, 'status': status, 'payload': None, 'ctype': 'application/json', 'attachment': None, 'mode': 'plain'}

    def _register_xapp(self):
        hostname = os.getenv("HOSTNAME")
        xapp_name = self._config.get_item_by_key("name")
        xapp_version = self._config.get_item_by_key("version")

        http_endpoint = self.xAppEndpoint
        rmr_endpoint = self.rmr_endpoint

        request = {
            "appName": hostname,
            "appVersion": xapp_version,
            "configPath": "",
            "appInstanceName": xapp_name,
            "httpEndpoint": http_endpoint,
            "rmrEndpoint": rmr_endpoint,
            "config": json.dumps(self._config.cfg)
        }

        resp = requests.post(self.APP_MGR_URL + "/register", json=request)

        if resp.status_code in [200, 201]:
            self.logger.debug("xApp registered in App Manager with success!")
            return

        self.logger.warning("Unable to register in App Manager!")

    def start(self):
        self.logger.info('Running usap-xapp!')

        ranFuncDecodedDuNode = self.e2sm_kpm.decode_ran_function_definition(bytes.fromhex("60304F52414E2D4532534D2D4B504D000018312E332E362E312E342E312E35333134382E312E322E322E3205004B504D204D6F6E69746F720001010700506572696F646963205265706F7274010110010109004532204E6F6465204D6561737572656D656E740101000F01E04452422E416972496644656C6179556C03604452422E5061636B65745375636365737352617465556C674E42557501A04452422E526C6344656C6179556C02C04452422E526C635061636B657444726F7052617465446C02004452422E526C6353647544656C6179446C03804452422E526C635364755472616E736D6974746564566F6C756D65444C03804452422E526C635364755472616E736D6974746564566F6C756D65554C01404452422E5545546870446C01404452422E5545546870556C0260524143482E507265616D626C6544656443656C6C01A05252552E507262417661696C446C01A05252552E507262417661696C556C01605252552E507262546F74446C01605252552E507262546F74556C01805252552E50726255736564446C01805252552E50726255736564556C0101010100010211004532204E6F6465204D6561737572656D656E7420666F7220612073696E676C652055450102000E01E04452422E416972496644656C6179556C03604452422E5061636B65745375636365737352617465556C674E42557501A04452422E526C6344656C6179556C02C04452422E526C635061636B657444726F7052617465446C02004452422E526C6353647544656C6179446C03804452422E526C635364755472616E736D6974746564566F6C756D65444C03804452422E526C635364755472616E736D6974746564566F6C756D65554C01404452422E5545546870446C01404452422E5545546870556C01A05252552E507262417661696C446C01A05252552E507262417661696C556C01605252552E507262546F74446C01605252552E507262546F74556C01805252552E50726255736564446C01805252552E50726255736564556C010101010001031600436F6E646974696F6E2D62617365642C2055452D6C6576656C204532204E6F6465204D6561737572656D656E740103000E01E04452422E416972496644656C6179556C03604452422E5061636B65745375636365737352617465556C674E42557501A04452422E526C6344656C6179556C02C04452422E526C635061636B657444726F7052617465446C02004452422E526C6353647544656C6179446C03804452422E526C635364755472616E736D6974746564566F6C756D65444C03804452422E526C635364755472616E736D6974746564566F6C756D65554C01404452422E5545546870446C01404452422E5545546870556C01A05252552E507262417661696C446C01A05252552E507262417661696C556C01605252552E507262546F74446C01605252552E507262546F74556C01805252552E50726255736564446C01805252552E50726255736564556C010101020001041580436F6D6D6F6E20436F6E646974696F6E2D62617365642C2055452D6C6576656C204D6561737572656D656E740104000E01E04452422E416972496644656C6179556C03604452422E5061636B65745375636365737352617465556C674E42557501A04452422E526C6344656C6179556C02C04452422E526C635061636B657444726F7052617465446C02004452422E526C6353647544656C6179446C03804452422E526C635364755472616E736D6974746564566F6C756D65444C03804452422E526C635364755472616E736D6974746564566F6C756D65554C01404452422E5545546870446C01404452422E5545546870556C01A05252552E507262417661696C446C01A05252552E507262417661696C556C01605252552E507262546F74446C01605252552E507262546F74556C01805252552E50726255736564446C01805252552E50726255736564556C0101010300010511804532204E6F6465204D6561737572656D656E7420666F72206D756C7469706C65205545730105000E01E04452422E416972496644656C6179556C03604452422E5061636B65745375636365737352617465556C674E42557501A04452422E526C6344656C6179556C02C04452422E526C635061636B657444726F7052617465446C02004452422E526C6353647544656C6179446C03804452422E526C635364755472616E736D6974746564566F6C756D65444C03804452422E526C635364755472616E736D6974746564566F6C756D65554C01404452422E5545546870446C01404452422E5545546870556C01A05252552E507262417661696C446C01A05252552E507262417661696C556C01605252552E507262546F74446C01605252552E507262546F74556C01805252552E50726255736564446C01805252552E50726255736564556C01010103"))
        ranFuncDecodedCuNode = self.e2sm_kpm.decode_ran_function_definition(bytes.fromhex("60304F52414E2D4532534D2D4B504D000018312E332E362E312E342E312E35333134382E312E322E322E3205004B504D204D6F6E69746F720001010700506572696F646963205265706F7274010110010109004532204E6F6465204D6561737572656D656E740101000002604452422E5064637052656F726444656C6179556C0101010100010211004532204E6F6465204D6561737572656D656E7420666F7220612073696E676C652055450102000002604452422E5064637052656F726444656C6179556C010101010001031600436F6E646974696F6E2D62617365642C2055452D6C6576656C204532204E6F6465204D6561737572656D656E740103000002604452422E5064637052656F726444656C6179556C010101020001041580436F6D6D6F6E20436F6E646974696F6E2D62617365642C2055452D6C6576656C204D6561737572656D656E740104000002604452422E5064637052656F726444656C6179556C0101010300010511804532204E6F6465204D6561737572656D656E7420666F72206D756C7469706C65205545730105000002604452422E5064637052656F726444656C6179556C01010103"))

        metricsDu = self.rnib.get_metric_names_by_report_style(
            ranFuncDecodedDuNode, 4)

        metricsCu = self.rnib.get_metric_names_by_report_style(
            ranFuncDecodedCuNode, 4)

        print(metricsDu)

        print(metricsCu)

        # Event trigger
        evTriggerDef = self.e2sm_kpm.encode_event_trigger_def(1000)

        evTriggerDef = [evTriggerDef[i]
                        for i in range(0, len(evTriggerDef))]

        print(evTriggerDef)

        # Action definition
        matchingUeConds = [{'testCondInfo': {'testType': (
            'ul-rSRP', 'true'), 'testExpr': 'lessthan', 'testValue': ('valueInt', 1000)}}]
        actDefFmt4Du = self.e2sm_kpm.encode_action_def_format4(
            matchingUeConds, metricsDu, 1000)
        actDefFmt4Du = [actDefFmt4Du[i]
                        for i in range(0, len(actDefFmt4Du))]
        # print(actDefFmt4Du)

        actDefFmt4Cu = self.e2sm_kpm.encode_action_def_format4(
            matchingUeConds, metricsCu, 1000)
        actDefFmt4Cu = [actDefFmt4Cu[i]
                        for i in range(0, len(actDefFmt4Cu))]
        print(actDefFmt4Cu)

        # self.running[0] = True
        # # Initialize RMR client
        # self.init_rmr()

        # # Initialize Subscriber to talk to Subscription Manager over REST API
        # self.init_subscriber()

        # # Initialize HTTP server
        # self.init_http_server()

        # # Register xApp
        # self._register_xapp()

        # # Initialize kpimon module
        # self.kpimon = Kpimon(
        #     self.subscriber, self.subEndpoint, self.my_subscriptions, self.rmr_client, self.running)
        # self.kpimon.start()

        # # Thread for handle rmr messages
        # self.rmr_loop_thread = threading.Thread(target=self.kpimon.rmr_loop)
        # self.rmr_loop_thread.start()

    def stop(self):
        self.logger.warning('Stopping usap-xapp!')

        self.running[0] = False

        if self.kpimon is not None:
            self.kpimon.unsubscribe_all()

        if self.http_server is not None:
            self.http_server.stop()  # stop http server

        # Wait for RMR loop finish
        if self.rmr_loop_thread is not None:
            self.rmr_loop_thread.join()

        rmr.rmr_close(self.rmr_client)  # stop rmr thread
