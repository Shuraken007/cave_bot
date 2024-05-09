import os
import json

from .utils import build_path

class Logger:
    def dump_msg(self, msg, file_name, mode=None):
        default = lambda o: f"<<non-serializable: {type(o).__qualname__}>>"

        file_path = os.path.join(self.output_dir, file_name)
        with open(file_path, 'a+', encoding='utf8') as f:
            prepared_msg = msg
            if mode == 'dump':
                prepared_msg = json.dumps(msg, indent=4, ensure_ascii=False, default=default)
            elif mode == 'unique':
                assert isinstance(msg, str), 'msg must be string for uniq mode'
                if self.unique_hash.get(msg):
                    return
                else:
                    self.unique_hash[msg] = True
            f.write(str(prepared_msg) + '\n')

    def __init__(self, output_dir):
        self.unique_hash = {}
        self.output_dir = build_path([output_dir], None, mkdir = True)
