import re
import pandas as pd
from datetime import datetime as dt
from DWF.utils import CommandHandler, EventHandler
from DWF.parser import BaseFormatter, NodeRange


# #Check if the string starts with "The" and ends with "Spain":

# txt = "Hi {nm:mdl:bill:useo}!!!, How are you??"
# # x = re.finditer("{(\w+):(\w+):(\w+):(\w+)}", txt)
# x = re.finditer("{(\w+):(\w+):([\w:]+)}", txt)

# print('hello')
# # print(len(x))
# for k in x:
#   print(k.start(), k.end(), k.group())
#   for index in range(0, k.lastindex+1):
#     print(k.group(index))


# lst = ["hello", 'how are you', "fine"]
# for idx in reversed(lst):
#     print(idx)

class Base:
    def __init__(self):
        self.data = None

    def get(self, attr):
        if self.data is None: self.refresh()
        return self.data[attr]


    def refresh(self):
        self.data = {'age': 32}


class Extended(Base):
    def refresh(self):
        print(self.data)


key = {'NAME': 'AMARAVATHI', 'SESSION': 'PM'}

def main_1():
    # obj = Base()
    # print(obj.get('age'))
    df = pd.read_csv('E:/wesite_programs/tbot/p1/FINAL.csv')
    df.loc[[all([df.loc[idx][k] == key[k] for k in key]) for idx in df.index], "NAME"] = "KATHRIKAI"
    df.loc[len(df), [x for x in key] + ['TOTAL']] = [key[x] for x in key] + ['200']
    print(df)


def main_2():
    test = 'min( attr )'
    match = re.match('(\w+)([\w\s\(\)]+)', test)
    print(match.group(1), str(match.group(2)).strip())
    print(dt.strptime('11-Mar-23', '%d-%b-%y').strftime('%d-%b-%y'))


def main_3():
    import re

    to_normal_str = {
            "camel": lambda string: ' '.join([word.lower() for word in re.findall(r'[A-Z]?[a-z]*', string)])
    }

    print(to_normal_str["camel"]("myNameIsManish"))
    arr = ['amu', 'bot']
    print(arr[3])



class Voice(CommandHandler.Command):
    def __init__(self, name):
        super().__init__(name)

    def trigger(self, *params):
        return self.noise([val for val in params[0]])

    def noise(self, params):
        pass


class Speak(Voice):
    def __init__(self):
        super().__init__('speak')

    def noise(self, params):
        return 'Hello!! {0}'.format(params[0])


class Bark(Voice):
    def __init__(self):
        super().__init__('bark')

    def noise(self, params):
        return '{0}!, Val Val Val'.format(params[0])


def main_4():
    # sound_handle = CommandHandler(Speak(), Bark())
    # print(sound_handle.exec('speak', 45))
    # print(sound_handle.exec('bark', 'Jade'))
    eh = EventHandler()
    eh.Event('fire', 'Third floor identified as fired').show()
    fireEvent = EventHandler.Event('fire')

    class FireEngine(EventHandler.Observer):
        def __init__(self):
            super().__init__('FireEngine')

        def notify(self, event):
            return False

    eh.add_event(fireEvent)
    eh.add_event(EventHandler.Event('noi'))
    eh.add_observer(FireEngine())
    eh.add_observer(EventHandler.Observer('Savitha'))
    eh.publish('fire', ['FireEngine'])
    eh.subscribe('Savitha', ['noi', 'fire'])
    # eh.desc()
    eh.exec(fireEvent)


class Node:
    def __init__(self,  text, category='BASE', start=0, end=0):
        self.category = category
        self.start = start
        self.end = end
        self.text = text
        self.children = []

    def show(self):
        print('{0} [{1}-{2}]: {3}'.format(self.category, self.start, self.end, self.text))
        return self

    def append(self, obj):
        self.children.append(obj)



def main_5():
    template = "Hi {nm:evl:{nm:mdl:mas_cust:StatementHead->__iter_curr__:OpenBalance}+{nm:mdl:mas_cust:StatementHead->__iter_curr__:BillAmount}} and {nm:evl:{nm:mdl:mas_cust:StatementHead->__iter_curr__:OpenBalance} /10}"
    # template = "Hi {nm:mdl:mas_cust:StatementHead->__iter_curr__:OpenBalance} + {nm:mdl:mas_cust:StatementHead->__iter_curr__:BillAmount}"
    pattern = r'{nm:((\w+):([\s\w.:\/\*\+\->]+))}'
    nd = Node(template, 'BASE', 0, len(template)).show()
    print(nd.text[nd.start:nd.end+1])

    while True:
        print('=============')
        print(nd.text)
        matches = tuple(re.finditer(pattern, nd.text))
        print(len(matches))

        print('Matches: ')
        for match in matches:
            print(match.group(), match.group(2), match.start(), match.end())
            nd.text = nd.text.replace(match.group(), ''.rjust(len(match.group())))

        if not len(tuple(matches)):
            break


def main_6():
    template = "Hi {nm:evl:{nm:mdl:mas_cust:StatementHead->__iter_curr__:OpenBalance}+{nm:mdl:mas_cust:StatementHead->__iter_curr__:BillAmount}} and {nm:evl:{nm:mdl:mas_cust:StatementHead->__iter_curr__:OpenBalance} /10}.."
    # template = 'Hello, I am a super boy'
    bf = BaseFormatter(NodeRange(0, len(template)), template)
    pattern = r'{nm:((\w+):([\s\w.:\/\*\+\->]+))}'
    print(template)
    while True:
        matches = tuple(re.finditer(pattern, template))
        for match in matches:
            template = template.replace(match.group(), ''.rjust(len(match.group())))
            child = BaseFormatter(NodeRange(match.start(), match.end()), match.group(2))
            bf.add_sibling(child)
            print(match.group(), match.group(2), match.start(), match.end())
            print(child.convert())

        if not len(tuple(matches)):
            break

    print("========")
    print(bf.display(False))
    print(bf.template)
    print(bf.convert())

if __name__ == '__main__':
    main_6()
