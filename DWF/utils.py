from DWF.modal import QueryBuilder, Key, GenericModal
import pandas as pd


class Store(QueryBuilder):
    def __init__(self, config_path: str = None):
        self.dbs = dict()
        self.master_key = Key()
        if config_path:
            self.define_from_file(config_path)

    def get_modal(self, modal_name):
        try:
            return self.dbs[modal_name]
        except Exception as e:
            print(e)
            return None

    def set_modal(self, modal_name, modal):
        self.dbs[modal_name] = modal

    def build_query(self, attrs) -> str:
        return ''.join(['{0} == "{1}" and '.format(k, self.master_key.get_value(k)) for k in attrs])[:-5]
        # return ''

    def define_from_file(self, path):
        in_json = {
            'mas_cust': {'file': 'data/Master-Customer-Statement.csv', 'key': ['Customer']},
            'mas_sales':{'file': 'data/Master-Customer-Trans-History.csv', 'key': ['Customer']},
            'dist_sum': {'file': 'data/05-10-23.csv', 'key': ['ID']}
        }
        for modal_name in in_json:
            self.set_modal(modal_name, GenericModal(in_json[modal_name]['file'], 
                self, in_json[modal_name]['key']))

        return self




class CommandHandler:
    def __init__(self, *cmds):
        self.commands = []
        try:
            if all([isinstance(x, self.Command) for x in cmds]):
                for x in cmds:
                    self.commands.append(x)
            else:
                raise ValueError('some are not commands')
        except Exception as e:
            print(e)
            raise Exception('Invalid init')

    def exec(self, name, *params):
        commands = self.commands
        try:
            for cmd in commands:
                if cmd.match(name):
                    return cmd.trigger(params)
            return None
        except Exception as e:
            print(e)
            return None

    class Command:
        def __init__(self, name):
            self.name = name

        def match(self, name):
            return self.name == name

        def trigger(self, *params):
            pass


class EventHandler:
    def __init__(self):
        self.register = pd.DataFrame({'all_O': [None]})
        self.register.index = ['all_E']
        self.listeners = dict()
        self.events = dict()

    class Event:
        def __init__(self, name, msg=None):
            self.name = name
            self.msg = '{0} event occurred'.format(name) if not msg else msg

        def show(self):
            print('[Event][{0}]: {1}'.format(self.name, self.msg))

    class Listener:
        def __init__(self, name='default'):
            self.name = name

        def rename(self, name):
            self.name = name
            return self

        def notify(self, event):
            pass

    def add_event(self, event: Event):
        self.register[event.name] = None
        self.events[event.name] = event

    def add_listener(self, listener: Listener):
        self.register.loc[listener.name] = None
        self.listeners[listener.name] = listener

    def publish(self, event: str, listeners: list):
        self.register.loc[listeners, event] = 'OK'
        # self.desc()

    def subscribe(self, listener: str, events: list):
        for event in events:
            self.register.loc[listener, event] = 'OK'
            # self.desc()

    def exec(self, name):
        event = self.events[name]
        df = self.register
        result = df.loc[df[name] == 'OK'][name]
        obj = {lsnr: self.listeners[lsnr].notify(event) for lsnr in result.index}
        # print(obj)
        return obj

    def desc(self):
        print(self.register)

