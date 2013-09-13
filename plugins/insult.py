# coding: utf-8
import random, time
import utility, settings
from commands import Command

class InsultCommand(Command):
	def __init__(self): 
		pass 

	def trig_insult(self, bot, source, target, trigger, argument):
		t = argument.strip()
		if not t:
			t = source

		insult = random.sample(self.insults, 1)[0]
		try:
			return insult.replace('%s', t)
		except:
			return "We all know %s sucks, but so does the insult I tried to use." % t

	def trig_addinsult(self, bot, source, target, trigger, argument):
		if not "%s" in argument:
			return "Trying to add an improper insult, booo!"
		elif argument in self.insults:
			return "That insult already exists!"
		self.insults.append(argument)
		self.save()
		return "Added insult: %s" % argument.replace('%s', source)

	def trig_votedelinsult(self,bot,source,target,trigger,argument):
		self.clean_up_votes()

		if argument in self.insults:
			if argument in self.votes:
				vote = self.votes[argument]
				if source in vote["votes"]:
					return "%s has already voted to remove insult" % (source)
				else:
					vote["votes"].append(source)
					if len(vote["votes"]) >= int(settings.Settings().insult['min_votes']):
						self.insults.remove(argument)
						del self.votes[argument]
						self.save()
						return "Vote succeeded, removing %s" % argument
					else:
						self.save()
						return "%s has now voted to remove '%s'" % (source,argument)
			else:
				self.votes[argument] = {"votes" : [source], "ends" : int(time.time()+int(settings.Settings().insult['timeout'])) }
				self.save()
				minutes = (int(settings.Settings().insult['timeout'])/60)
				min_str = "minutes" if minutes > 1 else "minute"
				return "Voting to delete '%s' has now begun and will run for %d %s. (Min num of votes is %d) | Vote by sending %s %s" % (argument, minutes, min_str, settings.Settings().insult['min_votes'], settings.Settings().trigger+"votedelinsult", argument)
		else:
			return "We cant vote on what isnt in the database"

	def clean_up_votes(self):
		for key in self.votes.keys():
			vote = self.votes[key]
			if vote['ends'] <= int(time.time()):
				del self.votes[key]

		self.save()

	def save(self):
		utility.save_data("insults", self.insults)
		utility.save_data("insult_votes", self.votes)

	def on_load(self):
		self.insults = utility.load_data("insults", [])
		self.votes = utility.load_data("insult_votes", {})

	def on_unload(self): 
		self.insults = None
		self.insults = None
