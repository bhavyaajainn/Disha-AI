#!/bin/bash

source venv/bin/activate
export PYTHONPATH=.
uvicorn app.main:app --reload
