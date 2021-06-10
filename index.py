from flask import Flask, render_template, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3 as sql

app = Flask(__name__)
basicAuth = HTTPBasicAuth()
users = {
	"admin": generate_password_hash("admin"),
	"user1": generate_password_hash("user1")
}

@basicAuth.verify_password
def verify_password(username, password):
	if username in users and check_password_hash(users.get(username), password):
		return username



@app.route('/')
def index():
	return render_template('index.html')



@app.route('/add', methods = ['POST', 'GET'])
@basicAuth.login_required
def add():
	con = sql.connect("database.db")
	# Add new record
	if request.method == 'POST':
		name = request.form['name']
		points = request.form['points']
		if (name == '') or (points == ''):
			return render_template('add.html', err = 1)
		try:
			with sql.connect("database.db") as con:
				cur = con.cursor()
		
				cur.execute("INSERT INTO users (name,points) VALUES (?,?)", (name, points))
				con.commit()
				msg = "Record successfully added"
		except:
			con.rollback()
			msg = "Error in INSERT operation"
		finally:
			con.close()
			return render_template("add.html", msg = msg)
	else:
		return render_template('add.html')



@app.route('/list', methods = ['POST', 'GET'])
@basicAuth.login_required
def list():
	con = sql.connect("database.db")
	con.row_factory = sql.Row
	cur = con.cursor()
	cur.execute("select * from users")
	rows = cur.fetchall()
	# Delete feature
	if request.method == 'POST':
		try:
			user_id = request.form['delete_user']

			with sql.connect("database.db") as con:
				cur = con.cursor()
				
				cur.execute("DELETE FROM users WHERE id = " + user_id)
				cur.execute("select * from users")
				rows = cur.fetchall()
				con.commit()
				msg = "Record successfully deleted"
		except:
			con.rollback()
			msg = "Error in delete operation"
		finally:
			con.close()
			return render_template("list.html", msg = msg, rows = rows)
	# List all
	else:
		return render_template("list.html", rows = rows)



# A little experiment for a product showcase
@app.route('/grid', methods = ['POST', 'GET'])
def grid():
	set_grid = 1
	if request.method == 'POST':
		set_grid = request.form.getlist('select')[0]
	grid = [0 for x in range(int(set_grid))]
	return render_template('grid-showcase.html', grid = grid, n_grid = len(grid))


if __name__ == '__main__':
	app.run(debug = True)






