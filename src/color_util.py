def ansi_message_start():
   return "```ansi"

def ansi_message_end():
   return "```"

color_aliases_foreground = {
   'gray' : 30,
   'red' : 31,
   'green' : 32,
   'yellow' : 33,
   'blue' : 34,
   'pink' : 35,
   'cyan' : 36,
   'white' : 37,
}

color_aliases_background = {
   'firefly dark blue': 40,
   'orange': 41,
   'marble blue': 42,
   'greyish turquoise': 43,
   'gray': 44,
   'indigo': 45,
   'light gray': 46,
   'white': 47,
}

def get_open_code(fg_color_alias, bg_color_alias):
   format = 0 # normal
   color_bg, color_fg = None, None
   if bg_color_alias:
      color_bg = color_aliases_background[bg_color_alias]
   if fg_color_alias:
      color_fg = color_aliases_foreground[fg_color_alias]
   
   if color_bg and color_fg:
      color = "{};{}".format(color_bg, color_fg)
   elif color_fg:
      color = "{}".format(color_fg)
   elif color_bg:
      color = "{}".format(color_bg)

   open_code = "\u001b[{};{}m".format(format, color)
   return open_code

def get_close_code():
   return "\u001b[0m"

def color_msg(msg, fg_color_alias, bg_color_alias):
   open_code = get_open_code(fg_color_alias, bg_color_alias)
   close_code = get_close_code()
   return open_code + msg + close_code

def is_text_black(bg):
   r = bg[0]
   g = bg[1]
   b = bg[2]
   t = bg[3]
   nThreshold = 50
   bgDelta = r*0.299 + g*0.587 + b*0.114
   if bgDelta > nThreshold:
      return True
   return False