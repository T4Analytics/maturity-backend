import os, sys
import random, string
from datetime import datetime
from typing import Any
import logging
import psycopg2
import psycopg2.extras

from fastapi.responses import JSONResponse

from modules.constants import Constants
c = Constants()


class Helpers:
	_db: None
	_instance = None  # used to make this a singleton

	def __new__(cls, *args, **kwargs):
		if not isinstance(cls._instance, cls):
			cls._instance = object.__new__(cls, *args, **kwargs)
		return cls._instance

	def __init__(self):
		self._db = psycopg2.connect(host=self.env("db_server", "localhost"), database=self.env("db_name", "assessment"), user=self.env("db_user", "t4"), password=self.env("db_password", "t4"))
		self._cursor = self._db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
		logging.basicConfig(filename="/tmp/t4-assessment-debug.log", level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

	@staticmethod
	def field2tuple(rows, fieldname="id"):
		lst = [row[fieldname] for row in rows]
		return tuple(lst)
	
	@staticmethod
	def field2key(rows, fieldname="id"):
		lst = {row[fieldname]: row for row in rows}
		return lst
	
	@staticmethod
	def randstr(length: int = 8):
		letters = string.ascii_lowercase + string.digits
		randy = ''.join(random.choice(letters) for i in range(length))
		self.log(["randy", randy])
		return randy
		
	@staticmethod
	def now():
		dt = datetime.now()
		return dt.strftime('%Y-%m-%d %H:%M:%S')
	
	@staticmethod
	def log(*args, **kwargs):
		if kwargs:
			logging.info(kwargs)
		if args:
			for arg in args:
				logging.info(arg)

	@staticmethod
	def env(varname, default_value):
		return os.getenv(varname, default_value)

	@staticmethod
	def err(errcode: int, data: Any):
		return JSONResponse(data, status_code=errcode)

	def db_select(self, tablename, conds={}):
		qstr = f"SELECT * FROM {tablename} "
		if conds:
			qstr += "WHERE "
			for key in conds:
				if key[-4:] == "__ne":
					qstr += f"{key[:-4]} != %({key})s AND "
				elif key[-4:] == "__gt":
					qstr += f"{key[:-4]} > %({key})s AND "
				elif key[-4:] == "__in":
					qstr += f"{key[:-4]} in %({key})s AND "
				elif key[-5:] == "__gte":
					qstr += f"{key[:-5]} >= %({key})s AND "
				elif key[-4:] == "__lt":
					qstr += f"{key[:-4]} < %({key})s AND "
				elif key[-5:] == "__lte":
					qstr += f"{key[:-5]} <= %({key})s AND "
				else:
					qstr += f"{key} = %({key})s AND "
			qstr = qstr[:-4] + " ORDER BY Id DESC"
			self._cursor.execute(qstr, conds)
		else:
			qstr += "ORDER BY Id DESC"
			self._cursor.execute(qstr)
		return self._cursor.fetchall()
		
	def db_insert(self, tablename, data, config=[]):
		if type(data) != dict:
			data = data.dict()
		if "id" in data:
			del data["id"]
		if "created_at" in data:
			del data["created_at"]
		if "updated_at" in data:
			del data["updated_at"]
		data["created_at"] = self.now()
		data["updated_at"] = self.now()
		qstr = f"INSERT INTO {tablename} ("
		valuestr = ""
		values = []
		for colname, colvalue in data.items():
			qstr += f"{colname}, "
			valuestr += "%s, "
			if type(colvalue) == datetime:
				colvalue = colvalue.strftime('%Y-%m-%d %H:%M:%S')
			values.append(colvalue)
		qstr = qstr[:-2] + ") values (" + valuestr[:-2] + ") RETURNING id"
		try:
			self._cursor.execute(qstr, values)
			if c.retids in config:
				id = self._cursor.fetchall()[0]["id"]
				self._db.commit()
				return id
			elif c.retrows in config:
				id = self._cursor.fetchall()[0]["id"]
				self._db.commit()
				row = self.db_select(tablename, {"id":id})
				return row
			else:
				return True
		except Exception:
			raise
			# print(sys.exc_info())
			# return False
	
	def db_delete(self, tablename, id):
		qstr = f"UPDATE {tablename} SET is_deleted=1 WHERE id=%s"
		try:
			self._cursor.execute(qstr, (id,))
			self._db.commit()
			return id
		except Exception:
			print(sys.exc_info())
			return False
	
	def listing_endpoint(self, tablename, additional_conds={}):
		if "is_deleted" not in additional_conds:
			additional_conds["is_deleted"] = 0
		return self.db_select(tablename, additional_conds)
	
	def adding_endpoint(self, tablename, records, additional_fields={}):
		ids = []
		for record in records:
			newrecord = additional_fields
			newrecord.update(record)
			self.log(newrecord)
			ids.append(self.db_insert(tablename, newrecord, [c.retrows]))
		return ids
	
	def deleting_endpoint(self, tablename, ids):
		for id in ids:
			self.db_delete(tablename, id)
		return ids
