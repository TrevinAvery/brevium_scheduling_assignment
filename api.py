import requests
import json


class SchedulingApiError(Exception):
	pass

class InvalidTokenError(SchedulingApiError):
	# HTTP code 401
	pass

class StoppedError(SchedulingApiError):
	# HTTP code 405
	pass

class NoMoreAppointmentsError(SchedulingApiError):
	# HTTP code 204
	pass

class UnknownResponseCodeError(SchedulingApiError):
	pass


class AppointmentInfo:

	def __init__(self, object_dict):
		self.doctor_id = object_dict['doctorId']
		self.person_id = object_dict['personId']
		self.appointment_time = object_dict['appointmentTime']
		self.is_new_patient_appointment = object_dict['isNewPatientAppointment']
	
	def __str__(self) -> str:
		return f'doc: {self.doctor_id}, person: {self.person_id}, time: {self.appointment_time}, new: {self.is_new_patient_appointment}'
	
	def __repr__(self) -> str:
		return str(self)

class AppointmentInfoRequest(AppointmentInfo):

	def __init__(self, object_dict):
		super().__init__(object_dict)
		self.request_id = object_dict['requestId']

	def to_dict(self) -> dict:
		return {
			'doctorId': self.doctor_id,
			'personId': self.person_id,
			'appointmentTime': self.appointment_time,
			'isNewPatientAppointment': self.is_new_patient_appointment,
			'requestId': self.request_id,
		}

class AppointmentRequest:

	def __init__(self, object_dict):
		self.request_id = object_dict['requestId']
		self.person_id = object_dict['personId']
		self.preferred_days = object_dict['preferredDays']
		self.preferred_docs = object_dict['preferredDocs']
		self.is_new = object_dict['isNew']

	def __str__(self) -> str:
		return f'req: {self.request_id}, person: {self.person_id}, days: {self.preferred_days}, docs: {self.preferred_docs}, new: {self.is_new}'
	
	def __repr__(self) -> str:
		return str(self)


class SchedulingApi:

	endpoint = 'http://scheduling-interview-2021-265534043.us-west-2.elb.amazonaws.com/api/Scheduling/'

	def __init__(self, token):
		self.token = token
		
	def _request(self, method, path, body=None, object_hook=None):
		response = requests.request(method, self.endpoint + path, params={'token': self.token}, json=body)
		
		if response.status_code == 200:
			return json.loads(response.content, object_hook=object_hook) if object_hook else None
		
		elif response.status_code in [400, 401]:
			raise InvalidTokenError()
		elif response.status_code == 204:
			raise NoMoreAppointmentsError()
		elif response.status_code == 405:
			raise StoppedError()
		else:
			raise UnknownResponseCodeError(response.status_code)

	def start(self):
		"""Hit this endpoint to reset the test system before each 'run' of your program."""
		return self._request('post', 'Start')

	def stop(self):
		"""This is an optional endpoint that will allow you to mark a test run as 'done'.
		The API will then return the current schedule as you have requested it,
		for your debugging pleasure."""
		return self._request('post', 'Stop', object_hook=AppointmentInfo)

	def get_appointment_request(self):
		"""Returns the next appointment request to be serviced, or None if there are no more requests."""
		try:
			return self._request('get', 'AppointmentRequest', object_hook=AppointmentRequest)
		except NoMoreAppointmentsError:
			return None

	def get_schedule(self):
		"""Returns the initial monthly schedule."""
		return self._request('get', 'Schedule', object_hook=AppointmentInfo)
	
	def set_schedule(self, appointment: AppointmentInfoRequest):
		"""Marks an appointment slot as taken."""
		return self._request('post', 'Schedule', body=appointment.to_dict())


class MockSchedulingApi:
	"""This is a fake version of the SchedulingApi class that does not actually all the external API.
	This is intended for testing purposes because the real API can be really slow sometimes."""

	def __init__(self, token):
		self.token = token
		self.app_request_gen = None
		
	def _request(self, method, path, object_hook=None):
		response = requests.request(method, self.endpoint + path, params={'token': self.token})
		
		if response.status_code == 200:
			return json.loads(response.content, object_hook=object_hook) if object_hook else None
		
		elif response.status_code in [400, 401]:
			raise InvalidTokenError()
		elif response.status_code == 204:
			raise NoMoreAppointmentsError()
		elif response.status_code == 405:
			raise StoppedError()
		else:
			raise UnknownResponseCodeError(response.status_code)

	def start(self):
		"""Hit this endpoint to reset the test system before each 'run' of your program."""
		return

	def stop(self):
		"""This is an optional endpoint that will allow you to mark a test run as 'done'.
		The API will then return the current schedule as you have requested it,
		for your debugging pleasure."""
		return

	def _appointment_request_gen(self):
		request_dicts = [
			{'requestId': 0, 'personId': 1, 'preferredDays': ['2021-11-01T00:00:00Z', '2021-11-03T00:00:00Z'], 'preferredDocs': [2], 'isNew': True},
			{'requestId': 1, 'personId': 1, 'preferredDays': ['2021-11-24T00:00:00Z', '2021-11-25T00:00:00Z'], 'preferredDocs': [2, 3], 'isNew': False},
			{'requestId': 2, 'personId': 2, 'preferredDays': ['2021-11-03T00:00:00Z'], 'preferredDocs': [1], 'isNew': True},
			{'requestId': 3, 'personId': 3, 'preferredDays': ['2021-11-04T00:00:00Z', '2021-11-05T00:00:00Z'], 'preferredDocs': [1, 2, 3], 'isNew': False},
			{'requestId': 4, 'personId': 3, 'preferredDays': ['2021-11-18T00:00:00Z', '2021-11-19T00:00:00Z', '2021-11-22T00:00:00Z'], 'preferredDocs': [2, 3], 'isNew': False},
			{'requestId': 5, 'personId': 4, 'preferredDays': ['2021-11-22T00:00:00Z', '2021-11-23T00:00:00Z', '2021-11-24T00:00:00Z', '2021-11-25T00:00:00Z', '2021-11-26T00:00:00Z', '2021-11-29T00:00:00Z', '2021-11-30T00:00:00Z', '2021-12-01T00:00:00Z', '2021-12-02T00:00:00Z', '2021-12-03T00:00:00Z'], 'preferredDocs': [3], 'isNew': False},
			{'requestId': 6, 'personId': 4, 'preferredDays': ['2021-11-22T00:00:00Z', '2021-11-23T00:00:00Z', '2021-11-24T00:00:00Z', '2021-11-25T00:00:00Z', '2021-11-26T00:00:00Z', '2021-11-29T00:00:00Z', '2021-11-30T00:00:00Z', '2021-12-01T00:00:00Z', '2021-12-02T00:00:00Z', '2021-12-03T00:00:00Z'], 'preferredDocs': [3], 'isNew': False},
			{'requestId': 7, 'personId': 5, 'preferredDays': ['2021-11-18T00:00:00Z', '2021-11-19T00:00:00Z'], 'preferredDocs': [2, 3], 'isNew': False},
			{'requestId': 8, 'personId': 6, 'preferredDays': ['2021-12-06T00:00:00Z', '2021-12-07T00:00:00Z'], 'preferredDocs': [2], 'isNew': False},
			{'requestId': 9, 'personId': 10, 'preferredDays': ['2021-11-30T00:00:00Z'], 'preferredDocs': [1], 'isNew': True},
			{'requestId': 10, 'personId': 10, 'preferredDays': ['2021-12-23T00:00:00Z', '2021-12-24T00:00:00Z'], 'preferredDocs': [1], 'isNew': False},
			{'requestId': 11, 'personId': 12, 'preferredDays': ['2021-12-02T00:00:00Z', '2021-12-03T00:00:00Z'], 'preferredDocs': [1], 'isNew': True},
			{'requestId': 12, 'personId': 13, 'preferredDays': ['2021-12-02T00:00:00Z', '2021-12-03T00:00:00Z'], 'preferredDocs': [1], 'isNew': True},
			{'requestId': 13, 'personId': 16, 'preferredDays': ['2021-12-15T00:00:00Z', '2021-12-22T00:00:00Z'], 'preferredDocs': [3], 'isNew': False},
			{'requestId': 14, 'personId': 16, 'preferredDays': ['2021-12-27T00:00:00Z', '2021-12-28T00:00:00Z', '2021-12-29T00:00:00Z', '2021-12-30T00:00:00Z'], 'preferredDocs': [3], 'isNew': False},
			{'requestId': 15, 'personId': 19, 'preferredDays': ['2021-12-14T00:00:00Z', '2021-12-15T00:00:00Z', '2021-12-16T00:00:00Z'], 'preferredDocs': [3], 'isNew': True},
			{'requestId': 16, 'personId': 21, 'preferredDays': ['2021-12-24T00:00:00Z'], 'preferredDocs': [3], 'isNew': True},
		]

		requests = [AppointmentRequest(request_dict) for request_dict in request_dicts]

		for request in requests:
			yield request
	
		yield None

	def get_appointment_request(self):
		"""Returns the next appointment request to be serviced, or None if there are no more requests."""

		if self.app_request_gen is None:
			self.app_request_gen = self._appointment_request_gen()		

		return next(self.app_request_gen)

	def get_schedule(self):
		appointment_dicts = [
			{'doctorId': 2, 'personId': 1, 'appointmentTime': '2021-11-08T08:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 3, 'personId': 1, 'appointmentTime': '2021-12-15T09:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 3, 'personId': 4, 'appointmentTime': '2021-12-15T13:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 3, 'personId': 5, 'appointmentTime': '2021-12-15T11:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 2, 'personId': 2, 'appointmentTime': '2021-11-16T12:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 3, 'personId': 2, 'appointmentTime': '2021-12-09T14:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 3, 'personId': 2, 'appointmentTime': '2021-12-24T10:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 2, 'personId': 3, 'appointmentTime': '2021-12-24T09:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 1, 'personId': 9, 'appointmentTime': '2021-12-24T16:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 1, 'personId': 11, 'appointmentTime': '2021-12-24T13:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 3, 'personId': 3, 'appointmentTime': '2021-12-01T10:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 1, 'personId': 4, 'appointmentTime': '2021-11-09T15:00:00Z', 'isNewPatientAppointment': True},
			{'doctorId': 2, 'personId': 5, 'appointmentTime': '2021-11-12T16:00:00Z', 'isNewPatientAppointment': True},
			{'doctorId': 3, 'personId': 5, 'appointmentTime': '2021-12-02T11:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 1, 'personId': 15, 'appointmentTime': '2021-12-02T14:00:00Z', 'isNewPatientAppointment': True},
			{'doctorId': 2, 'personId': 22, 'appointmentTime': '2021-12-02T15:00:00Z', 'isNewPatientAppointment': True},
			{'doctorId': 3, 'personId': 24, 'appointmentTime': '2021-12-02T15:00:00Z', 'isNewPatientAppointment': True},
			{'doctorId': 2, 'personId': 23, 'appointmentTime': '2021-12-02T16:00:00Z', 'isNewPatientAppointment': True},
			{'doctorId': 3, 'personId': 25, 'appointmentTime': '2021-12-02T16:00:00Z', 'isNewPatientAppointment': True},
			{'doctorId': 2, 'personId': 6, 'appointmentTime': '2021-11-22T16:00:00Z', 'isNewPatientAppointment': True},
			{'doctorId': 2, 'personId': 6, 'appointmentTime': '2021-11-30T10:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 1, 'personId': 11, 'appointmentTime': '2021-11-30T16:00:00Z', 'isNewPatientAppointment': True},
			{'doctorId': 2, 'personId': 6, 'appointmentTime': '2021-12-21T09:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 1, 'personId': 12, 'appointmentTime': '2021-12-21T14:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 3, 'personId': 7, 'appointmentTime': '2021-11-23T08:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 3, 'personId': 7, 'appointmentTime': '2021-12-07T10:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 3, 'personId': 7, 'appointmentTime': '2021-12-22T14:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 3, 'personId': 8, 'appointmentTime': '2021-11-26T15:00:00Z', 'isNewPatientAppointment': True},
			{'doctorId': 3, 'personId': 8, 'appointmentTime': '2021-12-06T13:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 3, 'personId': 8, 'appointmentTime': '2021-12-20T14:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 2, 'personId': 9, 'appointmentTime': '2021-11-29T16:00:00Z', 'isNewPatientAppointment': True},
			{'doctorId': 1, 'personId': 11, 'appointmentTime': '2021-12-16T11:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 1, 'personId': 20, 'appointmentTime': '2021-12-16T16:00:00Z', 'isNewPatientAppointment': True},
			{'doctorId': 1, 'personId': 14, 'appointmentTime': '2021-12-03T16:00:00Z', 'isNewPatientAppointment': True},
			{'doctorId': 1, 'personId': 14, 'appointmentTime': '2021-12-17T14:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 1, 'personId': 16, 'appointmentTime': '2021-12-13T08:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 1, 'personId': 17, 'appointmentTime': '2021-12-13T12:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 2, 'personId': 18, 'appointmentTime': '2021-12-14T13:00:00Z', 'isNewPatientAppointment': False},
			{'doctorId': 2, 'personId': 19, 'appointmentTime': '2021-12-23T14:00:00Z', 'isNewPatientAppointment': False}
		]

		appointments = [AppointmentInfo(appointment_dict) for appointment_dict in appointment_dicts]

		return appointments
	
	def set_schedule(self, appointment: AppointmentInfoRequest):
		"""Marks an appointment slot as taken."""
		return
