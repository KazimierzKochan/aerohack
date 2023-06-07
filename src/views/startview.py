from os import path
import os
import tkinter as tk
from tkinter import Button, Canvas
from PIL import ImageTk, Image  
from utils import startutils
from graphics import style

def prepareView(tab, tabControl, nextTab, session):
	# ------------------------------ Configuration ------------------------------ #
	tab.grid_propagate(False)

	viewFrame = tk.Frame(tab, bg=style.LIGHTMEDIUMGRAY, bd=0)
	viewFrame.pack(expand=True, fill="both")

	viewFrame.columnconfigure(0, weight=1)
	viewFrame.columnconfigure(1, weight=1)

	viewFrame.rowconfigure(1, weight=1)
	viewFrame.rowconfigure(8, weight=1)


	# ------------------------------ Logo ------------------------------ #
	logoPath = os.getcwd()
	logoPath = logoPath+"/src/graphics/aerohack_bg.png"

	imgLogo = Image.open(logoPath)
	global pImgLogo
	pImgLogo = ImageTk.PhotoImage(imgLogo)

	cnvLogo = Canvas(viewFrame, bg=style.LIGHTMEDIUMGRAY)
	cnvLogo.grid(row=0, column=0, rowspan=2, columnspan=1, sticky="nwes")

	cnvLogo.create_image(10,10,anchor=tk.NW,image=pImgLogo)


	# ------------------------------ Start information ------------------------------ #
	lblWelcome = tk.Label(
		viewFrame,
		text="Welcome to AeroHack",
		background="gray",
	)
	lblWelcome.grid(row=2, column=0, sticky="ew")

	def btnSetupClicked():
		tabControl.select(nextTab)

	btnSetup = tk.Button(
		viewFrame,
		text = "Start attacking",
		command = btnSetupClicked,
		width=20,
		bg=style.DARKMEDIUMGRAY
	)
	btnSetup.grid(row = 5, column = 0)

	def btnSessionClicked():
		session.udateSession()

	btnSetup = tk.Button(
		viewFrame,
		text = "Start new session",
		command = btnSessionClicked,
		width=20,
		bg=style.DARKMEDIUMGRAY
	)
	btnSetup.grid(row = 6, column = 0)


	def btnSaveLogsClicked():
		session.saveLogs()

	btnSaveLogs = tk.Button(
		viewFrame,
		text = "Save logs",
		command = btnSaveLogsClicked,
		width=20,
		bg=style.DARKMEDIUMGRAY
	)
	btnSaveLogs.grid(row = 7, column = 0)



	# ------------------------------ FAQ ------------------------------ #
	lblFaqTitle = tk.Label(
		viewFrame,
		text="Frequently\nasked\nquestions",
		font=("TkDefaultFont", 40),
		bg=style.LIGHTMEDIUMGRAY
	)
	lblFaqTitle.grid(row=0, column=1, rowspan=2, sticky="nwes")


	lstFaq = startutils.getFaq()
	lstAnswers = startutils.getAnswers()

	questionRow = 2

	lblAnswer = tk.Label(
		viewFrame,
		text = "Click on the question",
		bg=style.LIGHTGRAY,
		height=1,
		width=1
	)
	lblAnswer.grid(row = 8, column = 1, rowspan=3, sticky="nswe")


	def btnQuestionClicked(index):
		lblAnswer.configure(text=lstAnswers[index])

	for faqIndex in range(0, len(lstFaq)):
		
		btnQuestion = Button(
			viewFrame,
			text = lstFaq[faqIndex],
			command = lambda faqIndex=faqIndex: btnQuestionClicked(faqIndex),
			bg = style.MEDIUMGRAY
		)
		
		btnQuestion.grid(row = questionRow, column = 1, sticky = "nwse")
		questionRow += 1


	# ------------------------------ Session information ------------------------------ #
	lblSession = tk.Label(
		viewFrame,
		textvariable = session.path,
		bg = style.MEDIUMGRAY
	)
	lblSession.grid(row=9, column=0, sticky="wes", columnspan=1)