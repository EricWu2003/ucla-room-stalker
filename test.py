# import requests
# from urllib.request import urlopen
# from bs4 import BeautifulSoup


# params = {'type': 'hedrick', 'duration': '30', 'date': '2022-01-05'}
# r = requests.get("https://reslife.ucla.edu/reserve", data=params)

# bsObj = BeautifulSoup(urlopen(f"http://reslife.ucla.edu/reserve?type=hedrick&duration=30&date=2022-01-05"), "html.parser")
# #bsObj = BeautifulSoup(r.content, "html.parser")



# print('done')

# import os
# print(max(os.listdir("logs")))

# def give_occurences(string):
#     indecies = [i for i in range(len(string)) if string[i] == "1"]
#     output = {}
#     next_contiguous = -1
#     for index in indecies:
#         if index == next_contiguous:
#             output[max(output.keys())] += 1
#         else:
#             output[index] = 1
#         next_contiguous = index +1
#     return output


# print(give_occurences("10000011111011111100000000111000000011111000010"))


import discord
import asyncio

class MyClient(discord.Client):
	async def send(self, channel, msg):
		while True:
			try:
				await channel.send(msg)
				break
			except Exception as e:
				print(e)
				print("waiting 2 seconds...")
				asyncio.sleep(2)
	
	
	async def on_ready(self):
		print('Logged on as {0}!'.format(self.user))
		
		
		await self.send(self.get_channel(923236060220231694), "e"*10000)


	async def on_message(self, message):
		if message.author == client.user:
			return
		
		await self.send(message.channel, "Hello")
		print('Message from {0.author}: {0.content}'.format(message))

client = MyClient()
client.run("OTIzMjcyMjQyNzY5NTc2MDI3.YcNmSA.qeLJ82Dr_N_pJJcI_xHcSpuav1U")

















# print('done')

