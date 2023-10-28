nl = "\n"
percentage = lambda num, total = 1: 100 * num / total

# Escape Codes 

def simple_print(simple = True):
    global ansi_bold
    global ansi_end
    global ansi_delete_line

    ansi_bold = '' if simple else '\x1b[1m'
    ansi_end = '' if simple else '\x1b[0m'
    ansi_delete_line = '' if simple else '\033[A\033[2K'

simple_print(False)

bold = lambda string: ansi_bold + string + ansi_end
enclose_circled = lambda string: '(' + str(string) + ')' #if string != "" else string
enclose_squared = lambda string: '[' + str(string) + ']' #if string != "" else string

def dictionary_to_string(dictionary):
    rounding = lambda el: round(el, 2) if isinstance(el, float) else el
    dictionary = [el + ' = ' + str(rounding(dictionary[el])) for el in dictionary]
    return enclose_circled(', '.join(dictionary))

