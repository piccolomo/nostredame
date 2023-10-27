import numpy as np
import re, sys


# Escape Codes 

def simple_print(simple = True):
    global bold_escape
    global end_escape
    global delete_line_escape

    bold_escape = '' if simple else '\x1b[1m'
    end_escape = '' if simple else '\x1b[0m'
    delete_line_escape = '' if simple else '\033[A\033[2K'

simple_print(False)

nl = "\n"
percentage = lambda num, total = 1: 100 * num / total
bold = lambda string: bold_escape + string + end_escape
enclose_squared = lambda string: '[' + str(string) + ']' if string != "" else string
enclose_circled = lambda string: '(' + str(string) + ')' if string != "" else string


def pad(string, length = 6): # 25.69 or 100.0
    string = str(string)
    ls = len(string)
    #length = ls if length is None else max(length, ls)
    spaces = " " * (length - ls)
    string += spaces
    return string[ : length]

def str_round(num, level = 2):
   if level > 0:
      return str(round(num, level))
   else:
      return str(int(round(num, 0)))# + '.'

def pad_round(num, length = 6, level = 2):
   if is_nan_or_none(num):
      return pad(num, length)
   int_length = len(str(int(num))) 
   level = min(level, length - int_length - 1)
   string = str_round(num, level)
   l = len(string)
   string = pad(string, length) if length >= l else '9' * length
   return string

def dictionary_to_string(dictionary):
    rounding = lambda el: el if isinstance(el, str) or isinstance(el, bool) or is_like_list(el) else round(el, 2)
    dictionary = {el: rounding(dictionary[el]) for el in dictionary}
    return str(dictionary)

delete_line = lambda: sys.stdout.write(delete_line_escape)
def indicator(i, tot): # i goes from 1 to tot
    delete_line() if i != 1 else None 
    print("progress:", pad_round(percentage(i, tot), 5) + " %")

    
# Extract Numbers from String
dot = r'\.{1,1}'
integer = r'\d+'
plus = r'|'
full_float = integer + dot + integer
right_float = dot + integer
left_float = integer + dot
float_number = full_float + plus + left_float + plus + right_float
number = float_number + plus + integer
number = '(' + number  + ')'
character = r'(?<=\D)\.{2,}'
begin_string = r'^'

get_numerical = lambda string: re.findall(number, string)
string_to_number = lambda string: int(string) if string.isdigit() else float(string)
strings_to_numbers = lambda strings: list(map(string_to_number, strings))
form_to_input = lambda form: re.sub(r'%.', '{}', form)


# String Utils
is_like_list = lambda data: any([isinstance(data, el) for el in [list, tuple, range, np.ndarray]])
is_nan_or_none = lambda el: np.isnan(el) or el is None # cannot import it from tools
