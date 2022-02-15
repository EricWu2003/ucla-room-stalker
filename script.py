token = "OTIzMjcyMjQyNzY5NTc2MDI3.YcNmSA.qeLJ82Dr_N_pJJcI_xHcSpuav1U"

channels = {
	"hedrick":923236228906750022,
	"hedrickmusic":923236283113934918,
	"hedrickstudy":923236506846494801,
	"hitch":923236543206948964,
	"meditation":923236565042495508,
	"movement":923236587318415401,
	"music":923236605014192191,
	"rieber":923236644600049694,
	"sproulmusic":923236681589596240,
	"sproulstudy":923236709313957949,
	"general":923236060220231694,
	"changes":923285913176526849,
	"deneve":939684115668684820,
}
room_channel_names = {"hedrick", "hedrickmusic", "hedrickstudy", "hitch", "meditation", "movement", "music", "rieber", "sproulmusic", "sproulstudy",} 
import discord
import reservation_checker as	 rc
import time
from datetime import datetime
from datetime import timedelta
from pytz import timezone, utc
import json
import os
import time, asyncio
import sys

#time.sleep(60) #just to make sure the time becomes convenient

script_path = "/home/ericwu/web_scraping"
#script_path = os.getcwd()

def get_pst_time():
	date_format='%Y-%m-%dT%H-%M-%S'
	date = datetime.now(tz=utc)
	date = date.astimezone(timezone('US/Pacific'))
	pstDateTime=date.strftime(date_format)
	return pstDateTime
def get_pst_date():
	return get_pst_time().split('T')[0]
def give_occurences(string):
	indecies = [i for i in range(len(string)) if string[i] == "1"]
	output = {}
	next_contiguous = -1
	for index in indecies:
		if index == next_contiguous:
			output[max(output.keys())] += 1
		else:
			output[index] = 1
		next_contiguous = index +1
	return output




class MyClient(discord.Client):

	async def send(self, channel, msg):
		while True:
			try:
				await channel.send(msg)
				break
			except Exception as e:
				print("waiting 2 seconds...")
				print(e)
				await asyncio.sleep(2)

	async def on_ready(self):
		global channels
		print(f'Logged on as {self.user}!')
		channels = {k:client.get_channel(v) for k, v in channels.items()}



		print(time.time())
		t = time.time()
		num_requests = 0


		data = {r:{} for r in rc.roomtypes}

		try:

			for room in rc.roomtypes:
				await channels[room].purge(limit = 200, check = lambda m:m.author == client.user)
				days = rc.find_available_days(room)
				for day in days[:15]:
					dotw = datetime.strptime(day, "%Y-%m-%d").strftime("%a")

					string_to_send = f"```🟨🟨🟨{day} ({dotw})🟨🟨🟨"

					data[room][day] = rc.get_data(room, day)
					if data[room][day] == None:
						print("let's try this another time")
						return
					#print(list(data[room][day].items()))
					for k, v in sorted(list(data[room][day].items()), key = lambda x: x[0]):   #we sort the keys by the value of the dictionary, which is the room
						s = rc.format_data(k, v, day)
						string_to_send += ("\n" + s)
					
					string_to_send += "```"
					await self.send(channels[room], string_to_send)
					time.sleep(3.4)
					num_requests += 1
			print("requests: " + str(num_requests))
			print(time.time())
			print(t - time.time())
		except Exception as e:
			print(e)
			return

		old_data = {}
		with open(os.path.join(script_path, "logs", max(os.listdir(os.path.join(script_path, "logs"))) ), 'r') as f:
			old_data = json.load(f)

		with open(os.path.join(script_path, f'logs/{get_pst_time()}.txt'), 'w') as f:
			f.write(json.dumps(data, indent="\t", sort_keys=True))


		# with open("logs/2021-12-22T20-15-08.txt") as f:
		#     old_data = json.load(f)
		# with open("logs/2021-12-22T20-59-35.txt") as f:
		#     data = json.load(f)
		
		slots_just_closed = {k:v for k, v in old_data.items()}
		slots_just_opened = {k:v for k, v in old_data.items()}



		text_to_send = ""

		for roomtype in old_data.keys():
			#we can assume roomtype is in data.keys()
			for date in old_data[roomtype].keys():
				if date in data[roomtype].keys():        
					for roomname in old_data[roomtype][date].keys():
						if roomname in data[roomtype][date].keys():
							old = old_data[roomtype][date][roomname]
							new = data[roomtype][date][roomname]

							#print(old, new)
							slots_just_closed[roomtype][date][roomname] = ["1" if (old[i] == "1" and new[i] == "0") else "0" for i in range(48)]
							slots_just_closed[roomtype][date][roomname] = "".join(slots_just_closed[roomtype][date][roomname])

							today = get_pst_date()
							for location, length in give_occurences(slots_just_closed[roomtype][date][roomname]).items():
								interval_beginning_time = (datetime.strptime(date, '%Y-%m-%d') + timedelta(minutes = 30*location)).strftime("%Y-%m-%dT%H-%M-%S")
								
								#print(interval_beginning_time)

								if interval_beginning_time < get_pst_time():
									continue
								formatted_interval_beginning_time = (datetime.strptime(date, '%Y-%m-%d') + timedelta(minutes = 30*location)).strftime("%a, %m-%d (%H:%M)")


								#dotw = datetime.strptime(date, "%Y-%m-%d").strftime("%a")
								text_to_send += f"JUST CLOSED: {roomname} for {length/2} hours on {formatted_interval_beginning_time}\n"
							

						   
							slots_just_opened[roomtype][date][roomname] = ["1" if (old[i] == "0" and new[i] == "1") else "0" for i in range(48)]
							slots_just_opened[roomtype][date][roomname] = "".join(slots_just_opened[roomtype][date][roomname])
							for location, length in give_occurences(slots_just_opened[roomtype][date][roomname]).items():
								formatted_interval_beginning_time = (datetime.strptime(date, '%Y-%m-%d') + timedelta(minutes = 30*location)).strftime("%a, %m-%d (%H:%M)")
								#dotw = datetime.strptime(date, "%Y-%m-%d").strftime("%a")
								text_to_send += f"JUST OPENED: {roomname} for {length/2} hours on {formatted_interval_beginning_time}\n"

						else:
							pass
						   
				else:
					pass
		if text_to_send:
			await self.send(channels['changes'], text_to_send)
		with open(os.path.join(script_path, f'changelog/changes-{get_pst_time()}.txt'), 'w') as f:
			f.write(text_to_send)
		
		sys.exit()

		




	async def on_message(self, message):
		if message.author == client.user:
			return
		
		print(f'Message from {message.author}: {message.content}')
		

client = MyClient()
client.run(token)
