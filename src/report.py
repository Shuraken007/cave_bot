from collections import OrderedDict

class Report:
   def add_reaction(self, reaction):
      if self.off:
         return
      
      if reaction not in self.reactions:
         self.reactions[reaction] = 0

      self.reactions[reaction] += 1

   def add_error(self, error: str):
      if self.off:
         return

      self.errors[self.key].append(error)

   def add_message(self, message: str):
      if self.off:
         return

      self.messages[self.key].append(message)

   def add_log(self, data):
      if self.off:
         return

      self.log[self.key].update(data)

   def get_log(self, key):
      if self.off:
         return None

      if key is None:
         key = self.key

      log = self.log[key]
      if len(log.keys()) > 0:
         return log
      return None
   
   def get_errors(self, key):
      if self.off:
         return None

      if key is None:
         key = self.key

      errors = self.errors[key]
      if len(errors) > 0:
         return errors
      return None
   
   def get_messages(self, key):
      if self.off:
         return None

      if key is None:
         key = self.key

      messages = self.messages[key]
      if len(messages) > 0:
         return messages
      return None
   
   def get_reactions(self):
      if self.off:
         return None
         
      if len(self.reactions.keys()) > 0:
         return self.reactions
      return None

   def set_key(self, key):
      self.key = key
      if key in self.keys:
         return
      self.log[key] = {}
      self.messages[key] = []
      self.errors[key] = []
      self.keys.append(key)

   def get_key(self):
      return self.key

   def get_keys(self):
      return self.keys

   def __init__(self):
      self.reactions = OrderedDict()
      self.messages = {}
      self.errors = {}
      self.log = {}
      self.off = False
      self.keys = []