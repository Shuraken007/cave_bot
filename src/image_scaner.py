import numpy as np
import cv2 as cv
from const import MAP_SIZE
from reaction import Reactions as r
import requests

masks = {
   'red': {
      'lower': np.array([128, 0, 0,])[::-1],
      'upper': np.array([128, 0, 0,])[::-1],
   },
   'green': {
      'lower': np.array([0, 128, 0,])[::-1],
      'upper': np.array([0, 128, 0,])[::-1],
   },
   'blue': {
      'lower': np.array([0, 0, 128,])[::-1],
      'upper': np.array([0, 0, 128,])[::-1],
   },
}

def only_cv_colour(img):
   mask_arr = []

   for mask_conf in masks.values():
      mask_arr.append(cv.inRange(img, mask_conf['lower'], mask_conf['upper']))

   total_mask = sum(mask_arr)
   img[np.where(total_mask==0)] = 0
   return img

def get_cell_coords(x, y, minmax_arr):
   w = minmax_arr[2] - minmax_arr[0]
   h = minmax_arr[3] - minmax_arr[1]
   cell_w = int(w / (MAP_SIZE[0] - 1))
   cell_y = int(h / (MAP_SIZE[1] - 1))

   i = round((x - minmax_arr[0]) / cell_w) + 1
   j = round((y - minmax_arr[1]) / cell_y) + 1
   return i, j

def min_max_coords(x, y, arr = None):
   if arr is None:
      arr = [x, y, x, y]
   arr[0] = min(arr[0], x)
   arr[1] = min(arr[1], y)
   arr[2] = max(arr[2], x)
   arr[3] = max(arr[3], y)
   return arr

def contours(img, report):
   imgray  = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
   contours, _ = cv.findContours(imgray, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
   
   coords = []
   minmax_arr = None
   total_cells = 0
   for cnt in contours:
      area = int(cv.contourArea(cnt))
      if not area > 0:
         continue
      perimeter = int(cv.arcLength(cnt, True))
      if not perimeter > 0:
         continue
      val = area / perimeter

      x,y,w,h = cv.boundingRect(cnt)
      aspect_ratio = float(w)/h      
      rect_area = w * h
      fill_rect = float(area)/rect_area
      if val > 3 and 0.9 <= aspect_ratio <= 1.3 and 0.6 <= fill_rect:
         total_cells += 1
         minmax_arr = min_max_coords(x, y, minmax_arr)
         coords.append((x, y, cnt))
     
   if total_cells != 400:
      report.add_reaction(r.user_data_wrong)
      report.add_error(f'detected {total_cells}/400, required 400')
      return None
   
   safe_cells = []
   mean_delta = 30
   for x, y, cnt in coords:
      i, j = get_cell_coords(x, y, minmax_arr)
      mask = np.zeros(imgray.shape,np.uint8)
      cv.drawContours(mask,[cnt],0,255,-1)      
      mean_color = cv.mean(img, mask)
      if abs(sum(mean_color) - 128) <= mean_delta and (abs(mean_color[1] - 128) <= mean_delta or abs(mean_color[0] - 128) <= mean_delta):
         safe_cells.append((j, i))
   return safe_cells

def is_cube(n):
    cbrt = np.cbrt(n)
    return cbrt ** 3 == n, int(cbrt)

def reduce_color_space(img, n_colors=64):
    n_valid, cbrt = is_cube(n_colors)

    if not n_valid:
        print("n_colors should be a perfect cube")
        return

    n_bits = int(np.log2(cbrt))

    if n_bits > 8:
        print("Can't generate more colors")
        return

    bitmask = int(f"{'1' * n_bits}{'0' * (8 - n_bits)}", 2)

    return img & bitmask

def get_safe_cells(img, report):
   img = reduce_color_space(img, n_colors=8)
   kernel = np.ones((3, 3),np.uint8)
   img = cv.morphologyEx(img, cv.MORPH_OPEN, kernel)
   img = cv.morphologyEx(img, cv.MORPH_OPEN, kernel)
   img = cv.morphologyEx(img, cv.MORPH_CLOSE, kernel)
   img = only_cv_colour(img)
   safe_cells = contours(img, report)
   return safe_cells

def url_to_image(url):
   resp = requests.get(url, stream=True).raw
   image = np.asarray(bytearray(resp.read()), dtype="uint8")
   return cv.imdecode(image, cv.IMREAD_COLOR)

# if __name__ == '__main__':
   # import os
   # from os import listdir
   # from os.path import isfile, join

   # dir = 'test_img_scan'
   # for file_name in os.listdir(dir):
   #    file_path = os.path.join(dir, file_name)
   #    if not os.path.isfile(file_path):
   #       continue
   #    img = cv.imread(file_path)
   #    run(img, file_name)
   # img = cv.imread('test_img_scan/IMG_8250.png')
   # safe_cells = get_safe_cells(img, 'image.png')
   # print(safe_cells)