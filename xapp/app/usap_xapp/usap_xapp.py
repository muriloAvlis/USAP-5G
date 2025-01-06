import time
import json
import ricxappframe.xapp_subscribe as subscribe
import ricxappframe.xapp_rest as ricrest

from ricxappframe.xapp_frame import rmr
from ricxappframe.e2ap.asn1 import IndicationMsg
from ..e2sm.kpm_module import e2sm_types, e2sm_kpm_module


class SubscriptionWrapper(object):
    def __init__(self):
        self.e2sm_type = e2sm_types.E2SM_UNKNONW
        self.subscription_id = None  # Subscription ID used in RIC indication msgs
        self.e2_event_instance_id = None
        self.callback_func = None


class UsapXapp(object):
    def __init__(self, logger=None, http_server_port=8080, rmr_port=4560):
        # logger
        self.logger = logger
        self.logger.info('Running usap-xapp!')

        # Default config
        self.xAppEndpoint = "service-ricxapp-usap-xapp-http.ricxapp"
        self.MY_HTTP_SERVER_ADDRESS = "0.0.0.0"  # bind to all interfaces
        self.MY_HTTP_SERVER_PORT = http_server_port  # web server listen port
        self.MY_RMR_PORT = rmr_port  # rmr data port
        # Subscription manager address
        self.SUB_MGR_URI = 'http://service-ricplt-submgr-http.ricplt.svc:8088/ric/v1'
        self.E2_MGR_URI = 'http://service-ricplt-e2mgr-http.ricplt.svc:3800/v1/nodeb/'

        self.e2sm_kpm = e2sm_kpm_module(self)
        self.my_subscriptions = {}  # stores subscriptions
        self.running = False  # control variable

    def init_rmr(self):
        initbind = str(self.MY_RMR_PORT).encode('utf-8')
        self.rmr_client = rmr.rmr_init(
            initbind, rmr.RMR_MAX_RCV_BYTES, 0x00)
        while rmr.rmr_ready(self.rmr_client) == 0:  # wait for RMR ready
            self.logger.info('RMR is not ready, waiting...')
            time.sleep(1)

        rmr.rmr_set_stimeout(self.rmr_client, 1)  # msg timeout

        self.rmr_sbuf = rmr.rmr_alloc_msg(self.rmr_client, 2072)  # rmr buffer
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
            self.http_server.handler, "GET", "healthAlive", "/ric/v1/health/alive", self.healthyGetAliveHandler)
        self.http_server.handler.add_handler(
            self.http_server.handler, "GET", "healthReady", "/ric/v1/health/ready", self.healthyGetReadyHandler)

        # subscription CB
        if self.subscriber.ResponseHandler(self._subscription_response_callback, self.http_server) is not True:
            self.logger.error(
                'Error when trying to set the subscription reponse callback')

        # Start server
        self.http_server.start()

    def _subscription_response_callback(self, name, path, data, ctype):
        data = json.loads(data)
        SubscriptionId = data['SubscriptionId']
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

    def healthyGetReadyHandler(self, name, path, data, ctype):
        response = self._create_http_response()
        response['payload'] = ("{'status': 'ready'}")
        return response

    def healthyGetAliveHandler(self, name, path, data, ctype):
        response = self._create_http_response()
        response['payload'] = ("{'status': 'alive'}")
        return response

    def _create_http_response(self, status=200, response="OK"):
        return {'response': response, 'status': status, 'payload': None, 'ctype': 'application/json', 'attachment': None, 'mode': 'plain'}

    def start(self):
        self.running = True
        # Initialize RMR client
        self.init_rmr()

        # Initialize Subscriber to talk to Subscription Manager over REST API
        self.init_subscriber()

        # Initialize HTTP server
        self.init_http_server()

        # TODO: get E2 nodes IDs (SDL or REST?)
        while self.running:
            time.sleep(5)

    def stop(self):
        self.logger.warning('Stopping usap-xapp!')
        self.http_server.stop()  # stop http server
        rmr.rmr_close(self.rmr_client)  # stop rmr thread
        self.running = False
