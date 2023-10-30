import re

to_normal_str = {
        "camel": lambda string: ' '.join([word for word in re.findall(r'[A-Z]?[a-z]*', string)]),
        "pascal": lambda string: ' '.join([word for word in re.findall(r'[A-Z]?[a-z]*', string)]),
        "snake": lambda string: ' '.join(word.lower() for word in re.split(r'_', string)),
        "kebab": lambda string: ' '.join(word.lower() for word in re.split(r'-', string)),
        "upper": lambda string: string.lower(),
        "lower": lambda string: string.lower(),
        "title": lambda string: string.lower(),
        "sentence": lambda string: string.lower()
}

to_convert_case = {
        "camel": lambda string: "{0}{1}".format(string.split()[0].lower(), ''.join(word.capitalize() for word in string.split())),
        "pascal": lambda string: ''.join(word.capitalize() for word in string.split()),

}

to_normal_str["camel"]("myNameIsManish")