# -*- coding: utf-8 -*-
from flask import Flask,jsonify
from flask_restful import reqparse, abort, Api, Resource
from flask_pymongo import PyMongo


app = Flask(__name__)
api = Api(app)
app.config['MONGO_DBNAME'] = 'Guoke'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/Guoke'
mongo = PyMongo(app, config_prefix='MONGO')

TODOS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': '?????'},
    'todo3': {'task': 'profit!'},
}


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist.".format(todo_id))

parser = reqparse.RequestParser()
parser.add_argument('task')

# Find all Guoke_info
# Show question list

class Questions(Resource):
    def get(self):
        count = mongo.db.Guoke_info.find().count()
        topTwentyFocus = mongo.db.Guoke_info.find().sort('Focus', -1).limit(20)
        listQuestion = []
        for question in topTwentyFocus:
            listQuestion.append({'title': question['title'], 'Focus': question['Focus']})
        return jsonify(listQuestion, count)

# Todo
# shows a single todo item and lets you delete a todo item
class Todo(Resource):
    def get(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204

    def put(self, todo_id):
        args = parser.parse_args()
        task = {'task': args['task']}
        TODOS[todo_id] = task
        return task, 201


# TodoList
# shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    def get(self):
        return TODOS

    def post(self):
        args = parser.parse_args()
        todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
        todo_id = 'todo%i' % todo_id
        TODOS[todo_id] = {'task': args['task']}
        return TODOS[todo_id], 201

##
## Actually setup the Api resource routing here
##
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<todo_id>')
api.add_resource(Questions, '/questions')

if __name__ == '__main__':
    app.run(debug=True)