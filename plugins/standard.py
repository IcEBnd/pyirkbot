# coding: utf-8

from commands import Command
import htmlentitydefs
import string
import re
import utility
import os
import pickle
import random

class EchoCommand(Command): 
	def __init__(self):
		pass
	
	def trig_echo(self, bot, source, target, trigger, argument):
		return argument

class HelloCommand(Command): 
	def __init__(self):
		pass
	
	def trig_hello(self, bot, source, target, trigger, argument):
		return "Hello there, %s!" % source

class PickCommand(Command): 
	def __init__(self):
		pass
	
	def trig_pick(self, bot, source, target, trigger, argument):
		choices = argument.split(" or ")
		choices = map(lambda x: x.strip(), choices)
		choices = filter(lambda choice: len(choice), choices)

		print choices

		if choices:
			responses = ["Hm... Definitely not %s.", "%s!", "I say... %s!", "I wouldn't pick %s...", "Perhaps %s..."]
			choice = random.choice(choices)
			response = random.choice(responses)
			
			return response % choice
		else:
			return None

class InsultCommand(Command): 
    def __init__(self): 
        pass 
 
    def trig_insult(self, bot, source, target, trigger, argument): 
        t = source 
        if argument: 
            m = re.search('(\S+)', argument) 
 
            if m: 
                t = m.group(1) 
 
        import random; 
        insult = random.sample(self.insults, 1)[0] 
        try: 
            return insult.replace('%s', t)
            
        except: 
            return "Improper insult, check your data" 
         
    def trig_addinsult(self, bot, source, target, trigger, argument): 
        if not "%s" in argument: 
            return "Trying to add an improper insult, booo!" 
        elif argument in self.insults: 
            return "That insult already exists!" 
        self.insults.append(argument) 
        self.save() 
        return "Added insult: %s" % argument.replace('%s', source)
     
    def save(self): 
        f = open(os.path.join("data", "insults.txt"), "w") 
        p = pickle.Pickler(f) 
        p.dump(self.insults) 
        f.close() 
     
    def on_load(self): 
        self.insults = [] 
 
        try:
            f = open(os.path.join("data", "insults.txt"), "r") 
            unpickler = pickle.Unpickler(f) 
            self.insults = unpickler.load() 
            f.close() 
        except:
            pass
         
    def on_unload(self): 
        self.insults = None

class RawCommand(Command):
	def trig_raw(self, bot, source, target, trigger, argument):
		if source == 'serp' or source == 'teetow':
			bot.send(argument)

class TimeCommand(Command):
	def trig_time(self, bot, source, target, trigger, argument):
		import datetime
		return datetime.datetime.now().isoformat()

class WeekCommand(Command):
	def trig_week(self, bot, source, target, trigger, argument):
		import datetime
		return "Current week: %d." % (int(datetime.datetime.now().strftime("%W"))+1)

def is_trigger(name):
	m = re.search('^trig_.+', name)
	if m:
		return True
	else:
		return False

def remove_first_five(text):
	return text[5:]

class CommandsCommand(Command):
	def trig_commands(self, bot, source, target, trigger, argument):
		triggers = []
		for command in Command.__subclasses__():
			for trigger in command.triggers:
				if trigger not in triggers:
					triggers.append(trigger)

			l = command.__dict__
			l = filter(is_trigger, l)
			l = map(remove_first_five, l)

			for trigger in l:
				if trigger not in triggers:
					triggers.append(trigger)
		
		return "Commands: %s" % ", ".join(sorted(triggers))

#	def can_trigger(self, source, trigger):
#		return source in ['serp!~serp@85.8.2.181.se.wasadata.net']

asciilize = string.maketrans("������", "aaoAAO")

_get_temp_re = re.compile('^\s*(.+)\s*$')
class TempCommand(Command):
	def __init__(self):
		pass

	def trig_temp(self, bot, source, target, trigger, argument):
		if argument:
			self.places[source] = argument
			self.save()
		else:
			if source in self.places:
				argument = self.places[source]
			else:
				argument = 'ryd'

		argument_text = argument
		argument = argument.translate(asciilize)

		url = "http://www.temperatur.nu/termo/%s/temp.txt" % argument
		response = utility.read_url(url)
		data = response["data"]

		m = _get_temp_re.match(data)

		if m:
			return "Temperature in %s: %s." % (argument_text, m.group(1))

	def save(self): 
		f = open(os.path.join("data", "places.txt"), "w") 
		p = pickle.Pickler(f) 
		p.dump(self.places) 
		f.close() 

	def on_load(self): 
		self.places = {}

		try:
			f = open(os.path.join("data", "places.txt"), "r") 
			unpickler = pickle.Unpickler(f) 
			self.places = unpickler.load() 
			f.close() 
		except:
			pass

	def on_unload(self): 
		self.places = {}

class GoogleCommand(Command):
	def trig_google(self, bot, source, target, trigger, argument):
		url = 'http://www.google.com/search?rls=en&q=' + utility.escape(argument) + '&ie=UTF-8&oe=UTF-8'

		response = utility.read_url(url)

		data = response["data"]

		# try to extract calculator result
		m = re.search('<td><img src=\/images\/calc_img\.gif width=40 height=30 alt=""><\/td><td>&nbsp;<\/td><td nowrap><h2 class=r><font size=\+1><b>(.*?)<\/b>', data)
		if m:
			answer = m.group(1)
			answer = answer.replace(' &#215;', '�').replace('<sup>', '^')
			answer = re.sub('<.+?>', '', answer)
			return answer

		# try to extract definition
		m = re.search('<img src=\/images\/dictblue\.gif width=40 height=30 alt=""><td valign=top><font size=-1>(.*?)<br>', data)
		if m:
			definition = utility.unescape(m.group(1))
			definition = re.sub('<.+?>', '', definition)
			return definition
		
		# try to extract first hit
		m = re.search('<div class=g><a href="(.*?)" class=l>(.*?)<\/a>(.*?)</div>', data)
		if m:

			text = utility.unescape(m.group(2))
			text = re.sub('<.+?>', '', text)

			link = m.group(1)

			return "%s - %s | %s" % (text, link, url)
		else:
			return url

class WikipediaCommand(Command):
	def wp_get(self, item):
		url = "http://en.wikipedia.org/wiki/%s" % utility.escape(item.replace(" ", "_"))

		response = utility.read_url(url)

		data = response["data"]
		url = response["url"]
		
		# sometimes there is a nasty table containing the first <p>. we can't allow this to happen!
		pattern = re.compile("<table.*?>.+?<\/table>", re.MULTILINE)

		data = re.sub(pattern, "", data)

		m = re.search("<p>(.+?)<\/p>", data)
		if m:
			data = utility.unescape(m.group(1))
			data = re.sub("<.+?>", "", data)
			data = re.sub("\[\d+\]", "", data)

			index = data.rfind(".", 0, 300)

			if index == -1:
				index = 300

			if index+1 < len(data) and data[index+1] == '"':
				index += 1

			data = data[0:index+1]

			if "Wikipedia does not have an article with this exact name." in data:
				data = None
		else:
			data = None

		return (url, data)

	def trig_wp(self, bot, source, target, trigger, argument):
		url, data = self.wp_get(argument)

		if data:
			return "%s - %s" % (data, url)
		else:
			return url

class AAOCommand(Command):
	triggers = ['}{|', '���', 'åäö']

	def on_trigger(self, bot, source, target, trigger, argument):
		if target == '#c++.se':
			if trigger == '���':
				return source+": Du anv�nder nog latin-1 eller liknande. Fast det �r OK. F�r den h�r g�ngen."
			elif trigger == '}{|':
				return source+": Du anv�nder nog ISO-646. Uhm."
			else:
				return source+": Du anv�nder nog utf-8. Bra shit, mannen!"
		else:
			if trigger == '���':
				return source+": Du anv�nder nog latin-1 eller liknande."
			elif trigger == '}{|':
				return source+": Du anv�nder nog ISO-646."
			else:
				return source+": Du anv�nder nog utf-8."
			
class CollectCommand(Command):
	def trig_collect(self, bot, source, target, trigger, argument):
		import gc
		obj_count = 0
		if True:
			objects = gc.get_objects()
			obj_count = len(objects)
			types = {}
			for o in objects:
				t = type(o)

				if t in types:
					types[t] += 1
				else:
					types[t] = 1

			l = []
			for key in types:
				l.append((types[key], key))

			#print sorted(l)
		gc.set_debug(gc.DEBUG_LEAK)
		return "Collected %s objects out of %s." % (gc.collect(), obj_count)
