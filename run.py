from flask import Flask, render_template, redirect, request, jsonify, abort
from pymongo import MongoClient
from classes import *
import re
import os

# config system
app = Flask(__name__)
app.config.update(dict(SECRET_KEY='yoursecretkey'))
MONGO_URL = os.environ.get('MONGODB_URI') 
client = MongoClient(MONGO_URL)
#client = MongoClient('localhost:27017')
db = client.heroku_kwvpv399
session = {'search':False, 'add':True, 'update':True, 'delete':True,'data':[], 'message':''}

if db.settings.find({'name': 'task_id'}).count() <= 0:
    print("task_id Not found, creating....")
    db.settings.insert_one({'name':'task_id', 'value':0})

def updateTaskID(value):
    task_id = db.settings.find_one()['value']
    task_id += value
    db.settings.update_one(
        {'name':'task_id'},
        {'$set':
            {'value':task_id}
        })

def validate_add_contact(number,name):
    if not (number.isnumeric() and len(number) == 10 and re.match("^[a-zA-Z0-9_ ]*$", name) and not db.tasks.find_one({"number":number})):
       session['add'] = False
       session['message'] = "Invalid Entry"

def addContact(number,name):
    validate_add_contact(number,name)
    if session['add'] :
       task_id = db.settings.find_one()['value']
       print task_id
    
       task = {'id':task_id, 'number':number, 'name':name}

       db.tasks.insert_one(task)
       updateTaskID(1)
    return redirect('/')


@app.route('/api/contacts', methods=['POST'])
def rest_add_contact():
    session['add'] = True
    session['message'] = ''
    if not request.json or not 'number' in request.json or not 'name' in request.json:
        abort(400)
    number = request.json['number']
    name = request.json['name']
    addContact(number,name)
    return jsonify({'result': session['add'], 'message':session['message']})

def deleteContact(name):
    contact_exists("name",name)
    if session['delete']:
       db.tasks.delete_many({'name':name})
    return redirect('/')

@app.route('/api/contacts', methods=['DELETE'])
def rest_delete_contact():
    session['delete'] = True
    session['message'] = ''

    if not request.json or not 'name' in request.json :
        abort(400)
    name = request.json['name']
    deleteContact(name)
    return jsonify({'result': session['delete'], 'message':session['message']})

def contact_exists(typ,name):
    if not db.tasks.find_one({typ:name}):
       if typ == "name":
          session['delete'] = False
       else:
          session['update'] = False
       session['message'] = "No contact exists."

def updateContact(key,name):
    contact_exists("number",key)
    if session['update']:
       db.tasks.update_one(
           {"number": key},
           {"$set":
               {"name": name}
           }
       )
    return redirect('/')

@app.route('/api/contacts', methods=['PUT'])
def rest_put_contact():
    session['update'] = True
    session['message'] = ''
    if not request.json or not 'number' in request.json or not 'name' in request.json :
        abort(400)
    name = request.json['name']
    number = request.json['number']
    updateContact(number,name)
    return jsonify({'result': session['update'], 'message':session['message']})

def searchContact(form):
    name = form.name.data
    number = form.number.data
    
    sdata = []
    if(name):
        print "/"+name+"/i"
        docs = db.tasks.find(
                   {"name":{ '$regex': name }}
               )
    else:
        docs = db.tasks.find(
                   {"number":{ '$regex': number }}
               )
    for i in docs:
        sdata.append(i)
    session['search'] = True
    session['data'] = sdata
    if len(sdata) <= 0:
       session['message'] = 'No data found.'
    return redirect('/')

def resetTask(form):
    db.tasks.drop()
    db.settings.drop()
    db.settings.insert_one({'name':'task_id', 'value':0})
    return redirect('/')

@app.route('/', methods=['GET','POST'])
def main():
    # create form
    cform = AddContact(prefix='cform')
    dform = DeleteContact(prefix='dform')
    uform = UpdateContact(prefix='uform')
    sform = SearchContact(prefix='sform')
    reset = ResetTask(prefix='reset')

    # response
    if cform.validate_on_submit() and cform.add.data:
        session['add'] = True
        session['message'] = ''
        return addContact(cform.number.data,cform.name.data)
    if dform.validate_on_submit() and dform.delete.data:
        session['delete'] = True
        session['message'] = ''
        return deleteContact(dform.name.data)
    if uform.validate_on_submit() and uform.update.data:
        session['update'] = True
        session['message'] = ''
        return updateContact(uform.number.data,uform.name.data)
    if sform.validate_on_submit() and sform.search.data:
        session['search'] = False
        session['message'] = ''
        return searchContact(sform)
    if reset.validate_on_submit() and reset.reset.data:
        return resetTask(reset)

    # read all data
    data = []
    if(session['search']):
        data = session['data']
        session['search'] = False
        session['data'] = ''
    else:
        docs = db.tasks.find()
        data = []
        for i in docs:
             data.append(i)
    
    if data:
        search = True

    return render_template('home.html', cform = cform, dform = dform, uform = uform, \
            sform = sform, data = data, reset = reset, message=session['message'])

if __name__=='__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
