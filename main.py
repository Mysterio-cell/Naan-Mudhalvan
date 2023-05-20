from flask import Flask, render_template, request, redirect, url_for, flash, session
from functions import func
from constants import AUTH_ADMIN_CODES

app = Flask(__name__)
app.secret_key = 'lmao'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<role>/home')
def homeroute(role):
    if 'user' in session:
        if role == 'admin':
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
        return render_template(role+'home.html', username=session['user'])
    else:
        return redirect(url_for('loginpage', role=role))


@app.route("/<role>/new_user", methods=['POST'])
def regpt(role):
    name = request.form['rname']
    email = request.form['remail']
    password = request.form['rpassword']
    admincode = request.form['admincode']
    print(name, email, password, admincode)
    if role == 'admin' and admincode not in AUTH_ADMIN_CODES:
        return render_template('admin.html', error="Invalid Admin Code")
    if func.check_user_exists(email):
        return render_template('admin.html', error="User already exists")
    if func.add_newuser(name, email, password, role):
        session['user'] = email
        return redirect(url_for('loginpage', role=role))
    else:
        return render_template('admin.html', error="Error creating user")





@app.route("/<role>/login")
def loginpage(role):
    return render_template(role+'.html', role=role)

@app.route("/<role>/login", methods=['POST'])
def loginpost(role):
    email = request.form['email']
    password = request.form['password']
    if func.check_exists(email, password, role):
        session['user'] = email
        return redirect(url_for('homeroute', role=role))
    else:
        return render_template(role+'.html', error="Invalid Credentials")


@app.route('/adminhome')
def adminhome():
    username = 'John Doe'
    
    # Retrieve complaint details from the database
    complaints = func.get_complaint()  # Assuming you have implemented the get_complaints() function
    
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
    complaints = func.get_complaint()
   
    return render_template('agenthome.html', agent_name=agent_name, agent_id=agent_id, complaints=complaints)


@app.route('/userhome')
def usrhome():
    flash("a")
    return render_template('userhome.html', username=session.get('user'))



@app.route('/submit-complaint', methods=['POST'])
def submit_complaint():
    file = request.files['complaint_image']
    title = request.form['complaint_type']
    description = request.form['complaint_description']
    latitute = request.form['latitude']
    longitute = request.form['longitude']
    location_details = request.form['location_details']
    mail = session.get('user')
    print(title, description, latitute, longitute, location_details, mail)
    if file.filename == '':
        return redirect("/userhome")
    if file:
        filename = f"temp/{func.generate_random_string()}"
        file.save(filename)
        image_url = func.upload_file(filename)
        func.new_complaint(title, description, mail, image_url, latitute, longitute, location_details)
        flash(message="Complaint submitted successfully", category="success")
        return redirect("/userhome")
    return render_template('userhome.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
