
import airtable
from bs4 import BeautifulSoup
import requests
import datetime

class Page:

	def __init__(self, request_url):
		# info to login
		self.url = request_url
		login_url = 'https://kehillah.schoology.com/login'
		'?destination=assignment%2F2360127760%2Finfo&school=538118791'
		payload = {'mail': 'rlang2022@kehillahstudent.org', 'pass': '', 
			'school_nid': '538118791', 
			'form_build_id': '37956b9-2rWfbx10cAVhTwrESBe3AJX1oAMzRhoyRV2SEMgqf4g', 
			'form_id': 's_user_login_form'}

		# login and goes to requested url
		with requests.Session() as session:
		    post = session.post(login_url, data=payload)
		    r = session.get(self.url)

		self.soup = BeautifulSoup(r.content, 'html.parser')

	def getCourseTitle(self):
		""" find and return course title """
		line = self.soup.find('span', class_='course-title').find('a')
		return line.get_text()

	def getAssignmentTitle(self):
		""" find and return assignment title """
		line = self.soup.find('h2', class_='page-title')
		return line.get_text()

	def getDueDate(self):
		""" find and return due date """
		line = self.soup.find('div', class_='assignment-details')
		return line.get_text()


class Assignment:

	courses = {'Comedy and Satire': 'English', 'AP Calculus BC': 'Math', 
		'Jews and the Modern American Experience': 'Jewish Studies', 
		'Introduction to Economics': 'Social Studies', 
		'AP Statistics': 'Statistics', 'Advanced Algorithms Honors': 'Computer Science', 
		'AP Physics C': 'Physics', 'Engineering 1': 'Engineering'}
	months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
		'October', 'November','December']

	def __init__(self, page):
		# these are the default values
		self.title = page.getAssignmentTitle()
		self.subject = self.processSubject(page.getCourseTitle())
		self.url = page.url
		self.date = self.createDate(page.getDueDate())
		self.type = self.getType()
		self.notes = ''
		self.project = ''
		self.priority = '!!!'

		base_key = 'app9MVZp2e3XrDeZr'
		table_name = 'My Tasks and Homework'
		self.airtable = airtable.Airtable(base_key, table_name, api_key='keyGsishSLatHyz0n')

	def processSubject(self, course_title):
		""" get subject to be one of airtable's options """
		subject = course_title.split(':')[0]
		return Assignment.courses[subject]

	def createDate(self, due_date):
		""" return datetime object """
		# fix so works without date given
		parts = due_date.split(',', 1)[1].split(' ')
		year = int(parts[3])
		month = Assignment.months.index(parts[1])+1
		day = int(parts[2][:-1])
		if 'at' in parts:
			time = parts[5].split(':')
			hour = int(time[0])
			if parts[6] == 'pm': hour += 12
			hour = (hour + 7) % 24
			minute = int(time[1])
		else:
			hour = 7
			minute = 0
		date = datetime.datetime(year, month, day, hour, minute)
		return date

	def textProcessDate(self):
		""" return date in form of Month Name dd, yyyy """
		return self.date.strftime('%B %d, %Y')

	def textProcessTime(self):
		""" return time in form of hh:mm am/pm """
		return self.date.strftime('%I:%M %p')

	def getType(self):
		""" return guess of type """
		quizwords = ['quiz', 'Quiz', 'QUIZ', 'test', 'Test', 'TEST', 'quest', 'Quest', 'QUEST', 'exam', 
			'Exam', 'EXAM', 'opportunity', 'Oppurtunity', 'OPPORTUNITY']
		for word in quizwords:
			if word in self.title: return 'Tests and Quizzes'
		return 'Homework'

	def toJSON(self):
		""" upload assignment to airtable """
		return {'Assignment': self.title, 'Subject': self.subject, 'Due Date': self.date.isoformat('T'),
			'URL': self.url, 'Attachments and Notes': self.notes, 'Type': self.type, 'Project': self.project, 
			'Priority': self.priority}

	def toAirtable(self):
		""" upload to airtable"""
		self.airtable.insert(self.toJSON())


if __name__ == '__main__':
	url = input()
	p = Page(url)
	a = Assignment(p)
	a.toAirtable()

