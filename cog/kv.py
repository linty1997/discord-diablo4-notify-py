import workers_kv
from dotenv import load_dotenv
import os

load_dotenv()


class KV:
    def __init__(self, account_id, namespace_id, api_key):
        self.kv = workers_kv.Namespace(account_id=account_id, namespace_id=namespace_id, api_key=api_key)

        # self.kv = workers_kv.Namespace(account_id=os.getenv("KV_ACCOUNT"),
        #                                namespace_id=os.getenv("KV_NAMESPACE"),
        #                                api_key=os.getenv("KV_TOKEN"))

    def get_keys(self):
        return self.kv.list_keys()

    def get_val(self, key):
        return self.kv.read(key)

    def set_val(self, data: dict):
        self.kv.write(data)

    def del_key(self, key):
        self.kv.delete_one(key)

    def del_keys(self, keys: list):
        self.kv.delete_many(keys)


class KvData(KV):
    def __init__(self):
        super().__init__(os.getenv("KV_ACCOUNT"), os.getenv("KV_NAMESPACE_DATA"), os.getenv("KV_TOKEN"))

