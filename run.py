from flask import Flask, render_template, redirect
from pymongo import MongoClient
from classes import *
import re

# config system
app = Flask(__name__)
app.config.update(dict(SECRET_KEY='yoursecretkey'))
client = MongoClient('localhost:27017')
db = client.TaskManager
session = {'search':False, 'data':[], 'message':''}

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

def addContact(form):
    number = form.number.data
    name = form.name.data
    task_id = db.settings.find_one()['value']
    print task_id
    
    task = {'id':task_id, 'number':number, 'name':name}

    db.tasks.insert_one(task)
    updateTaskID(1)
    return redirect('/')

def deleteContact(form):
    name = form.name.data

    db.tasks.delete_many({'name':name})

    return redirect('/')

def updateContact(form):
    key = form.number.data
    name = form.name.data
    
    db.tasks.update_one(
        {"number": key},
        {"$set":
            {"name": name}
        }
    )

    return redirect('/')

def searchContact(form):
    print "I am here"
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
    print docs
    for i in docs:
        sdata.append(i)
    session['search'] = True
    session['data'] = sdata
    session['message'] = 'No data found.'
    print sdata
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
        return addContact(cform)
    if dform.validate_on_submit() and dform.delete.data:
        return deleteContact(dform)
    if uform.validate_on_submit() and uform.update.data:
        return updateContact(uform)
    if sform.validate_on_submit() and sform.search.data:
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

    return render_template('home.html', cform = cform, dform = dform, uform = uform, \
            sform = sform, data = data, reset = reset)

if __name__=='__main__':
    app.run(debug=True)
