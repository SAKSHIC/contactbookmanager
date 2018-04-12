# CRUD APIs for a contact book app

This is a example of Python Flask's usage as a "Contact Book Manager" using MongoDB as Database Management System. We are using PyMongo as database connector.

Few examples for CRUD using REST API -

curl -i -H "Content-Type: application/json" -X POST -d '{"number":"9090909090","name":"Sashi"}' http://contactbookmanager.herokuapp.com/api/contacts

curl -i -H "Content-Type: application/json" -X PUT -d '{"number":"9090909090","name":"Xue"}' http://contactbookmanager.herokuapp.com/api/contacts

curl -i -H "Content-Type: application/json" -X DELETE -d '{"name":"Xue"}' http://contactbookmanager.herokuapp.com/api/contacts
