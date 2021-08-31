from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Required
from wtforms.fields.html5 import DateField
import email_validator
from flask_ckeditor import CKEditorField

class New_Employee_Form(FlaskForm):
    employee_name= StringField("Employee Name", validators=[DataRequired(message="This is required")])
    employee_id= StringField("Employee Id", validators=[DataRequired()])
    employee_type= SelectField("Employee Type", validators=[DataRequired()],
                               choices=[(None,"Select"),
                                        ('FTE',"Full Time Employee"),
                                        ('Contractor', 'Contractor'),
                                        ('Intern', 'Intern')])
    email= StringField("Email Email Id", validators=[DataRequired(), Email()])
    skype= StringField("Skype Calling Number", validators=[DataRequired()])
    submit = SubmitField("Add")


class New_Project_Form(FlaskForm):
    project_id = StringField("Project Id", validators=[DataRequired()])
    project_name= StringField("Project Name", validators=[DataRequired()])
    start_date = DateField("Project Start Date", format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField("Project End Date", format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField("Add")

class New_Allocation_Form(FlaskForm):
    # project_id = StringField("Project Id", validators=[DataRequired()])
    project_id = SelectField("Project Id",  validators=[DataRequired()])
    # employee_id = StringField("Employee Id")
    employee_id = SelectField("Employee Id")
    alloc_percent = StringField("Allocation percentage")
    submit = SubmitField("Add")
    select = SubmitField("Choose from List")



class Find_Allocation(FlaskForm):
    # employee_id = StringField("Employee Id", validators=[DataRequired()])
    employee_id = SelectField("Employee Id", validators=[DataRequired()])
    date = DateField("On Date", format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField("Find allocation.")


class Find_Details(FlaskForm):
    # employee_id = StringField("Employee Id", validators=[DataRequired()])
    employee_id = SelectField("Employee Id", validators=[DataRequired()])
    from_date = DateField("From Date", format='%Y-%m-%d', validators=[DataRequired()])
    to_date = DateField("To Date", format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField("Find Details.")
