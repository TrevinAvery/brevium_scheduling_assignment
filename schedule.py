from datetime import datetime
from bisect import bisect, insort
from collections import defaultdict
from api import *

class Schedule:

	_datetime_format = '%Y-%m-%dT%H:%M:%SZ'

	doctors = defaultdict(list)
	persons = defaultdict(list)

	def __init__(self, appointments: list = None) -> None:
		if appointments:
			for appointment in appointments:
				self.add_appointment(appointment)

	def __str__(self) -> str:
		return f'docs: {self.doctors}, persons: {self.persons}'

	def __repr__(self) -> str:
		return str(self)

	def _date_from_str(self, date_str: str) -> datetime:
		return datetime.strptime(date_str, self._datetime_format)

	def _str_from_date(self, date: datetime) -> str:
		return datetime.strftime(date, self._datetime_format)

	def add_appointment(self, appointment: AppointmentInfo) -> None:
		date = self._date_from_str(appointment.appointment_time)
		insort(self.doctors[appointment.doctor_id], date)
		insort(self.persons[appointment.person_id], date.date())

	def get_valid_appointment(self, request: AppointmentRequest) -> AppointmentInfoRequest:

		for day in request.preferred_days:
			date = self._date_from_str(day).date()

			# make sure date is a weekday
			if date.weekday() >= 5:
				continue

			# make sure date is in November or December
			if date.month < 11:
				continue

			# make sure date is not within a week of an existing appointment
			person_apps = self.persons[request.person_id]
			date_idx = bisect(person_apps, date)
			if date_idx > 0:
				before = person_apps[date_idx - 1]
				if abs(before - date).days < 7:
					continue
			
			if date_idx < len(person_apps):
				after = person_apps[date_idx]
				if abs(after - date).days < 7:
					continue

			# make sure a doctor is available
			for doctor_id in request.preferred_docs:

				doc_apps = self.doctors[doctor_id]

				# reduce possible times if new
				earliest_time = 8
				if request.is_new:
					earliest_time = 15
				latest_time = 16

				# check for available hours
				for time in range(earliest_time, latest_time + 1):
					app_time = datetime(date.year, date.month, date.day, time)
					app_time_idx = bisect(doc_apps, app_time)

					if app_time_idx > 0:
						before = doc_apps[app_time_idx - 1]
						if before == app_time:
							continue
					
					if app_time_idx < len(doc_apps):
						after = doc_apps[app_time_idx]
						if after == app_time:
							continue

					# the spot is avialable
					return AppointmentInfoRequest({
						'doctorId': doctor_id,
						'personId': request.person_id,
						'appointmentTime': self._str_from_date(app_time),
						'isNewPatientAppointment': request.is_new,
						'requestId': request.request_id,
					})
		else:
			raise Exception('No valid appointment time found')
