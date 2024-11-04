import psycopg2
from pywebio import start_server
from pywebio.input import input_group, input, PASSWORD, select, textarea, file_upload
from pywebio.output import put_text, put_success, put_error, put_markdown, put_button, clear, put_table
from pywebio.session import go_app, hold
from datetime import datetime

# Database connection settings
DB_SETTINGS = {
    'dbname': 'MaintenanceRequestSystem',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': 5432
}
is_table_visible=False;
# Function to establish database connection
def get_db_connection():
    return psycopg2.connect(**DB_SETTINGS)

# Function for manager to assign a request to a staff member
def assign_request_to_staff():
    global is_table_visible
    clear()  # Clear previous output
    is_table_visible = False  # Reset table visibility

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get unassigned requests and staff list
        cursor.execute("SELECT request_id, description FROM Request where staff_id is NULL")
        requests = cursor.fetchall()
        cursor.execute("SELECT staff_id, name FROM maintenance")
        staff = cursor.fetchall()

        # Check if there are any unassigned requests and available staff
        if not requests:
            put_text("No unassigned requests.")
            return
        if not staff:
            put_text("No staff available.")
            return

        # Display form for assigning request
        assign_data = input_group("Assign Request to Staff", [
            select("Request", name="request_id", options=[(f"Request {req[0]}: {req[1]}", req[0]) for req in requests]),
            select("Staff", name="staff_id", options=[(f"{s[1]} (ID: {s[0]})", s[0]) for s in staff])
        ])

        # Update request with assigned staff ID
        update_query = "UPDATE Request SET staff_id = %s WHERE request_id = %s"
        cursor.execute(update_query, (assign_data["staff_id"], assign_data["request_id"]))
        conn.commit()
        put_success("Request assigned to staff successfully!")
    except Exception as e:
        put_error(f"Failed to assign request: {e}")
    finally:
        cursor.close()
        conn.close()


def check_staff_credentials(email, password):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT password FROM maintenance WHERE email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        return result and result[0] == password
    except Exception as e:
        print(f"Error checking credentials: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Function for staff to view their assigned requests


# Function for staff to view and update their assigned requests

def staff_dashboard(email):
    clear()  # Clear previous output

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch staff ID based on email
        cursor.execute("SELECT staff_id FROM maintenance WHERE email = %s", (email,))
        staff_id = cursor.fetchone()[0]

        # Input group for filtering options
        filter_options = input_group("Filter Maintenance Requests", [
            input("Apartment Number", name="apt_no", type="text", placeholder="Enter apartment number (optional)", required=False),
            select("Area of the Problem", name="area", options=["All", "Kitchen", "Bathroom", "Living Room", "Bedroom", "Other"], value="All"),
            input("Start Date", name="start_date", type="date", required=False),
            input("End Date", name="end_date", type="date", required=False),
            select("Status", name="status", options=["All", "pending", "completed"], value="All")
        ])

        # Function to retrieve filtered requests
        def get_filtered_requests():
            # Build query dynamically based on selected filters
            query = "SELECT request_id, apt_no, area, description, request_time, status FROM request WHERE staff_id = %s"
            params = [staff_id]

            if filter_options["apt_no"]:
                query += " AND apt_no = %s"
                params.append(filter_options["apt_no"])
            if filter_options["area"] != "All":
                query += " AND area = %s"
                params.append(filter_options["area"])
            if filter_options["status"] != "All":
                query += " AND status = %s"
                params.append(filter_options["status"])
            if filter_options["start_date"]:
                query += " AND request_time >= %s"
                params.append(filter_options["start_date"])
            if filter_options["end_date"]:
                query += " AND request_time <= %s"
                params.append(filter_options["end_date"])

            cursor.execute(query, tuple(params))
            return cursor.fetchall()

        # Function to display requests and provide status update interface
        def display_requests(requests):
            if requests:
                # Display request details in a table format
                table_data = [["Request ID", "Apartment No", "Area", "Description", "Request Time", "Current Status"]]
                for req in requests:
                    request_id, apt_no, area, description, request_time, status = req
                    table_data.append([request_id, apt_no, area, description, request_time, status])
                put_table(table_data)

                # Create dropdown inputs for updating statuses
                update_status_inputs = [
                    select(f"Update status for Request {req[0]}", options=["pending", "completed"], value=req[5], name=f"status_{req[0]}")
                    for req in requests if req[5] == "pending"  # Only show for 'pending' requests
                ]

                if update_status_inputs:
                    # Collect updated statuses and apply updates
                    updated_statuses = input_group("Update Request Statuses", update_status_inputs)
                    for name, new_status in updated_statuses.items():
                        if name.startswith("status_"):
                            req_id = int(name.split("_")[1])
                            update_status_in_db(req_id, new_status)
                    put_success("Statuses updated successfully!")

                    # Refresh table to show latest data after update
                    clear()
                    updated_requests = get_filtered_requests()
                    display_requests(updated_requests)
                else:
                    put_text("No pending requests to update.")
            else:
                put_text("No maintenance requests found for the selected filters.")

        # Initial display of filtered requests
        requests = get_filtered_requests()
        display_requests(requests)

    except Exception as e:
        put_error(f"Error fetching maintenance requests: {e}")
    finally:
        cursor.close()
        conn.close()

# Function to update request status in database
def update_status_in_db(request_id, status):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        update_query = "UPDATE request SET status = %s WHERE request_id = %s"
        cursor.execute(update_query, (status, request_id))
        conn.commit()
    except Exception as e:
        print(f"Failed to update request status for ID {request_id}: {e}")
    finally:
        cursor.close()
        conn.close()


# Function to update the status of a request in the database
def update_status_in_db(request_id, status):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        update_query = "UPDATE request SET status = %s WHERE request_id = %s"
        cursor.execute(update_query, (status, request_id))
        conn.commit()
    except Exception as e:
        print(f"Failed to update request status: {e}")
    finally:
        cursor.close()
        conn.close()


# Function to check manager credentials
def check_manager_credentials(email, password):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT password FROM Manager WHERE email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        return result and result[0] == password
    except Exception as e:
        print(f"Error checking credentials: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Function to add tenant, ensuring the apartment is unoccupied
def add_tenant(tenant_data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if apartment is already assigned
        check_query = "SELECT tenant_id FROM Tenant WHERE apt_no = %s AND checkout IS NULL"
        cursor.execute(check_query, (tenant_data['apt_no'],))
        existing_tenant = cursor.fetchone()
        
        if existing_tenant:
            put_error("The apartment is already assigned to another tenant. Please choose a different apartment.")
            return

        # Insert the new tenant if apartment is unoccupied
        insert_query = """
        INSERT INTO Tenant (name, phone_number, email, checkin, apt_no, password)
        VALUES (%s, %s, %s, %s, %s, NULL)
        """
        cursor.execute(insert_query, (
            tenant_data['name'], tenant_data['phone'], tenant_data['email'], 
            tenant_data['checkin'], tenant_data['apt_no']
        ))
        conn.commit()
        put_success("Tenant added successfully!")
    except Exception as e:
        put_error(f"Failed to add tenant: {e}")
    finally:
        cursor.close()
        conn.close()

# Function to display tenant form for manager to add tenant details
def display_add_tenant_form():
    tenant_data = input_group("Add Tenant", [
        input("Name", name="name", type="text", placeholder="Enter tenant name"),
        input("Phone Number", name="phone", type="text", placeholder="Enter tenant phone number"),
        input("Email", name="email", type="text", placeholder="Enter tenant email"),
        input("Check-in Date", name="checkin", type="date", placeholder="Enter check-in date"),
        input("Apartment Number", name="apt_no", type="text", placeholder="Enter apartment number")
    ])
    add_tenant(tenant_data)

# Function to move tenant to a different apartment
def move_tenant(tenant_id, new_apt_no):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the new apartment is already occupied
        check_query = "SELECT tenant_id FROM Tenant WHERE apt_no = %s AND checkout IS NULL"
        cursor.execute(check_query, (new_apt_no,))
        existing_tenant = cursor.fetchone()
        
        if existing_tenant:
            put_error("The apartment is already occupied. Please choose a different apartment.")
            return

        # Update tenant's apartment number
        update_query = "UPDATE Tenant SET apt_no = %s WHERE tenant_id = %s"
        cursor.execute(update_query, (new_apt_no, tenant_id))
        conn.commit()
        put_success("Tenant moved successfully!")
    except Exception as e:
        put_error(f"Failed to move tenant: {e}")
    finally:
        cursor.close()
        conn.close()

# Function to delete a tenant
def delete_tenant(tenant_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        delete_query = "DELETE FROM Tenant WHERE tenant_id = %s"
        cursor.execute(delete_query, (tenant_id,))
        conn.commit()
        put_success("Tenant deleted successfully!")
    except Exception as e:
        put_error(f"Failed to delete tenant: {e}")
    finally:
        cursor.close()
        conn.close()

# Function to view all tenant details
def view_tenant_details():
    global is_table_visible
    if not is_table_visible:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "SELECT tenant_id, name, phone_number, checkin, checkout, apt_no FROM Tenant ORDER BY tenant_id"
            cursor.execute(query)
            tenants = cursor.fetchall()

            if tenants:
                table_data = [["Tenant ID", "Name", "Phone Number", "Check-in Date", "Check-out Date", "Apartment No"]]
                for tenant in tenants:
                    table_data.append([tenant[0], tenant[1], tenant[2], tenant[3], tenant[4], tenant[5]])
                put_table(table_data)
                is_table_visible=True
            else:
                put_text("No tenants found.")
        except Exception as e:
            put_error(f"Error fetching tenant details: {e}")
        finally:
            cursor.close()
            conn.close()
    else:
        clear()
        is_table_visible=False
        
    

# Tenant functionalities

# Function for tenant to set password if not already set
def set_tenant_password(email):
    tenant_data = input_group("Set Your Password", [
        input("New Password", name="password", type=PASSWORD, placeholder="Enter your new password"),
    ])

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        update_query = "UPDATE Tenant SET password = %s WHERE email = %s"
        cursor.execute(update_query, (tenant_data["password"], email))
        conn.commit()
        put_success("Password set successfully! You can now log in.")
    except Exception as e:
        put_error(f"Failed to set password: {e}")
    finally:
        cursor.close()
        conn.close()

# Function for tenant login, with option to set password if not set
def tenant_login(email, password):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT password, apt_no FROM Tenant WHERE email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()

        if result is None:
            put_error("Tenant not found.")
            return
        elif result[0] is None:
            # Password is NULL, prompt tenant to set a new password
            put_text("You need to set your password.")
            set_tenant_password(email)
        elif result[0] == password:
            put_success("Login successful! Welcome, Tenant!")
            tenant_dashboard(email, result[1])  # Pass apartment number to tenant dashboard
        else:
            put_error("Incorrect password. Please try again.")
    except Exception as e:
        put_error(f"Error during login: {e}")
    finally:
        cursor.close()
        conn.close()

# Tenant Dashboard with options to submit a new request or view history
def tenant_dashboard(email, apt_no):
    put_button("Submit New Maintenance Request", onclick=lambda: submit_request_form(email, apt_no), color="primary")
    put_button("View Request History", onclick=lambda: view_request_history(email), color="secondary")

# Function to submit a new maintenance request
def submit_request_form(email, apt_no):
    request_data = input_group("Submit New Maintenance Request", [
        input("Apartment Number", name="apt_no", value=apt_no, readonly=True),
        select("Area of the Problem", name="area", options=["Kitchen", "Bathroom", "Living Room", "Bedroom", "Other"]),
        textarea("Description", name="description", placeholder="Brief description of the problem"),
        file_upload("Photo (optional)", name="photo", accept="image/*")
    ])

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO Request (tenant_id, apt_no, area, description, request_time, photo, status)
        VALUES ((SELECT tenant_ID FROM Tenant WHERE email = %s), %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            email, apt_no, request_data["area"], request_data["description"], 
            datetime.now(), request_data["photo"], "pending"
        ))
        conn.commit()
        put_success("Maintenance request submitted successfully!")
    except Exception as e:
        put_error(f"Failed to submit request: {e}")
    finally:
        cursor.close()
        conn.close()

# Function to view the tenant's request history
def view_request_history(email):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        SELECT request_id, apt_no, area, description, request_time, status
        FROM Request
        WHERE tenant_id = (SELECT tenant_ID FROM Tenant WHERE email = %s)
        ORDER BY request_time DESC
        """
        cursor.execute(query, (email,))
        requests = cursor.fetchall()

        if not requests:
            put_text("No previous maintenance requests found.")
        else:
            table_data = [["Request ID", "Apartment", "Area", "Description", "Date", "Status"]]
            for req in requests:
                table_data.append([req[0], req[1], req[2], req[3], req[4], req[5]])
            put_table(table_data)
    except Exception as e:
        put_error(f"Error fetching request history: {e}")
    finally:
        cursor.close()
        conn.close()

# Function for manager dashboard with options to add, move, delete, and view tenants
def manager_dashboard():
    put_button("Add Tenant", onclick=display_add_tenant_form, color="success")
    put_button("Move Tenant", onclick=display_move_tenant_form, color="primary")
    put_button("Delete Tenant", onclick=display_delete_tenant_form, color="danger")
    put_button("View Tenant Details", onclick=view_tenant_details, color="info")
    put_button("Assign Request to Staff", onclick=assign_request_to_staff, color="warning")

# Function to display form for moving a tenant
def display_move_tenant_form():
    move_data = input_group("Move Tenant", [
        input("Tenant ID", name="tenant_id", type="number", placeholder="Enter tenant ID"),
        input("New Apartment Number", name="new_apt_no", type="text", placeholder="Enter new apartment number"),
    ])
    move_tenant(move_data['tenant_id'], move_data['new_apt_no'])

# Function to display form for deleting a tenant
def display_delete_tenant_form():
    delete_data = input("Enter Tenant ID to delete", type="number", placeholder="Tenant ID")
    delete_tenant(delete_data)

# Main login function
def login():
    put_markdown("# Maintenance Management System Login")

    # Input form to collect login credentials and role
    login_data = input_group("Login", [
        input("Email", name="email", type="text", placeholder="Enter your email"),
        input("Password", name="password", type=PASSWORD, placeholder="Enter your password"),
        select("User Type", name="role", options=["Manager", "Tenant", "Staff"])
    ])

    email = login_data["email"]
    password = login_data["password"]
    role = login_data["role"]

    # Validate credentials based on selected role
    if role == "Manager" and check_manager_credentials(email, password):
        put_success("Welcome, Manager!")
        manager_dashboard()  # Redirect to the manager dashboard
    elif role == "Staff" and check_staff_credentials(email, password):
        put_success("Welcome, Staff!")
        staff_dashboard(email)  # Redirect to the staff dashboard with email as parameter
    elif role == "Tenant":
        tenant_login(email, password)  # Redirect to tenant login handling
    else:
        put_error("Invalid credentials. Please try again.")
if __name__ == "__main__":
    start_server(login, port=8080)
