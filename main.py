from schedule import Schedule
from api import *
from pprint import pprint


if __name__ == '__main__':

	print('Please enter a valid API token')
	token = input()

	api = SchedulingApi(token)

	print('Start')
	api.start()
	
	print('Get initial schedule')
	appointments = api.get_schedule()
	schedule = Schedule(appointments)

	print('Schedule')
	pprint(schedule)

	print('Begin scheduling appointments')
	while request := api.get_appointment_request():
		print(request, flush=True)
		appointment = schedule.get_valid_appointment(request)
		schedule.add_appointment(appointment)
		api.set_schedule(appointment)

	print('Stop and show the results')
	final = api.stop()
	pprint(final)
