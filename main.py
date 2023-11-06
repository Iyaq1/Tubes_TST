from typing import Annotated
from fastapi import FastAPI, HTTPException, Form
import json
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
app = FastAPI()


class Questions(BaseModel):
	id: int
	question: str
	correct_answer : str
	score_weight : int
class Answer(BaseModel):
	id: int
	answer : str
	

json_filename="questions.JSON"

with open(json_filename,"r") as read_file:
	data = json.load(read_file)

@app.get('/')
async def hello_world():
	return {"message": "Hello World"}

@app.get('/questions/{question_id}')
async def read_questions(question_id: int):
	print(question_id)
	for question in data["questions"]:
		print(question)
		if  question["id"] == (question_id):
			return question
		

	raise HTTPException(
		status_code=404, detail=f'menu not found'
	)

@app.post('/answer')
async def add_answer(answer: Answer):
	answer_dict = answer.dict()
	answer_found = False
	for answer_list in data['user_answers']:
		if answer_list['id'] == answer_dict['id']:
			item_found = True
			return "Answer "+str(answer_dict['id'])+" exists."
	if not (answer_found):
		question_found = False
		for question_list in data["questions"]:
			if question_list['id'] == answer_dict['id']:
				question_found = True
				data['user_answers'].append(answer_dict)
				with open(json_filename,"w") as write_file:
					json.dump(data, write_file)

				return answer_dict  
		if not (question_found):
			return "No question exists with that number"
		raise HTTPException(
			status_code=404, detail=f'item not found'
	)

@app.get('/score')
async def get_score():
	score = 0
	for answer_list in data['user_answers']:
		for question_list in (data['questions']):
			if ((answer_list['answer'] == question_list['correct_answer'] ) and (answer_list['id'] == question_list['id']  )):
				score += question_list['score_weight']
	return score
	

@app.delete('/answer')
async def delete_answer():

	for questions_idx, answer_item in enumerate(data['user_answers']):
		if answer_item['id'] != 0:
			data['user_answers'].pop(questions_idx)
			
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
	return "updated"

@app.get('/answer')
async def get_all_answer():
	return data['user_answers']

@app.get('/questions')
async def get_all_question():
	return data['questions']

@app.put('/answer')
async def change_answer(answer :Answer):

	answer_dict = answer.dict()
	answer_found = False
	question_found = False
	for answer_idx, answer_list in enumerate(data["user_answers"]):
		if answer_list['id'] == answer_dict['id']:
			for question_list in data["questions"]:
				if question_list['id'] == answer_dict['id']:
					data["user_answers"][answer_idx] = answer_dict
					answer_found = True
					question_found = True
					with open(json_filename,"w") as write_file:
						json.dump(data, write_file)
					return "Updated"
	if not (answer_found): 
		return "no Answer found"
	if not (question_found):
		return "no Answer found"
	raise HTTPException(
		status_code=404, detail=f'item not found'
	)
