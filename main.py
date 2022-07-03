import json
from typing import List, Dict
from fastapi import FastAPI
from modules.helpers import Helpers
from modules.constants import Constants


h = Helpers()
c = Constants()


app = FastAPI(
	title="T4Analytics Maturity Analysis API",
	description="maturity.t4analytics.com",
	version="1.0.0",
	contact={
		"name": "Necmettin Begiter",
		"email": "necmettin@t4analytics.com",
		"url": "https://t4analytics.com"
	},
	openapi_tags=[
		{"name": "maturity", "description": "Maturity Analysis"},
	],
	docs_url="/api/v1/docs",
	redoc_url=None,
	openapi_url="/api/v1/openapi.json"
)


@app.get("/", tags=["root"], include_in_schema=False)
@app.get("/api/", tags=["root"], include_in_schema=False)
@app.get("/api/v1/", tags=["root"], include_in_schema=False)
def root():
	return h.err(303, {"url": c.docsurl})


@app.post("/api/v1/submit", response_model=List)
async def save_form(record: Dict):
	record["formdata"] = json.dumps(record["formdata"])
	h.log(record)
	retval = h.adding_endpoint("forms", [record])
	h.log(retval)
	return retval

