import numpy as np

import pandas as pd

import sys

import matplotlib.dates as dates
import matplotlib.pyplot as plt

import matplotlib.patches as patches
# columns : Index(['start_date', 'end_date', 'pollster', 'sponsor', 'sample_size',
       # 'population', 'party', 'subject', 'tracking', 'text', 'approve',
       # 'disapprove', 'url'],

 # party options  ['all', 'R', 'D', 'I']
plt.style.use('../Downloads/BME163.mplstyle')

class DataIntake():
	def __init__(self, file):
		self.df = pd.read_csv(file)


	def fixDates(self):
		self.df.start_date = pd.to_datetime(self.df.start_date, format = '%Y-%m-%d')
		self.df.end_date = pd.to_datetime(self.df.end_date, format = '%Y-%m-%d')


	def getdf(self):
		return self.df

	def printdates(self):
		print(self.df.end_date.sort_values())


	def getGradedPolls(self, grade):
		self.df[self.df['538 Grade'].isin(grade)]
		return self.df.Pollster

	def getPct(self):
		self.df['pct_approval'] = self.df['approve'] / (self.df['approve'] + self.df['disapprove'])



	def filterPollByPollsterGrade(self, pollsToKeep):
		self.df = self.df[self.df.pollster.isin(pollsToKeep)]


	def changeDatesToWeeks(self, column_name):
		self.df['week'] = self.df[column_name].dt.week
		self.df.start_date = self.df.start_date.dt.date
		# self.df.set_index('start_date', inplace = True)


	def weeklyAvgsByParty(self, party):
		weeklyValues = []
		exactDate = []
		for week in range(min(self.df.week), max(self.df.week) + 1):
			weeklyValues.append(np.array(self.df[(self.df['week'] == week) & (self.df['party'] == party)]['pct_approval'].dropna()))
			exactDate.append(np.array(self.df[(self.df['week'] == week) & (self.df['party'] == party)].start_date.dropna()))


		return weeklyValues, exactDate


class Graph:
	def __init__(self, dataframe):
		self.df = dataframe




	def setPanel(self, panelWidth, panelHeight, panelLeftPosition, panelBottomPosition):

		panel = plt.axes([panelLeftPosition/self.figWidth, panelBottomPosition/self.figHeight, 
			panelWidth/self.figWidth, panelHeight/self.figHeight])


		return panel


	def setFigure(self, figWidth, figHeight):
		self.figWidth = figWidth
		self.figHeight = figHeight
		self.fig = plt.figure(figsize = (figWidth, figHeight))


	def plotIndividualValues(self, panel, exactDates, weeklyValues, color, label):
		panel.set_xlim(min(self.df['week']), max(self.df['week'])+1)
		for weekV, week in zip(weeklyValues, range(min(self.df['week']), max(self.df['week'])+1)):
			panel.plot([week+0.5]* len(weekV), weekV, marker = 'o',  markersize = 1, lw = 0, alpha = 0.5, color = color, label = label)
		# for weekV, date in zip(weeklyValues, exactDates):
		# 	even = min(len(date), len(weekV))
		# 	panel.plot(date[:even], weekV[:even], marker = 'o',  markersize = 1, lw = 0, alpha = 0.65, color = color)
			# panel.plot([x_right], [y_value], marker='o', markersize=markerSize, markeredgewidth = 0, 
			# 					mfc=color, linewidth=0, zorder=4, alpha = 1)
		priorWeekAvg = 0
		priorWeek = min(self.df['week'])
		for weekV, week in zip(weeklyValues, range(min(self.df['week']), max(self.df['week'])+1)):
			line = panel.plot([week, week+1], [np.mean(weekV), np.mean(weekV)], lw = 0.8, color = color)
			if priorWeekAvg == 0:
				priorWeekAvg = np.mean(weekV)
				continue
			else:
				panel.plot([week,week],[np.mean(weekV), priorWeekAvg], lw = 0.8, color = color)
				priorWeekAvg = np.mean(weekV)
		
		return panel, line


	def formatPanel(self, panel):
		panel.set_yticklabels(['', '0%','20%','40%','60%','80%','100%'], fontsize = 'small')
		panel.set_xticklabels(['1/26/20', '3/7/20', '4/11/20','5/16/20','6/20/20','7/25/20'], ha = 'center', fontsize = 'small')
		panel.spines['top'].set_visible(False)
		panel.spines['right'].set_visible(False)
		panel.set_ylabel('% approval rating on \n national response to COVID-19')
		panel.set_xlabel('Date')
		panel.set_title('Approval of COVID-19 response over time \n based on political affiliation')

	def saveFig(self):
		plt.savefig('testA.png', dpi = 600)



def main():
	covidPoll = DataIntake(sys.argv[1])
		

	pollsterRatings = DataIntake(sys.argv[2])

	interestedPollsters = pollsterRatings.getGradedPolls(grade = ['A+' 'A/B' 'A' 'A-' 'B' 'B+'])
	# interestedPollsters = pollsterRatings.getGradedPolls(grade = ['F' 'C+' 'C' 'C-' 'C/D' 'D+' 'D-'])
	# 'F' 'B/C' 'B' 'B-' 'C+' 'C' 'C-' 'C/D' 'D+' 'D-']

	covidPoll.filterPollByPollsterGrade(interestedPollsters)

	covidPoll.fixDates()

	covidPoll.getPct()

	covidPoll.changeDatesToWeeks('start_date')

	r_weekly_avg, r_exact_dates = covidPoll.weeklyAvgsByParty('R')
	d_weekly_avg, d_exact_dates = covidPoll.weeklyAvgsByParty('D')
	i_weekly_avg, i_exact_dates = covidPoll.weeklyAvgsByParty('I')


	covGraph = Graph(covidPoll.getdf())

	covGraph.setFigure(6, 3)
	panel= covGraph.setPanel(5,2,.75,.5)
	panel, line1 = covGraph.plotIndividualValues(panel, r_exact_dates, r_weekly_avg, color = 'tomato', label = 'Republican')
	panel, line2 = covGraph.plotIndividualValues(panel, d_exact_dates, d_weekly_avg, color = 'royalblue', label = 'Democrat')
	panel, line3 = covGraph.plotIndividualValues(panel, i_exact_dates, i_weekly_avg, color = 'dimgrey', label = 'Independent')
	red_patch = patches.Patch(color='tomato', label='Republican')
	blue_patch = patches.Patch(color='royalblue', label='Democrat')
	gray_patch = patches.Patch(color='dimgray', label='Independent')
	plt.legend(handles=[red_patch, blue_patch,gray_patch], frameon= False, bbox_to_anchor = (5.4/6,2.8/3), fontsize = 'x-small')
	covGraph.formatPanel(panel)
	covGraph.saveFig()









main()