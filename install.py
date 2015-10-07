# -*- coding: utf-8 -*-

from principal.utils.GestionAlumnosUtils import secret_key
import getpass
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

hosts = []

print('\nAllowed hosts\n')

host = input('Please, enter the server IP address: ')
hosts.append(host)


database = {}
attributes = {}

print('\nMySQL database properties\n')

attributes['ENGINE'] = 'django.db.backends.mysql'
attributes['NAME'] = input('a.- Write the database NAME: ')
attributes['USER'] = input('b.- Write the USER: ')
attributes['PASSWORD'] = getpass.getpass('c.- Write the PASSWORD: ')
attributes['HOST'] = input('d.- Write the HOST: ')
attributes['PORT'] = input('e.- Write the PORT: ')

menu_engine = {'1': "I have an existing database with data. Do not create a database",
               '2': "Create database structure only (with an administrator)",
               '3': "Create database structure and sample data"}

selection_db = '-1'
while True:
    print('f.- Database structure and data settings. Select an option:\n')
    options = list(menu_engine.keys())
    options.sort()
    for entry in options:
        print("    " + entry + ")", menu_engine[entry])

    selection_db = input("Option: ")
    if selection_db == '1' or selection_db == '2' or selection_db == '3':
        break
    else:
        print("Unknown Option Selected!")

database['default'] = attributes

print('\nEmail server properties\n')
email = {}

menu_email = {'1': "True", '2': "False"}
while True:
    print('a.- Select if using TLS')
    options = list(menu_email.keys())
    options.sort()
    for entry in options:
        print("    " + entry + ")", menu_email[entry])

    selection = input("Option: ")
    if selection == '1':
        email['EMAIL_USE_TLS'] = True
        break
    elif selection == '2':
        email['EMAIL_USE_TLS'] = False
        break
    else:
        print("Unknown Option Selected!")

email['EMAIL_HOST'] = input('a.- Write the HOST: ')
email['EMAIL_PORT'] = input('b.- Write the PORT: ')
email['EMAIL_HOST_USER'] = input('c.- Write the USER: ')
email['EMAIL_HOST_PASSWORD'] = getpass.getpass('d.- Write the PASSWORD: ')

f = open(str(BASE_DIR) + '/gestionalumnos/data_properties.py', 'w')
f.write('# -*- coding: utf-8 -*-\n\n')

f.write('# ALLOWED_HOSTS\n')
f.write('ALLOWED_HOSTS = ' + str(hosts) + "\n\n")

f.write('# DATABASE\n')
f.write('DATABASES = ' + str(database) + "\n\n")

f.write('# EMAIL\n')
f.write('EMAIL_USE_TLS = ' + str(email['EMAIL_USE_TLS']) + "\n")
f.write("EMAIL_HOST = '" + str(email['EMAIL_HOST']) + "'\n")
f.write('EMAIL_PORT = ' + str(email['EMAIL_PORT']) + "\n")
f.write("EMAIL_HOST_USER = '" + str(email['EMAIL_HOST_USER']) + "'\n")
f.write("EMAIL_HOST_PASSWORD = '" + str(email['EMAIL_HOST_PASSWORD']) + "'\n")

f.close()

y = open(str(BASE_DIR) + '/gestionalumnos/settings_secret.py', 'w')
y.write('# -*- coding: utf-8 -*-\n\n')
y.write("SECRET_KEY = '" + str(secret_key()) + "'\n")
y.close()

if selection_db != '1':
    # Clean migrations package.
    MIGRATIONS_FOLDER = BASE_DIR + '/principal/migrations'
    for migration_file in os.listdir(MIGRATIONS_FOLDER):
        if not migration_file == '__init__.py':
            os.remove(MIGRATIONS_FOLDER + '/' + migration_file)

    # Perform makemigrations and migrate (create database)
    os.system('python ' + BASE_DIR + '/manage.py makemigrations')
    os.system('python ' + BASE_DIR + '/manage.py migrate')

    base_command = 'python ' + BASE_DIR + '/manage.py populate_db'

    if selection_db == '2':
        # Execute populate database only with production data
        base_command += ' --production_new_db_admin'

    os.system(base_command)

print('Application configured successfully')
