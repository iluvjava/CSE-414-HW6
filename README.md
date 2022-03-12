# Python Application for Vaccine Scheduler
HW6 for CSE 414 Database class at the university of Washington. 

### **Scope of The Project**
Entities from the Databases are classes in our code implementations. These classes are going to be implemented for the Database. 

1. Patients
2. Caregivers
3. Vaccines

**Expectations**

* Handle invalid inputs gracefully. E.g: Wrong commands, give user feed back. 
* After executing a command, re-route the program to display the list of commanda again. E.g: If a Patient reserves their vaccine for a date, you should update your database to refelct this information and route the patient back to the main menu afterwards. 
* Handle the database error in python and provide feedback. Use proper SQL command digest flags instead of direct putting SQL into the connection. 
* MUST use the provided Util algorithms for handing password related operations in the database.  

---
### **Part 1**

**The Database:**

* Draw the ER diagram of your design and place it under src.main.resources.design.pdf. 
* Write the create table statements for your design, create the tables on Azure, and save the code undersrc.main.resources.create.sql.

**The Entities Files:**
* Caregiver.py (Already implemented)
* Vaccine.py: Data Model for Vaccines
* Patient: Datam Models for Patients

**Database Operations:**
* create_patient \<username\> \<password\>
* login_patient \<username\> \<password\>
  * If a user is already logged in in the current session, you need to logout first before logging in again.

**Deliverable for Part I:**
* src.main.resources: 
  * design.pdf: The design of the database schema. 
  * create.sql: The create.sql statement for the tables.
* src.main.schedular.model: 
  * Caregiver.py: The data model for your caregivers. 
  * Patient.py: The data model for the users. 
  * Vaccine.py: The datamodel for the vaccines. 
  * Any other models that your created. 
* src.main.scheduler: 
  * Schedular.py: The main runner for your command-line interface. 



 