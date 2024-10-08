import random
from faker import Faker
from datetime import timedelta, datetime

fake = Faker('hu_HU')  # Hungarian locale

# Number of records to generate
NUM_PATIENTS = 1000
NUM_DOCTORS = 50
NUM_SERVICES = 30
NUM_EMPLOYEES = 10  # Non-doctor employees
NUM_APPOINTMENTS = 5000
NUM_FEEDBACKS = 500
NUM_REFERRALS = 200

# Keep track of IDs
patient_ids = []
doctor_ids = []
service_ids = []
employee_ids = []
appointment_ids = []

# Open the file in write mode
with open('insert_data.sql', 'w', encoding='utf-8') as file:

    # Generate Patients
    file.write("USE HealthcareAppDB;\nGO\n-- Patients\n")
    for i in range(1, NUM_PATIENTS + 1):
        first_name = fake.first_name()
        last_name = fake.last_name()
        date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=80)
        date_of_birth_str = date_of_birth.strftime('%Y-%m-%d')
        gender = random.choice(['M', 'F'])
        contact_number = fake.phone_number()
        email = fake.email()
        registration_date = fake.date_between(start_date='-1y', end_date='today')
        registration_date_str = registration_date.strftime('%Y-%m-%d')
        sql_statement = f"INSERT INTO Patients (PatientID, FirstName, LastName, DateOfBirth, Gender, ContactNumber, Email, RegistrationDate) VALUES ({i}, '{first_name}', '{last_name}', '{date_of_birth_str}', '{gender}', '{contact_number}', '{email}', '{registration_date_str}');\n"
        file.write(sql_statement)
        patient_ids.append(i)

    file.write("\n-- Doctors\n")
    # Generate Doctors
    for i in range(1, NUM_DOCTORS + 1):
        first_name = fake.first_name()
        last_name = fake.last_name()
        specialization = random.choice(['Cardiology', 'Dermatology', 'Orthopedics', 'Radiology', 'Pediatrics', 'Neurology', 'Ophthalmology', 'Gynecology', 'Endocrinology', 'Gastroenterology', 'Psychiatry', 'Oncology', 'Urology', 'Pulmonology'])
        employment_date = fake.date_between(start_date='-5y', end_date='today')
        employment_date_str = employment_date.strftime('%Y-%m-%d')
        sql_statement = f"INSERT INTO Doctors (DoctorID, FirstName, LastName, Specialization, EmploymentDate) VALUES ({i}, 'Dr. {first_name}', '{last_name}', '{specialization}', '{employment_date_str}');\n"
        file.write(sql_statement)
        doctor_ids.append(i)
        employee_ids.append(i)  # Assuming doctors are also employees

    file.write("\n-- Services\n")
    # Generate Services
    for i in range(1, NUM_SERVICES + 1):
        service_name = f"{fake.word().capitalize()} Service"
        service_category = random.choice(['Consultation', 'Cardiology', 'Dermatology', 'Radiology', 'Pediatrics', 'Neurology', 'Ophthalmology', 'Gynecology', 'Laboratory', 'Endocrinology', 'Gastroenterology', 'Psychiatry', 'Oncology', 'Urology', 'Pulmonology'])
        cost = random.randint(10000, 50000)
        sql_statement = f"INSERT INTO Services (ServiceID, ServiceName, ServiceCategory, Cost) VALUES ({i}, '{service_name}', '{service_category}', {cost});\n"
        file.write(sql_statement)
        service_ids.append(i)

    file.write("\n-- Employees\n")
    # Generate Non-doctor Employees
    for i in range(NUM_DOCTORS + 1, NUM_DOCTORS + NUM_EMPLOYEES + 1):
        first_name = fake.first_name()
        last_name = fake.last_name()
        role = random.choice(['Nurse', 'Admin', 'Technician', 'Receptionist'])
        employment_date = fake.date_between(start_date='-5y', end_date='today')
        employment_date_str = employment_date.strftime('%Y-%m-%d')
        department = random.choice(['Front Desk', 'Billing', 'Laboratory', 'Radiology'])
        sql_statement = f"INSERT INTO Employee (EmployeeID, FirstName, LastName, Role, EmploymentDate, Department) VALUES ({i}, '{first_name}', '{last_name}', '{role}', '{employment_date_str}', '{department}');\n"
        file.write(sql_statement)
        employee_ids.append(i)

    file.write("\n-- Appointments\n")
    # Generate Appointments
    for i in range(1, NUM_APPOINTMENTS + 1):
        patient_id = random.choice(patient_ids)
        doctor_id = random.choice(doctor_ids)
        service_id = random.choice(service_ids)
        appointment_datetime = fake.date_time_between(start_date='-1y', end_date='now')
        appointment_datetime_str = appointment_datetime.strftime('%Y-%m-%d %H:%M:%S')
        status = random.choices(['Scheduled', 'Completed', 'Cancelled', 'No-Show'], weights=[10, 70, 10, 10])[0]
        sql_statement = f"INSERT INTO Appointments (AppointmentID, PatientID, DoctorID, ServiceID, AppointmentDateTime, Status) VALUES ({i}, {patient_id}, {doctor_id}, {service_id}, '{appointment_datetime_str}', '{status}');\n"
        file.write(sql_statement)
        appointment_ids.append(i)

    file.write("\n-- Billing\n")
    # Generate Billing Records
    for i in range(1, NUM_APPOINTMENTS + 1):
        # Only for completed appointments
        status = random.choices(['Completed', 'Cancelled', 'No-Show'], weights=[70, 15, 15])[0]
        if status == 'Completed':
            appointment_id = i
            total_amount = random.randint(10000, 50000)
            amount_paid = total_amount  # Assuming full payment for simplicity
            payment_date = fake.date_between(start_date='-1y', end_date='today')
            payment_date_str = payment_date.strftime('%Y-%m-%d')
            payment_method = random.choice(['Cash', 'Card', 'Insurance'])
            sql_statement = f"INSERT INTO Billing (BillingID, AppointmentID, TotalAmount, AmountPaid, PaymentDate, PaymentMethod) VALUES ({i}, {appointment_id}, {total_amount}, {amount_paid}, '{payment_date_str}', '{payment_method}');\n"
            file.write(sql_statement)

    file.write("\n-- Feedback\n")
    # Generate Feedback Records
    for i in range(1, NUM_FEEDBACKS + 1):
        patient_id = random.choice(patient_ids)
        appointment_id = random.choice(appointment_ids)
        rating = random.randint(1, 5)
        comments = fake.sentence(nb_words=10).replace("'", "''")  # Escape single quotes
        feedback_date = fake.date_between(start_date='-1y', end_date='today')
        feedback_date_str = feedback_date.strftime('%Y-%m-%d')
        sql_statement = f"INSERT INTO Feedback (FeedbackID, PatientID, AppointmentID, Rating, Comments, FeedbackDate) VALUES ({i}, {patient_id}, {appointment_id}, {rating}, '{comments}', '{feedback_date_str}');\n"
        file.write(sql_statement)

    file.write("\n-- Referrals\n")
    # Generate Referrals
    for i in range(1, NUM_REFERRALS + 1):
        patient_id = random.choice(patient_ids)
        referring_physician_first_name = fake.first_name()
        referring_physician_last_name = fake.last_name()
        referring_physician = f"Dr. {referring_physician_first_name} {referring_physician_last_name}"
        referral_date = fake.date_between(start_date='-1y', end_date='today')
        referral_date_str = referral_date.strftime('%Y-%m-%d')
        notes = fake.sentence(nb_words=8).replace("'", "''")  # Escape single quotes
        sql_statement = f"INSERT INTO Referrals (ReferralID, PatientID, ReferringPhysician, ReferralDate, Notes) VALUES ({i}, {patient_id}, '{referring_physician}', '{referral_date_str}', '{notes}');\n"
        file.write(sql_statement)