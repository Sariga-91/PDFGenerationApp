import re
from datetime import datetime as dt
from DWF.utils import CommandHandler, Store


# ###### Common Interface to avoid cyclic dependecy ####
class AttrResolver:
    def resolve(self, modal_name: str, attr_name: str):
        return None


# #####  parse logic ###########
class NodeRange:
    def __init__(self, start, end, c_start=-1, c_end=-1):
        self.start = start
        self.end = end
        self.c_start = self.start if c_start < 0 else c_start
        self.c_end = self.end if c_end < 0 else c_end

    def display(self):
        return '({0}, {1}, {2}, {3})'.format(self.start, self.end, self.c_start, self.c_end)


# #####  parse logic ###########
class Formatter:
    def __init__(self, template: str,  nd_range: NodeRange):
        self.template = template
        self.nd_range = nd_range
        self.siblings = []

    def is_inclusive(self, nd_range: NodeRange):
        return self.nd_range.c_start <= nd_range.start and self.nd_range.c_end >= nd_range.end

    def fill_text_nodes(self):
        pass

    def convert(self) -> str:
        return ''

    def display(self) -> str:
        pass


class BaseFormatter(Formatter):
    def __init__(self, nd_range: NodeRange, template: str = None, attr_resolver: AttrResolver = None):
        super().__init__(template, nd_range)
        self.attr_resolver = attr_resolver
        self.parent = None

    def get_attr_resolver(self):
        return self.parent.get_attr_resolver() if self.parent else self.attr_resolver

    def convert(self):
        text = self.get_root().template
        position = self.nd_range.c_start
        output = []
        for sib in self.siblings:
            output.extend([text[position:sib.nd_range.start], str(sib.convert())])
            position = sib.nd_range.end
        output.append(text[position:self.nd_range.c_end])
        # print(output)
        return ''.join(output)

    def add_sibling(self, sibling: Formatter):
        target = len(self.siblings)
        for idx, sib in enumerate(self.siblings):
            if sibling.is_inclusive(sib.nd_range):
                target = idx
                break
        while target < len(self.siblings) and sibling.is_inclusive(self.siblings[target].nd_range):
            sibling.add_sibling(self.siblings.pop(target))
        self.siblings.insert(target, sibling)
        sibling.parent = self

    def get_root(self):
        return self.parent.get_root() if self.parent else self

    def display(self, detail=True) -> str:
        out = '[{0}-{1}, chld={2}] {3}'.format(self.nd_range.start, self.nd_range.end,
                                               len(self.siblings), self.template if detail else '...')
        ch = [s.display(detail) for s in self.siblings]
        return out + str(ch)


class ValueResolver(BaseFormatter):
    def __init__(self, nd_range: NodeRange, template: str):
        super().__init__(nd_range, template)

    def convert(self):
        # print(self.display())
        params = super().convert().split(':')
        modal_name = params[0]
        attr_name = params[1] if len(params) == 2 else '{0}({1})'.format(params[1], params[2])
        try:
            return self.get_attr_resolver().resolve(modal_name, attr_name)
        except Exception as e:
            return None


class Translation(CommandHandler.Command):
    def __init__(self, name):
        super().__init__(name)

    def trigger(self, *params):
        try:
            return self.translate([val for val in params[0]])
        except Exception as e:
            print('Input Error: ', e)
            return "InputError"

    def translate(self, params):
        pass


class Quotation(Translation):
    def __init__(self):
        super().__init__('quotes')

    def translate(self, params):
        return '"{0}"'.format(params[0])


class Price(Translation):
    def __init__(self):
        super().__init__('price')
        self.currencies = {
            'india': 'INR.', 'usa': 'USD.', 'singapore': 'Dollar.'
        }

    def translate(self, params):
        args = params[0].split(':')
        value = format(float(args[-1]), ".2f")
        return '{0}{1}'.format(self.currencies.get(args[0]) if args[0] in self.currencies else '', value)


class ParseDate(Translation):
    def __init__(self):
        super().__init__('pDate')

    def translate(self, params):
        args = params[0].split(':')
        args.reverse()
        dt_pattern = '%d-%b-%y' if len(args) == 1 else args[1]
        return dt.strptime(args[0], dt_pattern).strftime('%d-%b-%y')


class ConvertDate(Translation):
    def __init__(self):
        super().__init__('cDate')

    def translate(self, params):
        args = params[0].split(':')
        args.reverse()
        dt_pattern = '%d-%b-%y' if len(args) == 1 else args[1]
        return dt.strptime(args[0], '%d-%b-%y').strftime(dt_pattern)


class Upper(Translation):
    def __init__(self):
        super().__init__('upper')

    def translate(self, params):
        return params[0].upper()


class Lower(Translation):
    def __init__(self):
        super().__init__('lower')

    def translate(self, params):
        return params[0].lower()


class Split(Translation):
    def __init__(self):
        super().__init__('pStr')

    def translate(self, params):
        return params[0].split()


class Translator(BaseFormatter):
    def __init__(self, nd_range: NodeRange, template):
        super().__init__(nd_range, template)
        self.trans_handler = CommandHandler(
            Quotation(), Price(), ParseDate(),
            ConvertDate(), Upper(), Lower(), Split())

    def convert(self):
        # print(self.display())
        # do the conversion action
        text = super().convert()
        pos = text.index(':')
        return self.trans_handler.exec(text[:pos], text[pos+1:])


class ExprEvaluator(BaseFormatter):
    def __init__(self, nd_range: NodeRange, template):
        super().__init__(nd_range, template)

    def convert(self):
        # do the conversion action
        # value = self.siblings[0].convert()
        value = super().convert()
        return eval(value)


class TemplateParser:
    def __init__(self, nm_prefix: str = 'nm'):
        self.nm_prefix = nm_prefix

    def parse(self, template: str, attr_resolver: AttrResolver):
        # # write logic to build one or more Formatter as a tree # #
        pattern = ''.join(['{', self.nm_prefix, ':((\w+):([\s\w.:%\/\*\+\->\(\)]+))}'])
        base = BaseFormatter(NodeRange(0, len(template)), template, attr_resolver)
        while True:
            matches = tuple(re.finditer(pattern, template))
            for match in matches:
                template = template.replace(match.group(), ''.rjust(len(match.group())))
                # print(match.group(), match.group(2), match.group(3), match.start(), match.end())
                transform = match.group(2)
                nd_range = NodeRange(
                    match.start(), match.end(),
                    match.start() + match.group().index(match.group(3)),
                    match.start() + match.group().index(match.group(3)) + len(match.group(3))
                )
                # print(nd_range.display())
                if transform == 'mdl':
                    base.add_sibling(ValueResolver(nd_range, match.group(3)))
                elif transform == 'fmt':
                    base.add_sibling(Translator(nd_range, match.group(3)))
                else:
                    base.add_sibling(ExprEvaluator(nd_range, match.group(3)))
            if not len(tuple(matches)):
                break
        # print(base.display())
        return base


class ContentBuilder(AttrResolver):
    def __init__(self, store: Store, nm_prefix: str = 'nm'):
        self.store = store
        self.parser = TemplateParser(nm_prefix)

    def resolve(self, modal_name: str, attr_name: str):
        try:
            return self.store.get_modal(modal_name).get(attr_name)
        except Exception as e:
            print(e)
            return None

    def transform(self, template: str):
        return self.parser.parse(template, self).convert()
