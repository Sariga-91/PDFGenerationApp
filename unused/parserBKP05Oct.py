import re
from datetime import datetime as dt
from DWF.utils import CommandHandler
from DWF.modal import Modal


####### Common Interface to avoid cyclic dependecy ####
class AttrResolver:
    def resolve(self, modal_name: str, attr_name: str):
        return None


######  parse logic ###########
class Formatter:
    def __init__(self, template: str, start=0, end=-1):
        self.template = template
        self.start = start
        self.end = end

    def convert(self):
        return ''


class BaseFormatter(Formatter):
    def __init__(self, template: str, attr_resolver: AttrResolver = None, start=0, end=-1):
        super().__init__(template, start, end)
        self.attr_resolver = attr_resolver
        self.siblings = []
        self.parent = None

    def add_sibling(self, sibling: Formatter):
        sibling.parent = self
        if self.template:
            text_node = BaseFormatter(self.template[:sibling.start], end=sibling.start)
            text_node.parent = self
            self.siblings.append(text_node)
            self.siblings.append(sibling)
            text_node = BaseFormatter(self.template[sibling.end:], start=sibling.end)
            text_node.parent = self
            self.siblings.append(text_node)
            self.template = None
            return
        for sib in reversed(self.siblings):
            if sibling.start >= sib.start:
                sibling.start -= sib.start
                sibling.end -= sib.start
                sib.add_sibling(sibling)
                return

    def convert(self):
        if self.siblings:
            return ''.join([str(elem.convert()) for elem in self.siblings])
        elif self.template:
            return self.template
        return ''

    def get_attr_resolver(self):
        return self.parent.get_attr_resolver() if self.parent else self.attr_resolver


class ValueResolver(BaseFormatter):
    def __init__(self, pattern: str, start, end):
        super().__init__(pattern, start=start, end=end)
        params = pattern.split(':')
        self.modal_name = params[0]
        self.attr_name = params[1] if len(params) == 2 else '{0}({1})'.format(params[1], params[2])

    def convert(self):
        try:
            return self.get_attr_resolver().resolve(self.modal_name, self.attr_name)
        except:
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

    def translate(self, params):
        return format(float(params[0]), ".2f")


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
    def __init__(self, action, child, start, end):
        super().__init__(action, start=start, end=end)
        child.parent = self
        self.siblings.append(child)
        self.trans_handler = CommandHandler(
            Quotation(), Price(), ParseDate(),
            ConvertDate(), Upper(), Lower(), Split())

    def convert(self):
        # do the conversion action
        value = self.siblings[0].convert()
        return self.trans_handler.exec(self.template, value)


class ExprEvaluator(BaseFormatter):
    def __init__(self, child, start, end):
        super().__init__('', start=start, end=end)
        child.parent = self
        self.siblings.append(child)

    def convert(self):
        # do the conversion action
        value = self.siblings[0].convert()
        # print(value)
        return eval(value)


class TemplateParser:
    def __init__(self, nm_prefix: str = 'nm'):
        self.nm_prefix = nm_prefix

    def parse(self, template: str, attr_resolver: AttrResolver):
        # # write logic to build one or more Formatter as a tree # #
        pattern = '(\w+):([{\w.:%\->/\*\+\-\(\)}]+)'
        fmtr = BaseFormatter(template, attr_resolver)
        for match in list(re.finditer(''.join(['{', self.nm_prefix, ':', pattern, '}']), template)):
            # print(match.group(), match.group(2), match.start(), match.end())
            # # mdl - value resolver - fmt - nmc
            if match.group(1) == 'mdl':
                # print(match.group(2))
                fmtr.add_sibling(ValueResolver(match.group(2), match.start(), match.end()))
            elif match.group(1) == 'fmt':
                # print(match.group(2))
                for fmt_match in re.finditer(pattern, match.group(2)):
                    action = fmt_match.group(1)
                    child = self.parse(fmt_match.group(2), attr_resolver)
                    fmtr.add_sibling(Translator(action, child, match.start(), match.end()))
            elif match.group(1) == 'evl':
                # print(match.group(2))
                child = self.parse(match.group(2), attr_resolver)
                fmtr.add_sibling(ExprEvaluator(child, match.start(), match.end()))
        return fmtr

    # def parse(self, template: str, attr_resolver: AttrResolver):
    #     # # write logic to build one or more Formatter as a tree # #
    #     pattern = '(\w+):([{\w.:%\->/\*\+\-\(\)}]+)'
    #     fmtr = BaseFormatter(template, attr_resolver)
    #     for match in list(re.finditer(''.join(['{', self.nm_prefix, ':', pattern, '}']), template)):
    #         # print(match.group(), match.group(2), match.start(), match.end())
    #         # # mdl - value resolver - fmt - nmc
    #         if match.group(1) == 'mdl':
    #             # print(match.group(2))
    #             fmtr.add_sibling(ValueResolver(match.group(2), match.start(), match.end()))
    #         elif match.group(1) == 'fmt':
    #             # print(match.group(2))
    #             for fmt_match in re.finditer(pattern, match.group(2)):
    #                 action = fmt_match.group(1)
    #                 child = self.parse(fmt_match.group(2), attr_resolver)
    #                 fmtr.add_sibling(Translator(action, child, match.start(), match.end()))
    #         elif match.group(1) == 'evl':
    #             # print(match.group(2))
    #             child = self.parse(match.group(2), attr_resolver)
    #             fmtr.add_sibling(ExprEvaluator(child, match.start(), match.end()))
    #     return fmtr


class ContentBuilder(AttrResolver):
    def __init__(self, nm_prefix: str = 'nm'):
        self.modals = {}
        self.parser = TemplateParser(nm_prefix)

    def setModal(self, modal_name: str, modal: Modal):
        self.modals.update({modal_name: modal})

    def clear(self, modal_name: str):
        self.modals.pop(modal_name)

    def resolve(self, modal_name: str, attr_name: str):
        try:
            return self.modals.get(modal_name).get(attr_name)
        except:
            return None

    def clearAll(self):
        self.modals.empty()

    def transform(self, template: str):
        return self.parser.parse(template, self).convert()


