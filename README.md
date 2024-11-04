# Maintenance Request Management System

This is a web-based application for managing maintenance requests in a residential apartment complex. The system allows tenants to submit maintenance requests, staff to manage and update these requests, and managers to oversee tenant details. The application is built using Python, PostgreSQL, and PyWebIO.

### Features:
- Tenants can submit maintenance requests and view request history.
- Maintenance staff can browse and filter requests by various criteria and update the status of requests.
- Managers can add, move, and delete tenants.


## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
  - [Tenant Functionalities](#tenant-functionalities)
  - [Staff Functionalities](#staff-functionalities)
  - [Manager Functionalities](#manager-functionalities)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)



## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/maintenance-request-system.git
cd maintenance-request-system
pip install -r requirements.txt



DB_SETTINGS = {
    'dbname': 'MaintenanceRequestSystem',
    'user': 'your_postgres_user',
    'password': 'your_password',
    'host': 'localhost',
    'port': 5432
}


python app.py




### 4. Usage
**Section:** `## Usage`

Describe how each type of user can interact with the system.

``markdown
## Usage

### Tenant Functionalities
1. **Submit a Maintenance Request (FR1):**
   - Tenants can submit a request for maintenance with the following details: request ID (auto-generated), apartment number, area of the problem, description, date/time (auto-generated), optional photo, and request status (initially ‘pending’).

2. **View Maintenance Request History:**
   - Tenants can view the history of their submitted requests.

### Staff Functionalities
1. **Browse Maintenance Requests (FR2):**
   - Staff can browse all maintenance requests with filters for apartment number, area (e.g., kitchen), date range, and status.

2. **Update Request Status (FR3):**
   - Staff can change the status of a maintenance request from ‘pending’ to ‘completed’.

### Manager Functionalities
1. **Add New Tenant (FR4):**
   - Managers can add new tenants with details such as tenant ID, name, phone number, email, check-in date, and apartment number.

2. **Move Tenant (FR4):**
   - Managers can move tenants to another apartment if required.

3. **Delete Tenant (FR4):**
   - Managers can delete tenant records.


## Features

### Tenant Functionalities
- **FR1**: Submit a maintenance request with details, including automatic generation of request ID and timestamp.

### Staff Functionalities
- **FR2**: Filter maintenance requests by apartment number, area, date range, and status.
- **FR3**: Update the status of a request from 'pending' to 'completed'.

### Manager Functionalities
- **FR4**: Manage tenant records, including adding, moving, and deleting tenants.
