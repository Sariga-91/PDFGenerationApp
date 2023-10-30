from session_handler import BotMessage, UserSession, SessionHandler
from DWF.modal import DailyTransModal



modal = DailyTransModal('../data', 'template.csv')

ses_handler = SessionHandler()


def main():
	session = ses_handler.getSession('65811234')
	if session is None:
		session = UserSession('65811234', '65811234', 'Manish V')
		ses_handler.createSession(session)

	msg = BotMessage('200')
	session.handleMessage(msg)


if __name__ == '__main__':
	main()