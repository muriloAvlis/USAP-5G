import json

from usap.rnib.rnib import Rnib
from usap.e2sm.kpm_module import e2sm_types
from usap.e2sm.kpm_module import e2sm_kpm_module, e2sm_types
from usap.config.config import Config
from ricxappframe.e2ap.asn1 import IndicationMsg
from ricxappframe.xapp_frame import rmr


class SubscriptionWrapper(object):
    def __init__(self):
        self.e2sm_type = e2sm_types.E2SM_UNKNONW
        self.subscription_id = None  # Subscription ID used in RIC indication msgs
        self.e2_event_instance_id = None
        self.callback_func = None


class Kpimon():
    def __init__(self, subscriber, subEndpoint, subscriptionList, rmr_client, running):
        # R-NIB
        self.rnib = Rnib()

        # KPM Module
        self.e2sm_kpm = e2sm_kpm_module(self)

        # Logger
        self.logger = Config.get_logger()

        # Config
        self.config = Config()

        # Subs
        self.subscriber = subscriber
        self.subEndpoint = subEndpoint
        self.my_subscriptions = subscriptionList
        self.rmr_client = rmr_client
        self.running = running

    def subscription_callback(self, e2_node_id, subscription_id, indication_hdr, indication_msg, kpm_report_style, ue_id=None):
        if kpm_report_style == 2:
            self.logger.info('\nRIC Indication Received from {} for Subscription ID: {}, KPM Report Style: {}, UE ID: {}'.format(
                e2_node_id, subscription_id, kpm_report_style, ue_id))
        else:
            self.logger.info('\nRIC Indication Received from {} for Subscription ID: {}, KPM Report Style: {}'.format(
                e2_node_id, subscription_id, kpm_report_style))

        indication_hdr = self.e2sm_kpm.extract_hdr_info(indication_hdr)
        meas_data = self.e2sm_kpm.extract_meas_data(indication_msg)

        # TODO: just a test
        print(f'''\nE2SM-KPM RIC Indication Content: \n
                          \t Ind. Header: \n
                          \t\t ColletStartTime: {indication_hdr['colletStartTime']} \n
                          ''')
        print('\tMeasurements Data')
        granularity_period = meas_data.get('granulPeriod', None)

        if granularity_period is not None:
            print(f'\t\t GranularityPeriod: {granularity_period}')

        if kpm_report_style in [1, 2]:
            for metric_name, value in meas_data["measData"].items():
                print(f'\t\t Metric: {metric_name}, Value: {value}')
        else:
            for ue_id, ue_meas_data in meas_data['ueMeasData'].items():
                print(f'\t\tUE_ID: {ue_id}')

                granulPeriod = ue_meas_data.get("granulPeriod", None)
                if granulPeriod is not None:
                    print(f'\t\t GranularityPeriod: {granularity_period}')

                for metric_name, value in ue_meas_data["measData"].items():
                    print(f'\t\t Metric: {metric_name}, Value: {value}')

    def subscribe(self, e2_node_id, ran_function_id, event_trigger_def, action_def, indication_callback, e2sm_type=e2sm_types.E2SM_UNKNONW):
        # Now only 1 action in a Subscription Request
        action_id = 1

        # Need to transform byte data to bytearray for the REST request
        action_def = [action_def[i] for i in range(0, len(action_def))]

        subsequenteAction = self.subscriber.SubsequentAction(
            'continue', 'w10ms')

        actionDefinitionList = self.subscriber.ActionToBeSetup(
            action_id, "report", action_def, subsequenteAction)

        # Need to transform byte data to bytearray for the REST request
        event_trigger_def = [event_trigger_def[i]
                             for i in range(0, len(event_trigger_def))]

        xapp_event_instance_id = 1234  # TODO: what is this?????

        subsDetail = self.subscriber.SubscriptionDetail(
            xapp_event_instance_id, event_trigger_def, [actionDefinitionList])

        # Create and send RIC Subscription Request
        subReq = self.subscriber.SubscriptionParams(
            None, self.subEndpoint, e2_node_id, ran_function_id, None, [subsDetail])

        data, reason, status = self.subscriber.Subscribe(subReq)

        # Decode RIC Subscription Response
        subResponse = json.loads(data)
        subscription_id = subResponse['SubscriptionId']
        self.logger.info(
            f"Successfully subscribed with Subscription ID: {subscription_id}")

        # Wrapper to storages subscription informations
        subscriptionObj = SubscriptionWrapper()
        subscriptionObj.e2sm_type = e2sm_type
        subscriptionObj.subscription_id = subscription_id
        subscriptionObj.callback_func = indication_callback
        # Store active subscription in the dict
        self.my_subscriptions[subscription_id] = subscriptionObj

    def unsubscribe(self, subscription_id):
        self.logger.info(f"Unsubscribe Subscription ID: {subscription_id}")
        data, reason, status = self.subscriber.UnSubscribe(subscription_id)
        if (status == 204):
            self.logger.info(
                f"Successfully unsubscribed from Subscription ID: {subscription_id}")
        else:
            self.logger.error(
                f"Error during unsubscribing from Subscription ID: {subscription_id}")

    def unsubscribe_all(self):
        for e2_event_instance_id, subscriptionObj in self.my_subscriptions.items():
            self.unsubscribe(subscriptionObj.subscription_id)

    def _get_subscription_params(self, sm_name: str):
        '''Get subscription parameters from config file'''

        subscription_params = {}

        if self.config.controls['subscription'].get('subscriptionActive') == True:
            for sm in self.config.controls['subscription'].get('e2sm'):
                if sm['name'].upper() == sm_name.upper():
                    subscription_params = sm

        return subscription_params

    def rmr_loop(self):
        while self.running[0]:
            try:
                sbuf = rmr.rmr_torcv_msg(self.rmr_client, None, 100)
                summary = rmr.message_summary(sbuf)
            except Exception as e:
                continue

            if summary[rmr.RMR_MS_MSG_STATE] == 0:  # RMR_OK
                if (summary['message type'] == 12050):  # RIC INDICATION MESSAGE
                    e2_agent_id = str(summary['meid'].decode('utf-8'))
                    data = rmr.get_payload(sbuf)
                    try:
                        E2EventInstanceId = summary['subscription id']
                        ric_indication = IndicationMsg()
                        ric_indication.decode(data)
                        subscriptionObj = self.my_subscriptions.get(
                            E2EventInstanceId, None)
                        if subscriptionObj is None:  # if subscription not exist, ignore message
                            rmr.rmr_free_msg(sbuf)
                            continue

                        callback_func = subscriptionObj.callback_func
                        subscription_id = E2EventInstanceId

                        if callback_func is not None:
                            if (subscriptionObj.e2sm_type == e2sm_types.E2SM_KPM):
                                # if RIC Indication from E2SM-KPM then decode
                                indication_hdr, indication_msg = self.e2sm_kpm.decode_ric_indication(
                                    ric_indication)
                                callback_func(
                                    e2_agent_id, subscription_id, indication_hdr, indication_msg)
                            else:
                                # in other cases just pass undecoded byte data
                                callback_func(
                                    e2_agent_id, subscription_id, ric_indication.indication_header, ric_indication.indication_message)
                    except Exception as e:
                        self.logger.error(
                            "Error during RIC indication decoding: {}".format(e))
                        pass

                if (summary['message type'] == 12041):  # RIC CONTROL ACK
                    self.logger.info("Received RIC_CONTROL_ACK")
                if (summary['message type'] == 12042):  # RIC CONTROL FAILURE
                    self.logger.error("Received RIC_CONTROL_FAILURE")

            rmr.rmr_free_msg(sbuf)

    def start(self):
        nb_list = self.rnib.get_nbs_list()

        for nb in nb_list:
            if nb['connectionStatus'] == True:  # Connected E2 Node
                # Get KPM RAN Function Definition
                ran_function_def = self.rnib.get_ran_func_def_by_invetoryName(
                    nb['inventoryName'], self.e2sm_kpm.ran_func_id)

                if ran_function_def is None:
                    self.logger.warning(
                        f'E2 node {nb["inventoryName"]} does not support to E2SM-KPM RAN Function')
                    continue

                # RAN Function Definition (decoded)
                ran_function_def_decoded = self.e2sm_kpm.decode_ran_function_definition(
                    bytes.fromhex(ran_function_def))

                subscription_params = self._get_subscription_params('kpm')

                # Metric Names
                metric_names = self.rnib.get_metric_names_by_report_style(
                    ran_function_def_decoded, subscription_params['report_style_type'])

                # Check report style type and subscribe
                if subscription_params['report_style_type'] == 1:
                    self.logger.info(f"Subscribing to E2 Node: {nb['inventoryName']}, RAN Func: E2SM-KPM, Report Style: {subscription_params['report_style_type']}, Granularity Period: {subscription_params['granularity_period']}, Report Period: {subscription_params['reporting_period']}"
                                     )

                    self.e2sm_kpm.subscribe_report_service_style_1(
                        nb['inventoryName'],
                        subscription_params['reporting_period'],
                        metric_names,
                        subscription_params['granularity_period'],
                        self.subscription_callback)

                elif subscription_params['report_style_type'] == 2:
                    # need to bind also UE_ID to callback as it is not present in the RIC indication in the case of E2SM KPM Report Style 2
                    def subscription_callback(agent, sub, hdr, msg): return self.subscription_callback(
                        agent, sub, hdr, msg, subscription_params['report_style_type'], subscription_params['ue_list'][0].get('id'))

                    self.logger.info(f'''Subscribing to E2 Node: {
                                     nb['inventoryName']},
                                     RAN Func: E2SM-KPM,
                                     Report Style: {subscription_params['report_style_type']},
                                     Granularity Period: {subscription_params['granularity_period']},
                                     Report Period: {subscription_params['reporting_period']},
                                     UE ID: {subscription_params['ue_list'][0].get('id')}'''
                                     )

                    self.e2sm_kpm.subscribe_report_service_style_2(
                        nb['inventoryName'],
                        subscription_params['reporting_period'],
                        subscription_params['ue_list'][0].get('id'),
                        metric_names,
                        subscription_params['granularity_period'],
                        subscription_callback)
                elif subscription_params['report_style_type'] == 3:
                    if len(metric_names > 1):
                        metric_names = metric_names[0]
                        self.logger.warning(
                            f'Currently only 1 metric can be requested in E2SM-KPM Report Style 3, selected metric: {metric_names}')

                    # TODO: currently only dummy condition that is always satisfied, useful to get IDs of all connected UEs
                    # example matching UE condition: ul-rSRP < 1000
                    matchingConds = [{'matchingCondChoice': ('testCondInfo', {'testType': (
                        'ul-rSRP', 'true'), 'testExpr': 'lessthan', 'testValue': ('valueInt', 1000)})}]

                    self.logger.info(f'''Subscribing to E2 Node: {
                                     nb['inventoryName']},
                                     RAN Func: E2SM-KPM,
                                     Report Style: {subscription_params['report_style_type']},
                                     Granularity Period: {subscription_params['granularity_period']},
                                     Report Period: {subscription_params['reporting_period']}'''
                                     )

                    self.e2sm_kpm.subscribe_report_service_style_3(
                        nb['inventoryName'],
                        subscription_params['reporting_period'],
                        matchingConds,
                        metric_names,
                        subscription_params['granularity_period'],
                        self.subscription_callback)
                elif subscription_params['report_style_type'] == 4:
                    # TODO: currently only dummy condition that is always satisfied, useful to get IDs of all connected UEs
                    # example matching UE condition: ul-rSRP < 1000
                    matchingUeConds = [{'testCondInfo': {'testType': (
                        'ul-rSRP', 'true'), 'testExpr': 'lessthan', 'testValue': ('valueInt', 1000)}}]

                    self.logger.info(f'''Subscribing to E2 Node: {
                        nb['inventoryName']},
                     RAN Func: E2SM-KPM,
                     Report Style: {subscription_params['report_style_type']},
                     Granularity Period: {subscription_params['granularity_period']},
                     Report Period: {subscription_params['reporting_period']}'''
                                     )

                    self.e2sm_kpm.subscribe_report_service_style_4(
                        nb['inventoryName'],
                        subscription_params['reporting_period'],
                        matchingUeConds,
                        metric_names,
                        subscription_params['granularity_period'],
                        self.subscription_callback)
                elif subscription_params['report_style_type'] == 5:
                    if (len(subscription_params['ue_list']) < 2):
                        dummyUeId = subscription_params['ue_list'][0].get(
                            'id') + 1
                        subscription_params['ue_list'].append(dummyUeId)

                        self.logger.warning(
                            f'Subscription for E2SM-KPM Report Service Style 5 requires at least two UE IDs -> add dummy UeID: {dummyUeId}')

                    self.logger.info(f'''Subscribing to E2 Node: {
                        nb['inventoryName']},
                     RAN Func: E2SM-KPM,
                     Report Style: {subscription_params['report_style_type']},
                     Granularity Period: {subscription_params['granularity_period']},
                     Report Period: {subscription_params['reporting_period']}''')

                    self.e2sm_kpm.subscribe_report_service_style_5(
                        nb['inventoryName'], subscription_params['reporting_period'], subscription_params['ue_list'], metric_names, subscription_params['granularity_period'], self.subscription_callback)
                else:
                    self.logger.warning(f'''Subscription for E2SM-KPM Report Service Style {
                                        subscription_params['report_style_type']} is not supported''')
                    continue
            else:
                self.logger.warning(
                    f'E2 node {nb["inventoryName"]} disconnected, ignoring...')
                continue
