import os


class Constants:
	baseurl = "https://maturity.t4analytics.com/"
	apiurl = "https://maturity.t4analytics.com/api/v1/"
	docsurl = "https://maturity.t4analytics.com/api/v1/docs"

	retids = "retids"  # return ids
	retrows = "retrows"  # return rows

	def __init__(self):
		if os.getenv("environment", "develop") == "develop":
			self.baseurl = "https://madev.t4analytics.com/"
			self.apiurl = "https://madev.t4analytics.com/api/v1/"
			self.docsurl = "https://madev.t4analytics.com/api/v1/docs"
