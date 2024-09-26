from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'my_secret_key'

users = {}

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="cric_score"
)


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    match_details = session.get('match_details', None)
    session.pop('match_details', None)  # Clear after use
    return render_template("index.html", match_details=match_details)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        users[username] = password

        return redirect(url_for('hello_world'))
    return render_template('register.html')


@app.route('/new_login', methods=['POST'])
def new_login():
    admin_user = "admin"
    admin_pass = "123"

    login_username = request.form.get('login_username')
    login_password = request.form.get('login_password')

    if admin_user == login_username and admin_pass == login_password:
        return redirect(url_for('admin'))

    if login_username in users and users[login_username] == login_password:

        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM match_details ORDER BY id DESC LIMIT 1")
        match_details = cursor.fetchone()
        cursor.close()

        print("Fetched match details:", match_details)

        session['match_details'] = match_details
        return redirect(url_for('score_view'))
    else:
        print("Wrong username or password")
        return redirect(url_for('hello_world'))


@app.route('/score_view')
def score_view():
    match_details = session.get('match_details', None)
    print("Match details in score view:", match_details)  # Debugging output

    session.pop('match_details', None)

    return render_template('cric_score.html', match_details=match_details)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        teamA = request.form.get('teamA')
        teamB = request.form.get('teamB')
        batsmanA = request.form.get('batsmanA')
        batsmanB = request.form.get('batsmanB')
        bowler = request.form.get('bowler')
        commentary = request.form.get('commentary')
        runs = request.form.get('runs')
        overs = request.form.get('overs')
        wickets = request.form.get('wickets')

        mycursor = mydb.cursor()
        sql = ("INSERT INTO match_details (team_a, team_b, batsman_1, "
               "batsman_2, bowler, commentry, runs, overs, wickets) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
        val = (
            teamA, teamB, batsmanA, batsmanB, bowler, commentary, runs, overs,
            wickets)
        mycursor.execute(sql, val)
        mydb.commit()
        mycursor.close()

        return redirect(url_for('admin'))

    return render_template('admin.html')


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")
