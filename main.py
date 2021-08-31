from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_gravatar import Gravatar
from functools import wraps
from sqlalchemy import Table, Column, Integer, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from flask_gravatar import Gravatar
import smtplib
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from forms import New_Employee_Form, New_Project_Form, New_Allocation_Form, Find_Allocation, Find_Details


app = Flask(__name__)
app.config['SECRET_KEY'] = 'MyNameIsUmangJain'
bootstrap = Bootstrap(app)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///allocations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##Table-1 --> Employee Details Table Configuration
class Employee(db.Model):
    __tablename__ = "employees"
    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(100), nullable= False)
    employee_id= db.Column(db.String(100), unique=True, nullable=False)
    employee_type= db.Column(db.String, nullable=False)
    email= db.Column(db.String(100), nullable=False, unique= True)
    skype= db.Column(db.String(20), nullable=False, unique= True)
    allocations = relationship("Allocation", back_populates="employee")


##Table-2 --> Project Details Table Configuration
class Project(db.Model):
    __tablename__ = "projects"
    pid= db.Column(db.String(100), primary_key=True)
    pname= db.Column(db.String(250), nullable=False)
    start_date= db.Column(db.DateTime, nullable=False)
    end_date= db.Column(db.DateTime(50), nullable=False)
    allocations = relationship("Allocation", back_populates="project")

class Allocation(db.Model):
    __tablename__ = "allocations"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(100), ForeignKey('projects.pid'))
    project = relationship("Project", back_populates="allocations")
    employee_id = db.Column(db.String(100), ForeignKey('employees.employee_id'))
    employee = relationship("Employee", back_populates="allocations")
    allocation_percent = db.Column(db.Float, nullable=False)

db.create_all()




@app.route('/')
def home():
    # projects = Project.query.filter(Project.start_date <= datetime.now()).filter(Project.end_date <= datetime(2021, 9, 30)).all()
    # for project in projects:
    #     print(f"{project.pname}, {project.start_date}, {project.end_date}")

    # allocation = db.session.query(Allocation.employee_id,
    #                               func.sum(Allocation.allocation_percent).label('Total_Allocations')) \
    #     .join(Project) \
    #     .group_by(Allocation.employee_id) \
    #     .filter(Allocation.employee_id == 1234) \
    #     .filter(Project.start_date <= datetime(2021, 9, 30)) \
    #     .filter(datetime(2021, 10, 1) <= Project.end_date).all()
    #
    # print(f"{allocation[0].employee_id}, {allocation[0].Total_Allocations}")
    return render_template('index.html')


@app.route('/new-employee', methods=["GET","POST"])
def new_employee():
    form = New_Employee_Form()
    if form.validate_on_submit():
        employee_id = form.employee_id.data
        employee_name = form.employee_name.data
        employee_type = form.employee_type.data
        email = form.email.data
        skype = form.skype.data

        if employee_type == "None":
            flash("Please select the employee type!")
            return redirect(url_for('new_employee'))

        #Checking for a record with same employee id
        employee = db.session.query(Employee.employee_id,
                                    Employee.name).filter(Employee.employee_id == employee_id).all()
        if len(employee) > 0:
            flash(f"Employee {employee[0].employee_id} --> {employee[0].name} already exists.")
            return redirect(url_for('new_employee'))

        # Checking for a record with same email
        employee = db.session.query(Employee.employee_id,
                                    Employee.name).filter(Employee.email == email).all()
        if len(employee) > 0:
            flash(f"Employee {employee[0].employee_id} --> {employee[0].name} with email {email} already exists.")
            return redirect(url_for('new_employee'))

        # Checking for a record with same skype
        employee = db.session.query(Employee.employee_id,
                                    Employee.name).filter(Employee.skype == skype).all()
        if len(employee) > 0:
            flash(f"Employee {employee[0].employee_id} --> {employee[0].name} with skype number {skype} already exists.")
            return redirect(url_for('new_employee'))

        else:
            new_employee = Employee(
                name=employee_name,
                employee_id=employee_id,
                employee_type=employee_type,
                email=email,
                skype=skype
            )
            db.session.add(new_employee)
            new_allocation = Allocation(
                project_id="000",
                employee_id=employee_id,
                allocation_percent=0
            )
            db.session.add(new_allocation)
            db.session.commit()



            print(f"{employee_id}, {employee_name}, {employee_type}, {email}, {skype}")
            return redirect(url_for('home'))

    return render_template('new_employee.html', form= form)


@app.route('/new-project', methods=["GET", "POST"])
def new_project():
    form = New_Project_Form()
    if form.validate_on_submit():
        project_id = form.project_id.data
        project_name = form.project_name.data
        # # sy, sm, sd = form.start_date.data.split('-')
        # start_date =  datetime.datetime(int(sy), int(sm), int(sd))
        # ey, em, ed = form.end_date.data.split('-')
        # end_date = datetime.datetime(int(ey), int(em), int(ed))
        start_date = form.start_date.data
        end_date = form.end_date.data

        new_project= Project(
            pid=project_id,
            pname=project_name,
            start_date=start_date,
            end_date=end_date
        )
        db.session.add(new_project)
        db.session.commit()

        print(f"{project_id}, {project_name}, {start_date}, {end_date}")
        return redirect(url_for('home'))

    return render_template('new_project.html', form=form)


@app.route('/new-allocation', methods=["GET", "POST"])
def new_allocation():
    form = New_Allocation_Form()
    projects = db.session.query(Project.pid,
                                Project.pname).all()
    project_list = [(project.pid, project.pname) for project in projects]
    project_list.insert(0,(None, "Select"))

    employees = db.session.query(Employee.employee_id,
                                 Employee.name).all()
    employee_list = [(employee.employee_id, employee.name) for employee in employees]
    employee_list.insert(0, (None, "Select"))

    form.project_id.choices = project_list
    form.employee_id.choices = employee_list

    if form.validate_on_submit():
        #if request.form.action == 'submit':
        if 'submit' in request.form:
            print("submit")
            project_id = form.project_id.data
            employee_id = form.employee_id.data
            alloc_percent = form.alloc_percent.data

            if project_id == None:
                flash(f"Project Id is required!")
                return redirect(url_for('new_allocation'))

            if employee_id == "None":
                flash(f"Employee Id is required!")
                return redirect(url_for('new_allocation'))

            elif not alloc_percent:
                flash(f"Allocation Percentage is required.")
                return redirect(url_for('new_allocation'))

            alloc = float(alloc_percent)
            prev_alloc = db.session.query(func.sum(Allocation.allocation_percent).label('prev')) \
                .group_by(Allocation.employee_id) \
                .filter(Allocation.employee_id == employee_id)
            if prev_alloc[0].prev + alloc >= 100:
                emp = db.session.query(Employee.name).filter(Employee.employee_id == employee_id).all()
                flash(f"Total Allocation for {emp[0].name} exceeds 100%. Please recheck the values.")
                return redirect(url_for('new_allocation'))

            new_allocation= Allocation(
                project_id=project_id,
                employee_id=employee_id,
                allocation_percent=alloc_percent
            )
            db.session.add(new_allocation)
            db.session.commit()

            print(f"{project_id}, {employee_id}, {alloc_percent}")


            return redirect(url_for('home'))

        else:
            return redirect(url_for('select_members'))

    return render_template('new_allocation.html', form=form)


@app.route('/select', methods=["GET","POST"])
def select_members():

    projects = db.session.query(Project.pid,
                                Project.pname).all()
    project_list = [(project.pid, project.pname) for project in projects]
    project_list.insert(0, (None, "Select"))

    if request.method == "POST":
        pid = request.form['project_id']
        print(f"Select pid = {pid}")
        if pid == "None":
            flash(f"Project Id cannot be empty!")
            return redirect(url_for('select_members'))

        selected_members= request.form.getlist('select_team_members')
        for member in selected_members:
            alloc = request.form[member]
            if not alloc:
                flash(f"Allocation value for id {member} cannot be empty.")
                return redirect(url_for('select_members'))
            else:
                alloc = float(alloc)
                prev_alloc = db.session.query(func.sum(Allocation.allocation_percent).label('prev'))\
                                .group_by(Allocation.employee_id)\
                                .filter(Allocation.employee_id == member)
                if prev_alloc[0].prev + alloc >= 100:
                    emp = db.session.query(Employee.name).filter(Employee.employee_id == member).all()
                    flash(f"Total Allocation for {emp[0].name} exceeds 100%. Please recheck the values.")
                    return redirect(url_for('select_members'))

                else:
                    new_allocation = Allocation(
                        project_id=pid,
                        employee_id=member,
                        allocation_percent=alloc
                    )
                    db.session.add(new_allocation)
                    db.session.commit()

        return redirect(url_for('home'))

    ##############
    all_employees = db.session.query(Employee.employee_id,
                                     Employee.name,
                                     Employee.employee_type,
                                     func.sum(Allocation.allocation_percent)
                                     .label('Total_Allocations')
                                     )\
                        .join(Allocation.employee)\
                        .group_by(Allocation.employee_id).all()

    print(all_employees)
    available_members = []
    for i in all_employees:
        if i.Total_Allocations < 100:
            available_members.append(i)

    return render_template('select.html', employees = available_members, projects = project_list)


@app.route('/find-allocation', methods=["GET", "POST"])
def find_allocation():
    form = Find_Allocation()

    employees = db.session.query(Employee.employee_id,
                                 Employee.name).all()
    employee_list = [(employee.employee_id, employee.name) for employee in employees]
    employee_list.insert(0, (None, "Select"))

    form.employee_id.choices = employee_list

    if form.validate_on_submit():
        employee_id = form.employee_id.data
        date = form.date.data

        allocation = db.session.query(Allocation.employee_id,
                                      Employee.name,
                                      func.sum(Allocation.allocation_percent).label('Total_Allocations')) \
            .join(Project).join(Employee) \
            .group_by(Allocation.employee_id) \
            .filter(Allocation.employee_id == employee_id) \
            .filter(Project.start_date <= date) \
            .filter(date <= Project.end_date).all()

        # y, m, d = str(date).split('-')
        # start_date = datetime.datetime(int(sy), int(sm), int(sd))
        #
        # print(len(allocation))
        # print(allocation)
        if len(allocation) > 0:
            flash(f"Current Allocations for {allocation[0].employee_id} --> {allocation[0].name} is {allocation[0].Total_Allocations}%")
            return redirect(url_for('find_allocation'))
        else:
            flash(f"Current Allocations is 0%")
            return redirect(url_for('find_allocation'))

    return render_template('find_allocation.html', form = form)


@app.route('/find-details', methods = ["GET", "POST"])
def find_details():
    form = Find_Details()

    employees = db.session.query(Employee.employee_id,
                                 Employee.name).all()
    employee_list = [(employee.employee_id, employee.name) for employee in employees]
    employee_list.insert(0, (None, "Select"))

    form.employee_id.choices = employee_list


    if form.validate_on_submit():
        emp_id = form.employee_id.data
        from_date = form.from_date.data
        to_date = form.to_date.data + timedelta(days=1)

        records = db.session.query(Employee.name,
                                   Employee.email,
                                   Employee.skype,
                                   Project.pid,
                                   Project.pname,
                                   Project.start_date,
                                   Project.end_date,
                                   func.sum(Allocation.allocation_percent).label('Total_Allocations'))\
                    .join(Project).join(Employee) \
                    .filter((Project.start_date >= from_date) | (Project.end_date <= to_date))\
                    .group_by(Allocation.project_id)\
                    .filter(Allocation.employee_id == emp_id)\
                    .all()

        # print(len(records))
        # for x in records:
        #     print(f"{x.name},"
        #           f"{x.email}."
        #           f"{x.skype},"
        #           f"{x.pname},"
        #           f"{x.pname},"
        #           f"{x.start_date},"
        #           f"{x.end_date},"
        #           f"{x.Total_Allocations}")

        if len(records) == 0:
            flash(f"No Allocations to Show!")
            return render_template('employee_records.html', isForm=True, form = form)

        return render_template('employee_records.html', isForm=False, records=records, n=len(records))


    return render_template('employee_records.html', isForm=True, form = form)



if __name__ == "__main__":
    app.run(debug=True)