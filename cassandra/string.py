nl = "\n"

# Escape Codes
enclose_circled = lambda string: '(' + str(string) + ')' #if string != "" else string
enclose_squared = lambda string: '[' + str(string) + ']' #if string != "" else string

# def dictionary_to_string(dictionary):
#     rounding = lambda el: round(el, 2) if isinstance(el, float) else el
#     dictionary = [el + ' = ' + str(rounding(dictionary[el])) for el in dictionary]
#     return enclose_circled(', '.join(dictionary))

