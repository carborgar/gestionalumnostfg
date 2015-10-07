# Gestión de alumnos (TFG)
Sistema de gestión de fichas y tutorías de los alumnos de la Universidad de Sevilla.

# Requisitos
0.Tener una base de datos creada (vacía) y un usuario con acceso a la misma.

1.Instalación de dependencias del sistema
```
sudo apt-get install libmysqlclient-dev python3 python3-dev python-virtualenv mysql-server mysql-client
```
3.Instalación de módulos de Python
```
virtualenv --python=/usr/bin/python3 myenv
source myenv/bin/activate
cd gestionalumnos
pip install -r requirements.txt
```
4.Configuración
```
python3 install.py
```
Seguir los pasos del instalador.


# Ejecución (Servidor de desarrollo)
```
python3 manage.py runserver
```
