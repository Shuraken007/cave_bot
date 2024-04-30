from PIL import Image, ImageFilter

import numpy as np
import cv2 as cv
from const import MAP_SIZE

colors = {
   'red': (234, 57, 43),
   'green': (120, 251, 79),
   'blue': (30, 31, 245),
}

def only_colors(img):
   r = colors['red']
   g = colors['green']
   width = img.size[0] 
   height = img.size[1]
   for i in range(0,width):# process all pixels
      for j in range(0,height):
         data = img.getpixel((i,j))
         if not((data[0] > r[0] and data[1] < r[1] and data[2] < r[2]) or \
            (data[0] < g[0] and data[1] > g[1] and data[2] < g[2])):
            img.putpixel((i,j),(0, 0, 0))
   return img

def only_colour(img):
   red, green, blue = img.split()

   # R, G, B = 0, 1, 2
   r = colors['red'][0]
   g = colors['green'][1]
   b = colors['blue'][2]
   d = 2

   red = red.point(lambda i: i > r-d and i < r+d and i or 0)
   green = green.point(lambda i: i > g-d and i < g+d and i or 0)
   blue = blue.point(lambda i: i > b-d and i < b+d and i or 0)
   # zeroed_band = red.point(lambda _: 0)

   # select regions where red is less than 100
   # mask = source[R].point(lambda i: i < r[0] and 0 or 255)
   # process the green band
   # source[G].paste(g_mask, None, g_mask)
   # paste the processed band back, but only where red was < 100
   # build a new multiband image
   img = Image.merge(img.mode, (red, green, blue))
   return img

def reduce_image(img):
   # result = img.convert('RGB')
   # result = img.convert('P', palette=Image.ADAPTIVE, colors=5)
   img = img.quantize(colors=3)
   # result = img.convert('RGB')
   # width = img.size[0] 
   # height = img.size[1]
   # for i in range(0,width):# process all pixels
   #    for j in range(0,height):
   #       data = img.getpixel((i,j))   
   #       # print(data)
   # print(result.getcolors())
   return img

def gray_scale(img):
   img = img.convert("L")
   th = [190, 195]
   th1 = [100, 120]
   img = img.point(lambda x: 255 if x > th[0] and x < th[1] or x > th1[0] and x < th1[1] else 0)
   return img

def MorphInc(img, count, size=3):
   for _ in range(count):
      img = img.filter(ImageFilter.MinFilter(size))
   return img

def MorphDec(img, count, size=3):
   for _ in range(count):
      img = img.filter(ImageFilter.MaxFilter(size))
   return img

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
   # 'red': {
   #    'lower': np.array([220, 0, 0,])[::-1],
   #    'upper': np.array([255, 100, 100,])[::-1],
   # },
   # 'green': {
   #    'lower': np.array([0, 210, 0,])[::-1],
   #    'upper': np.array([150, 255, 100,])[::-1],
   # },
   # 'blue': {
   #    'lower': np.array([0, 0, 220,])[::-1],
   #    'upper': np.array([100, 100, 255,])[::-1],
   # },
}

def only_cv_colour(img):
   mask_arr = []

   for mask_conf in masks.values():
      mask_arr.append(cv.inRange(img, mask_conf['lower'], mask_conf['upper']))

   total_mask = sum(mask_arr)
   img[np.where(total_mask==0)] = 0
   return img

def sort_bbox(boundingBoxes):
   # combine x and y as a single list and sort based on that 
   boundingBoxes = sorted(boundingBoxes, key=lambda b:b[0]+b[1], reverse=False)
   return boundingBoxes

def contours(img):
   imgray  = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
   contours, hierarchy = cv.findContours(imgray, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
   
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
         # rect = cv.minAreaRect(cnt)
         # box = cv.boxPoints(rect)
         # box = np.intp(box)
         # cv.drawContours(img, [box], 0, (0, 255, 255), 2)
         # shift = int( 0.1 * rect[1][0])
         coords.append((x,y, cnt))
      # elif val > 3:
      #    msg = 'aspect_ratio_rect: {:.2f}, area/perimeter: {:.2f}, fill_rect: {:.2f}' \
      #       .format(aspect_ratio, val, fill_rect)
      #    print(msg)

   # for x, y, width in x_y:
   #    print(width)
   #    # print(x, y)
   #    cv.rectangle(img, (x, y), (x+10, y+10),(0, 255, 255), 2)
   print(f'total_cells: {total_cells}')
   if total_cells != 400:
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
      print(mean_color)
      if abs(sum(mean_color) - 128) <= mean_delta and (abs(mean_color[1] - 128) <= mean_delta or abs(mean_color[0] - 128) <= mean_delta):
         safe_cells.append((j, i))
      i += 1
      if i > 20:
         j += 1
         i = 1
   return safe_cells

def grey_filter(img):
   gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
   thresh1 = cv.threshold(gray, 200, 255, cv.THRESH_OTSU)[1]
   # thresh1 = cv.threshold(gray, 200, 255, cv.THRESH_BINARY)[1]
   thresh2 = cv.threshold(gray, 120, 255, cv.THRESH_BINARY_INV)[1]

   # close_kernel = cv.getStructuringElement(cv.MORPH_RECT, (15,3))
   # close = cv.morphologyEx(thresh, cv.MORPH_CLOSE, close_kernel, iterations=1)

   # dilate_kernel = cv.getStructuringElement(cv.MORPH_RECT, (5,3))
   # dilate = cv.dilate(close, dilate_kernel, iterations=1)

   # cnts = cv.findContours(dilate, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
   # cnts = cnts[0] if len(cnts) == 2 else cnts[1]
   # for c in cnts:
   #    area = cv.contourArea(c)
   #    if area > 800 and area < 15000:
   #       x,y,w,h = cv.boundingRect(c)
   #       cv.rectangle(img, (x, y), (x + w, y + h), (222,228,251), -1)

   return thresh1, thresh2

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

def run(img, name):
   # img = cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)
   print(name)
   # img1, img2 = grey_filter(img)
   img = reduce_color_space(img, n_colors=8)
   kernel = np.ones((3, 3),np.uint8)
   img = cv.morphologyEx(img, cv.MORPH_OPEN, kernel)
   img = cv.morphologyEx(img, cv.MORPH_OPEN, kernel)
   img = cv.morphologyEx(img, cv.MORPH_CLOSE, kernel)
   # img = cv.morphologyEx(img, cv.MORPH_CLOSE, kernel)
   # img = cv.morphologyEx(img, cv.MORPH_CLOSE, kernel)
   img = only_cv_colour(img)


   safe_cells = contours(img)
   print(safe_cells)
   cv.imwrite(f'output/img/{name}', img)
   # cv.imwrite(f'output/img/th_{name}', img1)
   # cv.imwrite(f'output/img/th_inv_{name}', img2)
   print("\n")

if __name__ == '__main__':
   # img = Image.open('test_img_scan/test_screen.png')
   # img = only_colour(img)
   import os
   from os import listdir
   from os.path import isfile, join

   # dir = 'test_img_scan'
   # for file_name in os.listdir(dir):
   #    file_path = os.path.join(dir, file_name)
   #    if not os.path.isfile(file_path):
   #       continue
   #    img = cv.imread(file_path)
   #    run(img, file_name)
   img = cv.imread('test_img_scan/IMG_8250.png')
   run(img, 'image.png')

   # img = cv.imread('test_img_scan/test_screen.png')
   # # img = cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)
   # img = only_cv_colour(img)
   # safe_cells = contours(img)
   # print(safe_cells)
   # img = MorphDec(img, 2, 3)
   # img = MorphInc(img, 2, 5)
   # img = MorphDec(img, 2, 1)
   # img = gray_scale(img)
   # img = only_colors(img)
   # img = only_colors(img)

   # img = reduce_image(img)
   # img.save('output/img/test_screen.png')
   # cv.imwrite('output/img/test_screen.png', img)