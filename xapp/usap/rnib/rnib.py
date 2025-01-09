import requests
import os

from usap.e2sm.utils import decode_plmn
from usap.config.config import Config


class Rnib(object):
    def __init__(self):
        self.logger = Config.get_logger()

        self.E2_MGR_HOST = os.getenv('E2MGR_HTTP_SERVICE_HOST')
        self.E2_MGR_PORT = os.getenv('E2MGR_HTTP_SERVICE_PORT')
        self.E2_MGR_URI = 'http://' + self.E2_MGR_HOST + \
            ':' + self.E2_MGR_PORT + '/v1/nodeb/'

    def get_nbs_list(self) -> list:
        nbList = []

        url = self.E2_MGR_URI + 'states'
        response = requests.get(url)

        if response.status_code == 200:
            self.logger.info('Get E2 Nodes from E2 Manager with success!')
            data = response.json()
            nbList.extend(data)

            for nb in nbList:
                # Convert to bool
                nb['connectionStatus'] = nb['connectionStatus'] == 'CONNECTED'

                # Change PLMN to decoded format
                mcc, mnc = decode_plmn(nb['globalNbId'].get('plmnId'))
                nb['globalNbId']['plmnId'] = mcc + mnc
        else:
            self.logger.warning(f'''Unable to get E2 nodes [{
                response.status_code}]''')

        return nbList

    def get_ran_func_def_by_invetoryName(self, inventory_name, ran_func_id):
        url = self.E2_MGR_URI + inventory_name
        response = requests.get(url)

        if response.status_code == 200:
            self.logger.info(
                'Get RAN Function Definition from E2 Manager with success!')
            data = response.json()
            ran_functions = data['gnb']['ranFunctions']

            for rf in ran_functions:
                if rf['ranFunctionId'] == ran_func_id:
                    return rf['ranFunctionDefinition']

        self.logger.warning(f'''Unable to get RAN Function Definition to E2 Node {inventory_name} [{
            response.status_code}]''')

        return None

    def get_metric_names_by_report_style(self, ran_func_def: dict, report_style_type: int):
        return [
            metric['measName']
            for report_style in ran_func_def.get('ric-ReportStyle-List', [])
            if report_style.get('ric-ReportStyle-Type') == report_style_type
            for metric in report_style.get('measInfo-Action-List', [])
        ]


# tests
# if __name__ == '__main__':
#     rnib = Rnib()
#     kpm_packer = e2sm_kpm_packer()
#     nbList = rnib.get_nbs_list()

#     for nb in nbList:
#         print(60 * '*')
#         inventory_name = nb['inventoryName']
#         print(f'RAN NAME: {inventory_name}')
#         rf_def = rnib.get_ran_func_def_by_invetoryName(inventory_name, 2)
#         rf_def_bytes = bytes.fromhex(rf_def)
#         rf_def_decoded = kpm_packer.decode_ran_function_definition(
#             rf_def_bytes)

#         metric_names = rnib.get_metric_names_by_report_style(rf_def_decoded, 4)
#         print(metric_names)
