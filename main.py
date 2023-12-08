from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends
import json
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from auth import oauth2_router as auth_router
from auth import get_current_user
from auth import User
app = FastAPI()
app.include_router(auth_router)

class Questions(BaseModel):
	id: int
	question: str
	correct_answer : str
	score_weight : int


class Answer(BaseModel):
	id: int
	answer : str
	student : int
	course_id : int
class Course(BaseModel):
	id : int
	owner : int
	name : str
	course_id : int
class AnswerInput(BaseModel):
	id: int
	answer : str
	course_id : int
class CourseInput(BaseModel):
	id : int
	owner : int
	name : str
	

class QuestionsInput(BaseModel):
	question: str
	correct_answer : str
	score_weight : int
	course : int


question_filename="questions.JSON"
answer_filename = "answer.JSON"

with open(question_filename,"r") as read_file:
	question_data = json.load(read_file)

with open(answer_filename,"r") as read_file:
	answer_data = json.load(read_file)

@app.get('/')
async def hello_world(user = Depends(get_current_user)):
	return {"message": "Hello World"}

@app.get('/questions/{course_id}/{question_id}') #reworked
async def read_questions(question_id: int,course_id : int, user = Depends(get_current_user)):
	for course in question_data:
		if course["id"] == course_id:
			question_data_this = course["question"]
	for question in question_data_this:
		if  question['id'] == (question_id):
			return question
		

	raise HTTPException(
		status_code=404, detail=f'menu not found'
	)

@app.post('/answer') #reworked
async def add_answer(answer: AnswerInput, user = Depends(get_current_user)):
	answer_dict = answer.dict()
	answer_found = False
	course_found = False
	for item in question_data:
		if item['id'] == answer_dict['course_id']:
			course_found = True
			question_data_this = item["question"]
			break
	if not(course_found):
		return "Invalid Course Number"
	for answer_list in answer_data:
		if (answer_list['id'] == answer_dict['id']) and (answer_list["student"] == user["id"]) and (answer_list["course_id"] == answer_dict["course_id"]):
			item_found = True
			return "Answer "+str(answer_dict['id'])+" exists."
	if not (answer_found):
		question_found = False
		for question_list in question_data_this:
			
			if question_list['id'] == answer_dict['id']:
				question_found = True
				answer_input = {"id" : answer.id, "answer" : answer.answer, "student" : user["id"], "course_id" : answer.course_id}
				answer_data.append(answer_input)
				with open(answer_filename,"w") as write_file:
					json.dump(answer_data, write_file)

				return answer_dict  
		if not (question_found):
			return "No question exists with that number"
		raise HTTPException(
			status_code=404, detail=f'item not found'
	)

@app.get('/score/{course_id}') #reworked
async def get_score(course_id = int,user = Depends(get_current_user)):
	course_id = int(course_id)
	score = 0
	found = False
	for course in question_data:
		if course["id"] == course_id:
			question_data_this = course["question"]
			found = True
	if not(found):
		return "course not found"	
	for answer_list in answer_data:
		for question_list in (question_data_this):
			if ((answer_list['answer'] == question_list['correct_answer'] ) and (answer_list['id'] == question_list['id']  ) and (answer_list["course_id"] == course_id)):
				score += question_list['score_weight']
	return score
	

@app.delete('/answer/{course_id}/{question_id}') #reworked
async def delete_answer(course_id : int, question_id : int,user = Depends(get_current_user)):
	found = False
	course_id = int(course_id)
	question_id = int(question_id)
	for questions_idx, answer_list in enumerate(answer_data):
		if (answer_list['id'] == question_id) and (answer_list["student"] == user["id"]) and (answer_list["course_id"] == course_id):
			answer_data.pop(questions_idx)
			found = True
			break
	if (found):
		with open(answer_filename,"w") as write_file:
			json.dump(answer_data, write_file)
		return "updated"
	else:
		return "not found"
@app.get('/answer')
async def get_all_answer(user = Depends(get_current_user)):
	return answer_data

@app.get('/questions')
async def get_all_question(user = Depends(get_current_user)):
	return question_data

@app.put('/answer/{course_id}/{question_id}') #reworked
async def change_answer(course_id : int, question_id : int, answer : str, user = Depends(get_current_user)):
	course_id = int(course_id)
	question_id = int(question_id)	
	found = False
	for questions_idx, answer_list in enumerate(answer_data):
		if (answer_list['id'] == question_id) and (answer_list["student"] == user["id"]) and (answer_list["course_id"] == course_id):
			answer_data[questions_idx]["answer"] = answer
			with open(answer_filename,"w") as write_file:
				json.dump(answer_data, write_file)
			return "Updated"
			found = True
			break

	return "not found"
@app.post('/questions/{course_id}') #reworked
async def add_question(course_id : int ,questions : Questions,  user = Depends(get_current_user)):
	course_id = int(course_id)
	if not(user["admin"]):
		return "Access denied"
	question_dict = questions.dict()
	question_found = False
	for course in question_data:
		if course["id"] == course_id:
			question_data_this = course["question"]
			break

	for questions_list in question_data_this:
		if questions_list['id'] == question_dict['id']:
			item_found = True
			return "Questions number "+str(question_dict['id'])+" exists."
	if not (question_found):
		question_data_this.append(question_dict)
		with open(question_filename,"w") as write_file:
			json.dump(question_data, write_file)

		return question_dict  
	raise HTTPException(
			status_code=404, detail=f'item not found'
	)

@app.delete('/questions/{course_id}/{questions_id}') #reworked
async def delete_questions(course_id : int, questions_id : int,user = Depends(get_current_user)):
	course_id = int(course_id)
	questions_id = int(questions_id)
	if not(user["admin"]):
		return "Access denied"
	for course in question_data:
		if course["id"] == course_id:
			question_data_this = course["question"]
	for questions_idx, questions_item in enumerate(question_data_this):
		if questions_item['id'] == questions_id:
			question_data_this.pop(questions_idx)
			with open(question_filename,"w") as write_file:
				json.dump(question_data, write_file)
			return "updated"
	raise HTTPException(
			status_code=404, detail=f'item not found'
	)

@app.post('/course')
async def add_course(first_question : Questions,user = Depends(get_current_user)):
	course_id = 0
	if not(user["admin"]):
		return "Access denied"
	for item in question_data:
		if course_id <= item['id']:
			course_id = item['id'] + 1
	insert_course = {"id" : course_id, "question" : [{"id" : first_question.id, "question" : first_question.question, "correct_answer" : first_question.correct_answer}]}
	question_data.append(insert_course)
	with open(question_filename,"w") as write_file:
		json.dump(question_data, write_file)
	return "success"