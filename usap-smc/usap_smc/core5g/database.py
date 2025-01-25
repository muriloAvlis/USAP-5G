from usap_smc.logger.logger import Log
from usap_smc.core5g.mongodb import MongoConnection

from loguru import logger


class Database(MongoConnection):
    def __init__(self):
        super().__init__()
        self.collection = self.get_collection()

    def get_ue_by_imsi(self, imsi: str):
        """Get UE by IMSI"""
        query = {"imsi": imsi}

        uePdu = self.collection.find_one(query)

        return uePdu

    def check_ue_in_slice(self, imsi: str, sst: int) -> bool:
        """Check if UE is in slice with SST"""
        query = {
            "imsi": imsi,
            "slice": {"$elemMatch": {"sst": sst}}
        }

        res = self.collection.find_one(query)

        if res:
            return True

        return False

    def update_ue_slice_by_imsi(self, imsi: str, sst: int):
        """Update UE's SST by IMSI"""
        filter = {"imsi": imsi}
        update_query = {"$set": {"slice.0.sst": sst}}

        res = self.collection.update_one(filter, update_query)

        if res.modified_count > 0:
            logger.info(f"SST {sst} atualizado para a UE {imsi} no 5GC")
        else:
            logger.error(f"Erro ao atualizar SST da UE {imsi}")

    def stop(self):
        # Close mongodb connection
        self.close()
