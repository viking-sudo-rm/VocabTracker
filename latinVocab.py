from __future__ import with_statement
from Tkinter import *
import tkFileDialog, random, time, os

class Cell:
	def __init__(self,target,msg,parent,c,title=False):
		self.index = c
		self.title = title
		self.msg = StringVar()
		self.msg.set(msg)
		self.target = target
		self.parent = parent
		self.drawText()
	def drawText(self):
		self.l = Label(self.target,text=self.msg.get(),bg="#000000" if self.title else "#999999",fg="#FFFFFF" if self.title else "#000000",width=9)
		self.l.grid(row=self.parent.index,column=self.index)
		if not self.title: self.l.bind("<Button-1>",self.edit)
	def edit(self,event):
		self.l.destroy()
		self.e = Entry(self.target,textvariable=self.msg,justify=CENTER,width=10)
		self.e.grid(row=self.parent.index,column=self.index)
		self.e.bind("<Return>",self.save)
		self.e.bind("<FocusOut>",self.save)
	def save(self,event):
		self.e.destroy()
		self.drawText()
		
class Item:
	def __init__(self,forms,index,target,title=False):
		self.target = target
		self.index = index
		self.forms = [Cell(self.target,forms[i],self,i,title) for i in range(len(forms))]

class Chart:
	def __init__(self,target,mode):
		self.mode = mode
		self.target = target
		self.nextIndex = 1
		self.items = []
		self.window = Toplevel(target,height=300)
		self.window.resizable(width=False,height=True)
		self.window.title(mode.name)
		self.chart = Frame(self.window)
		self.chart.pack()
		Label(self.window,text="Press Tab to add a word...").pack()
		Label(self.window,text="Press Cntrl-S to save...").pack()
		Label(self.window,text="Press Cntrl-Q to generate a quiz...").pack()
		Item(self.mode.fieldNames + ["Meaning"],0,self.chart,True)
		self.window.bind("<Tab>",self.new)
		self.window.bind("<Control-s>",self.export)
		self.window.bind("<Control-q>",self.quiz)
	def new(self,event):
		self.items.append(Item(self.mode.defaultValues + ["[meaning]"],self.nextIndex,self.chart))
		self.nextIndex += 1
	def export(self,event):
		with open(tkFileDialog.asksaveasfilename(title="Save File As"),"w") as fh:
			for item in self.items: fh.write(", ".join([form.msg.get() for form in item.forms[:-1]]) + " = " + item.forms[-1].msg.get() + "\n")
	def quiz(self,event):
		i = self.items
		random.shuffle(i)
		quiz = Quiz(self,i,self.mode)

class Quiz:
	def __init__(self,parent,items,mode):
		self.correct = 0
		self.total = len(items)
		self.window = Toplevel(parent.target)
		self.window.title("Quiz")
		for item in items:
			initial = item.forms[random.randint(-1,0)]
			secondIndex = random.randint(0,len(item.forms) - 1)
			while initial == item.forms[secondIndex]:
				secondIndex = random.randint(0,len(item.forms) - 1)
			answer = item.forms[secondIndex]
			text = (mode.fieldNames + ["Meaning"])[secondIndex]
			self.askQuestion("What is the " + text + " of " + initial.msg.get() + "?",answer.msg.get())
		self.showResults()
	def askQuestion(self,question,answer):
		guess = StringVar()
		guess.set("[answer]")
		self.questionFrame = Frame(self.window)
		self.questionFrame.pack()
		Label(self.questionFrame,text=question).grid(row=0,column=0,columnspan=2)
		Entry(self.questionFrame,textvariable=guess).grid(row=1,column=0)
		self.b = Button(self.questionFrame,text="Submit",command=lambda: self.checkQuestion(answer,guess.get()))
		self.b.grid(row=1,column=1)
		self.questionIsDone = False
		while not self.questionIsDone: self.window.update()
	def checkQuestion(self,answer,guess):
		self.questionIsDone = True
		if answer.lower() == guess.lower():
			self.correct += 1
			Label(self.questionFrame,text="Correct :)",fg="green").grid(row=2,column=0)
		else: Label(self.questionFrame,text="Incorrect :(",fg="red").grid(row=2,column=0)
		self.b.config(state=DISABLED)
		self.window.update()
		time.sleep(2)
		self.questionFrame.destroy()
	def getHexColor(self,v):
		c = hex(v)[2:]
		return "#" + "0" * (6 - len(c)) + c
	def showResults(self):
		percentage = int((float(self.correct) / self.total) * 100)
		Label(self.window,text="# Correct:").grid(row=0,column=0)
		Label(self.window,text=str(self.correct) + "/" + str(self.total) + " = " + str(percentage) + "%").grid(row=1,column=0)
		Label(self.window,text="Grade:").grid(row=0,column=1)
		color = self.getHexColor(0xff0000 - (166464 * percentage))
		Label(self.window,bg=color,text="A" if percentage >= 90 else ("B" if percentage >= 80 else ("C" if percentage >= 70 else ("D" if percentage >= 60 else "F")))).grid(row=1,column=1)
		
class Mode:
	def __init__(self,name,fieldNames,defaultValues):
		self.name = name
		self.fieldNames = fieldNames
		self.defaultValues = defaultValues
			
class modeSelectionWindow:
	def getModes(self):
		l = os.listdir("templates")
		r = []
		for i in range(len(l)):
			with open("templates/" + l[i],"r") as fh:
				lines = map(lambda x: x.replace("\n","").split(":"),fh.readlines())
				print lines
				r.append(Mode(l[i][:-4],[x[0] for x in lines],[x[1] for x in lines]))
		return r
	def __init__(self,event):
		self.window = Toplevel(root,width=100,height=300)
		self.window.title("Select Type")
		self.index = IntVar()
		self.index.set(-1)
		Label(self.window,text="Select Vocabulary List Type:").grid(column=0,row=0)
		l = self.getModes()
		for i in range(len(l)):
			r = Radiobutton(self.window,text=l[i].name,variable=self.index,value=i,indicatoron=0,width=30)
			r.bind("<Double-Button-1>",self.create)
			r.grid(row=i + 1,column=0)
	def create(self,event):
		mode = self.getModes()[self.index.get()]
		Chart(root,mode)
		self.window.destroy()
		del self

root = Tk()
root.title("VocabTracker")
root.bind("<Control-n>",modeSelectionWindow)

t = Text(root,width=60,height=20)
t.grid(row=0,column=0)
t.insert(1.0,"\n\n\nWelcome to VocabTracker!!!\nThis program is designed to help you learn vocabulary while studying languages.\n\nPress Cntrl-N to get started...")
t.config(state=DISABLED)

mainloop()