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

def contours(img, report):
   imgray  = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
   contours, _ = cv.findContours(imgray, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
   
   coords = []
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
         coords.append((x,y, cnt))
     
   if total_cells != 400:
      report.add_reaction(r.user_data_wrong)
      report.add_error(f'detected {total_cells}/400, required 400')
      return None
   sorter = lambda x: (x[1], x[0])
   coords_sorted = sorted(coords, key=sorter)
   
   safe_cells = []
   i, j = 1, 1
   mean_delta = 30
   for x, y, cnt in coords_sorted:
      mask = np.zeros(imgray.shape,np.uint8)
      cv.drawContours(mask,[cnt],0,255,-1)      
      mean_color = cv.mean(img, mask)
      if abs(sum(mean_color) - 128) <= mean_delta and (abs(mean_color[1] - 128) <= mean_delta or abs(mean_color[0] - 128) <= mean_delta):
         safe_cells.append((j, i))
      i += 1
      if i > 20:
         j += 1
         i = 1
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

if __name__ == '__main__':
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