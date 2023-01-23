from flask import Flask #Codigo para importar y poder trabajar con todo el framework de flask
from flask import render_template,request,redirect,flash #Nos permitira mostrar los templates
from flaskext.mysql import MySQL #Nos permite conectarnos a la base de datos Mysql
from datetime import datetime
import os #Modulo del sistema operativo que nos permitira entrar en la carpeta uploads para borrar el archivo
from flask import send_from_directory #Modulo para mostrar elementos de un directorio

app = Flask(__name__,template_folder='views') #Creamos una primera aplicacion
#Creacion de llave secreta para el manejo de mensajes creados en flash
app.secret_key = "Develoteca"
'''Declaramos el uso de mysql pasandole las instruccion del host,user,password(no es necesario) y nombre de la base 
de datos'''

mysql = MySQL() 
app.config['MYSQL_DATABASE_HOST'] = 'localhost' #Para conectarse a la base de datos mysql se utilizara el host localhost
app.config['MYSQL_DATABASE_USER'] = 'root' 
app.config['MYSQL_DATABASE_PASSWORD'] = '' 
app.config['MYSQL_DATABASE_DB'] = 'sistema'
mysql.init_app(app) #Crear la conexion con los datos almacenados en app

CARPETA = os.path.join('uploads') 
app.config['CARPETA'] = CARPETA #Creamos una referencia para guardar la ruta de la carpeta uploads


@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto) 


@app.route('/') #Rutiamos la aplicacion
def index():
    #Insercion de datos en la base de datos
    sql = "SELECT * FROM `empleados`;"
    conn = mysql.connect() #Conectarse a la base de datos
    cursor = conn.cursor() #Almacenar Informacion
    cursor.execute(sql) #Ejecutar Sentencia

    empleados = cursor.fetchall() #Obtener todos los datos de la sentencia
    print(empleados)

    conn.commit() #Finalizar la sentencia

    return render_template('empleados/index.html',empleados = empleados)

@app.route('/create')
def create():
    
    return render_template('empleados/create.html')

@app.route('/store', methods=['POST']) #La informacion llegara a traves del metodo post a /store
def storage():
    nombre = request.form['txtNombre']
    correo = request.form['txtCorreo']
    foto = request.files['txtFoto']

    if nombre == "" or correo == "" or foto == "":
        flash("Recuerda llenar los datos de los campos")
        return redirect("/create")

    now = datetime.now() #Tomando el tiempo actual
    tiempo = now.strftime("%Y%H%M%S") #Transformando a un formato de años,horas,mes y segundos

    if foto.filename != " ":
        nuevoNombreFoto = tiempo + foto.filename
        foto.save("uploads/"+nuevoNombreFoto) 


    sql = "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s);"

    datos = (nombre,correo,nuevoNombreFoto) # De la foto solo voy a tomar su nombre de archivo
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()
    return redirect("/")
    
@app.route('/destroy/<int:id>')
def destroy(id):

    sql = f"DELETE FROM `empleados` WHERE id = {id} ;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(f"SELECT foto FROM empleados WHERE id = {id}")
    fila = cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
    cursor.execute(sql)
    conn.commit()
    return redirect("/")

    
@app.route('/edit/<int:id>')
def edit(id):

    sql = f"SELECT * FROM `empleados` WHERE id = {id} ;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    datos = cursor.fetchall()
    conn.commit() 
    return render_template("empleados/edit.html",datos = datos)
    
@app.route('/update', methods=['POST'])
def update():
    nombre = request.form['txtNombre']
    correo = request.form['txtCorreo']
    foto = request.files['txtFoto']
    id = request.form['txtId']

    sql = "UPDATE `empleados` SET nombre = %s , correo = %s WHERE id = %s;"

    datos = (nombre,correo,id)
    conn = mysql.connect()
    cursor = conn.cursor()

    now = datetime.now() #Tomando el tiempo actual
    tiempo = now.strftime("%Y%H%M%S") #Transformando a un formato de años,horas,mes y segundos
 
    if foto.filename != " ":

        nuevoNombreFoto = tiempo + foto.filename
        foto.save("uploads/"+nuevoNombreFoto) 

        cursor.execute(f"SELECT foto FROM empleados WHERE id = {id}")
        fila = cursor.fetchall()

        os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
        cursor.execute("UPDATE empleados SET foto = %s WHERE id = %s",(nuevoNombreFoto,id))
        conn.commit()
        
    cursor.execute(sql,datos)
    conn.commit()

    return redirect('/')

if __name__ == '__main__': # Correra la aplicacion
    app.run(debug=True)