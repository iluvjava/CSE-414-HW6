from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime

import Scheduler


def CreateLoginTestPatientUser():
    Scheduler.CURRENT_PATIENT = None
    Scheduler.CURRENT_CAREGIVER = None
    Scheduler.create_patient(["", "test", "test"])
    Scheduler.login_patient(["", "test", "test"])

CreateLoginTestPatientUser()




