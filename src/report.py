from collections import OrderedDict

class BaseStorage():
   def __init__(self):
      self.off = False

   def off(self):
      self.off = True

   def on(self):
      self.off = False

   def add(self, entity):
      raise Exception(f'abstract method')

   def get(self, key):
      raise Exception(f'abstract method')


class KeyStorage(BaseStorage):
   def __init__(self, name):
      super().__init__()
      self.data = {}
      self.name = name
      self.key = None

   def set_key(self, key):
      self.key = key
      if key in self.data:
         return
      self.data[key] = []

   def add(self, entity):
      if self.off:
         return
      if self.key is None:
         raise Exception(f'report key is not set for storage {self.name}')
      if type(entity) != list:
         entity = [entity]
      
      self.data[self.key].extend(entity)

   def get(self, key):
      if self.off:
         return None

      if key is None:
         raise Exception(f'key is not set on getting data for storage {self.name}')

      data = self.data.get(key, None)

      if data is None or len(data) == 0:
         return None

      return data

class ArrayStorage(BaseStorage):
   def __init__(self):
      super().__init__()
      self.data = []

   def add(self, entity):
      if self.off:
         return
      
      if type(entity) != list:
         entity = [entity]

      self.data.extend(entity)

   def get(self):
      if self.off:
         return None

      if len(self.data) == 0:
         return None
   
      return self.data
   
class CounterStorage(BaseStorage):
   def __init__(self):
      super().__init__()
      self.data = {}

   def add(self, entity):
      if self.off:
         return
      
      if type(entity) != list:
         entity = [entity]

      for e in entity:
         if e not in self.data:
            self.data[e] = 0

         self.data[e] += 1

   def get(self):
      if self.off:
         return None

      if len(self.data.keys()) == 0:
         return None
   
      return self.data

class Report:
   def set_key(self, key):
      self.key = key
      if key in self.keys:
         return

      self.keys.append(key)

      for storage in [self.msg, self.err, self.log]:
         storage.set_key(key)

      if key not in self.__inner_keys:
         self.reported_keys_amount += 1

   def dump_to_logger(self, logger):
      for key in self.keys:
         if data:= self.log.get(key):
            logger.dump_msg(data, 'log', mode='dump')

   def get_msg_arr_by_key(self, key, is_indent = False):
      msg_arr = []
      if messages:= self.msg.get(key):
         msg_arr.extend(messages)
      if errors:= self.err.get(key):
         msg_arr.extend(errors)
      
      if is_indent:
         msg_arr = ['\t' + x for x in msg_arr]

      return msg_arr
   
   def is_key_reported(self, key):
      if key in self.__inner_keys:
         return False
      
      if self.reported_keys_amount <= 1:
         return False

      return True


   def build_msg_arr(self):
      arr = []
      for key in self.keys:
         is_key_reported = self.is_key_reported(key)

         arr_by_key = self.get_msg_arr_by_key(key, is_indent = is_key_reported)
         if len(arr_by_key) == 0:
            continue
         if is_key_reported:
            arr.append(key + ':')

         arr.extend(arr_by_key)

      if reaction_data:= self.reaction_msg.get():
         if len(arr) > 0:
            arr.append('')
         arr.extend(reaction_data)

      return arr

   def off(self):
      for storage in self.storages:
         storage.off()

      self.off = True

   def on(self):
      for storage in self.storages:
         storage.on()

      self.off = False

   def __init__(self):
      self.off = False

      self.msg = KeyStorage('msg')
      self.err = KeyStorage('err')
      self.log = KeyStorage('log')

      self.reaction = CounterStorage()
      self.reaction_msg = ArrayStorage()

      self.image = ArrayStorage()

      self.storages = [self.msg, self.err, self.log, self.reaction_msg, self.reaction, self.image]

      self.keys = []

      self.reported_keys_amount = 0
      self.__default_key = 'default'
      self.__inner_keys = [self.__default_key]

      self.set_key(self.__default_key)