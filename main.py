from flask import Flask, render_template, request, redirect, url_for, flash, session
from functions import func
from constants import AUTH_ADMIN_CODES

app = Flask(__name__)
app.secret_key = 'lmao'




@app.route('/')
def index():
    return render_template('index.html')


@app.route("/admin/new_user", methods=['POST'])
def regpt():
    name = request.form['rname']
    email = request.form['remail']
    password = request.form['rpassword']
    admincode = request.form['admincode']
    print(name, email, password, admincode)
    if admincode not in AUTH_ADMIN_CODES:
        return render_template('admin.html', error="Invalid Admin Code")
    if func.check_user_exists(email):
        return "User already exists"
    if ok := func.add_newuser(name, email, password, 'admin'):
        session['user'] = email
        return redirect(url_for('regpt', error="User Created"))
    else:
        return "Error"


@app.route("/<role>/login")
def loginpage(role):
    return render_template(f'{role}.html', role=role)


@app.route('/adminhome')
def adminhome():
    username = 'John Doe'
    complaints = [
        {
            'id': 1,
            'username': 'John Doe',
            'image_url': 'path/to/image.jpg',
            'title': 'Issue Title',
            'description': 'Issue Description',
            'progress': '50%',
            'status': 'In Progress',
            'image_after_url': 'path/to/image.jpg'
        },
        {
            'id': 2,
            'username': 'Jane Smith',
            'image_url': 'path/to/image.jpg',
            'title': 'Issue Title',
            'description': 'Issue Description',
            'progress': '100%',
            'status': 'Completed',
            'image_after_url': 'path/to/image.jpg'
        }
        # Add more complaints as needed
    ]
    partners = [
        {'id': 1, 'name': 'Partner A'},
        {'id': 2, 'name': 'Partner B'},
        {'id': 3, 'name': 'Partner C'}
        # Add more partners as needed
    ]
    return render_template('adminhome.html', username=username, complaints=complaints, partners=partners)


@app.route('/agenthome')
def agenthome():
    agent_name = 'John Doe'
    agent_id = 1234
    complaints = [
        {
            'id': 1,
            'image_url': 'https://example.com/image1.jpg',
            'location_details': '123 Main St.',
            'file_id': 'abc123',
            'title': 'Broken Street Light',
            'description': 'The street light on Main St. is broken and needs to be fixed.',
            'assigned_partner': 1234,
            'progress': 'inprogress',
            'updated_status': 'In Progress',
            'image_after_url': ''
        },
          {
            'id': 1,
            'image_url': 'https://example.com/image1.jpg',
            'location_details': '123 Main St.',
            'file_id': 'abc123',
            'title': 'Broken Street Light',
            'description': 'The street light on Main St. is broken and needs to be fixed.',
            'assigned_partner': 1234,
            'progress': 'inprogress',
            'updated_status': 'In Progress',
            'image_after_url': ''
        }
    ]
    return render_template('agenthome.html', agent_name=agent_name, agent_id=agent_id, complaints=complaints)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
