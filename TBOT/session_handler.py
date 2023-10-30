class BotMessage:
	def __init__(self, text: str, data = {}):
		self.text = text
		self.data = data

	def getText(self):
		return self.text

	def getData(self):
		return self.data


class UserSession:
	def __init__(self, user_id: str, chat_id: str, name: str):
		self.user_id = user_id
		self.chat_id = chat_id
		self.name = name
		self.conv_state = None
		self.user_data = dict()

	def getUserId(self):
		return self.user_id

	def getChatId(self):
		return self.chat_id

	def getName(self):
		return self.name

	def setConvState(self, state: str):
		pass

	def setParam(self, attr: str, value: str):
		pass

	def clearParam(self, attr: str):
		self.user_data.pop(attr)

	def clearParams(self):
		self.user_data.clear()

	def handleMessage(self, msg: BotMessage):
		print(msg.getText(), msg.getData())


class SessionHandler:
	def __init__(self):
		self.sessions = dict()

	def getSession(self, chat_id: str):
		try:
			return self.sessions[chat_id]
		except:
			return None

	def createSession(self, session: UserSession):
		self.sessions[session.chat_id] = session
		return session

	def clearSession(self, chat_id: str):
		self.sessions.pop(chat_id)
