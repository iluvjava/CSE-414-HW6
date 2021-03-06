from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime

import Scheduler

def CreateLoginTestPatientUser():
    Scheduler.logout([''])
    Scheduler.CURRENT_PATIENT = None
    Scheduler.CURRENT_CAREGIVER = None
    Scheduler.create_patient(["", "test", "test"])
    Scheduler.login_patient(["", "test", "test"])
    return None


def CreateLoginTestCaregiver():
    Scheduler.logout([''])
    Scheduler.create_caregiver(['', "test", "test"])
    Scheduler.logout([''])
    Scheduler.login_caregiver(['', "test", "test"])
    return None


def CheckAvailability():
    Scheduler.search_caregiver_schedule(['', "2222-02-22"])
    return None

def CheckAppointmentsListing():
    Scheduler.show_appointments([])
    return None


def TryToReserve():
    Scheduler.reserve([''])
    print("Expect Token Error Message")
    Scheduler.reserve(['', '', ''])
    print("Expect Error Message")
    Scheduler.reserve(['', 'p', '2222-02-22'])
    print("Expect Error Message")
    Scheduler.reserve(['', 'Pfzer', '2002-02-02'])
    print("Expect Error Message")
    Scheduler.reserve(['', 'Pfzer', '2222-02-22'])
    print("Expect no Error Message")
    return None


if __name__ == "__main__":
    CreateLoginTestPatientUser()
    CheckAvailability()
    TryToReserve()
    CheckAppointmentsListing()
    CreateLoginTestCaregiver()
    CheckAppointmentsListing()



