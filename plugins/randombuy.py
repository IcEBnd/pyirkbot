# -*- coding: latin-1 -*-

# Plugin created by Merola

import re
import utility
from commands import Command

def random_product_dealextreme(max_price, hardcore):
	max_dollars = utility.currency_conversion(int(max_price), 'sek', 'usd')
	if max_dollars == None:
		return "Ajd�, nu gick n�got fel :("
	
	# Fetch the web page
	response = utility.read_url("http://www.dealextreme.com/products.dx/random.gadgets")
	data = response["data"].replace("\r\n", "")
	#data = data.replace("&nbsp;", "")
	
	product_pattern = "\<a href='\/details.dx\/sku.(\d+)' style=\" font-family: Verdana; font-size: 9pt;\"\>\s+(.+?)\s+\<\/a\>" + \
			".+?" + "style=\"font-size: 11pt;\"\>\s+\$(\d+\.\d\d)\s+\<\/font\>"
	product_iterator = re.finditer(product_pattern, data)
	
	for match in product_iterator:
		if float(match.group(3)) <= max_dollars:
			if hardcore:
				return "K�����p! http://www.dealextreme.com/shoppingcart.dx/add." + match.group(1) + "~quantity.1#_ctl0_content_pCheckout"
			else:
				return "$" + match.group(3) + ": " + match.group(2) + " | http://www.dealextreme.com/details.dx/sku." + match.group(1)
	
	return "Ingen tillr�ckligt billig produkt hittades, �ka gr�nsen eller f�rs�k igen!"

class RandomBuyCommand(Command):
	usage = "Anv�ndning: .k�p <maxkostnad i SEK> | M�nga '�' ger direktl�nk till kassan med produkt tillagd, ist�llet f�r produktdetaljer."
	
	def __init__(self):
		pass
		
	def on_privmsg(self, bot, source, target, message):
		m = re.match(r'\.k((�|ö)+)p(.*)', message)
		if not m:
			return # Not a trigger
		
		# Collect arguments
		args = [m.group(1), m.group(3).strip()]
		
		# Show usage
		if not args[1]:
			bot.tell(target, self.usage)
		
		# Ensure max price is a number
		elif not args[1].isdigit():
			bot.tell(target, "Maxkostnaden m�ste anges i hela svenska kronor!")
			
		# dealextreme.com
		else:
			# Length varies depending on encoding, so this is not a good way to do it
			hardcore = (len(args[0]) > 3)
			bot.tell(target, random_product_dealextreme(args[1], hardcore))

