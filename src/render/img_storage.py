class ImageStorage:
   def __init__(self) -> None:
      self.storage = {}
      pass

   def key_arr_to_str(self, key_arr):
      return "_".join([str(x) for x in key_arr])

   def add_image(self, key_arr, image):
      key = self.key_arr_to_str(key_arr)
      self.storage[key] = image

   def get_image(self, key_arr):
      key = self.key_arr_to_str(key_arr)
      return self.storage.get(key)
   
   def reset(self):
      self.storage = {}
