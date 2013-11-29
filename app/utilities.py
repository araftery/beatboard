def hours_since(timestring):
	import datetime, time, math
	try:
		timestring = timestring[:timestring.index(".")]
	except ValueError:
		pass
	timestamp = time.mktime(time.strptime(timestring, "%Y-%m-%d %H:%M:%S"))
	return int(round((datetime.datetime.utcnow() - datetime.datetime.fromtimestamp(timestamp)).total_seconds() / 3600., 0))