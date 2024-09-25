from fastapi import APIRouter, HTTPException
from sqlalchemy import func, and_
from db.connection import db_dependency
from db.VerifyToken import user_dependency
from models.userModels import Hospital, Doctor, Nurse, Appointments, Records,Users                                                                                                                      
router = APIRouter(prefix="/sum", tags=["Totals"])

@router.get(
    "/hospital/",
    description="Get all hospital counts for various entities",
)
async def get_all_hospitals_total_counts(
    user: user_dependency,
    db: db_dependency
):
    if isinstance(user, HTTPException):
        raise user

    if user["acc_type"] not in ["hospital"]:
        raise HTTPException(status_code=403, detail="You are not allowed to perform this action")

    hospital = db.query(Hospital).filter(Hospital.OwnerId == user["user_id"]).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    # Counting entities
    doctor_count = db.query(func.count(Doctor.id)).filter(Doctor.hospitalId == hospital.id).scalar()
    nurse_count = db.query(func.count(Nurse.id)).filter(Nurse.hospitalId == hospital.id).scalar()
    appointment_count = db.query(func.count(Appointments.id)).filter(Appointments.hospitalId == hospital.id).scalar()
    record_count = db.query(func.count(Records.id)).filter(Records.hospitalId == hospital.id).scalar()

    return {
        "hospital_name": hospital.hospital_name,
        "doctor_count": doctor_count,
        "nurse_count": nurse_count,
        "appointment_count": appointment_count,
        "record_count": record_count
    }
@router.get(
    "/doctor",
    description="Get all totals for the doctor including appointments and records.",
)
async def get_doctor_totals(
    user:user_dependency,
    db: db_dependency
):
    if isinstance(user, HTTPException):
        raise user

    if user["acc_type"] not in ["doctor"]:
        raise HTTPException(status_code=403, detail="You are not allowed to perform this action")

    doctor = db.query(Doctor).filter(Doctor.OwnerId == user["user_id"]).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Total appointments received
    total_appointments = db.query(func.count(Appointments.id)).filter(Appointments.Doctor_id == doctor.id).scalar()
    
    # Total pending appointments
    pending_appointments = db.query(func.count(Appointments.id)).filter(
        and_(Appointments.Doctor_id == doctor.id, Appointments.app_status == False)
    ).scalar()

    # Total completed appointments
    completed_appointments = db.query(func.count(Appointments.id)).filter(
        and_(Appointments.Doctor_id == doctor.id, Appointments.app_status == True)
    ).scalar()

    # Total records created
    total_records = db.query(func.count(Records.id)).filter(Records.Doctor_id == doctor.id).scalar()

    # Total patients attended (distinct count based on patient IDs in appointments)
    total_patients = db.query(func.count(func.distinct(Appointments.OwnerId))).filter(Appointments.Doctor_id == doctor.id).scalar()

    return {
        "total_appointments": total_appointments,
        "pending_appointments": pending_appointments,
        "completed_appointments": completed_appointments,
        "total_records": total_records,
        "total_patients": total_patients
    }

@router.get(
    "/admin",
    description="Get all totals for admin including users, hospitals, doctors, nurses, appointments, and records.",
)
async def get_admin_totals(db: db_dependency, user:user_dependency):
    if isinstance(user, HTTPException):
        raise user

    if not user or "user_id" not in user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if user["acc_type"] not in ["admin"]:
        raise HTTPException(status_code=403, detail="You are not allowed to perform this action")

    # Total users count
    total_users = db.query(func.count(Users.id)).scalar()

    # Total hospitals count
    total_hospitals = db.query(func.count(Hospital.id)).scalar()

    # Total doctors count
    total_doctors = db.query(func.count(Doctor.id)).scalar()

    # Total nurses count
    total_nurses = db.query(func.count(Nurse.id)).scalar()

    # Total appointments count
    total_appointments = db.query(func.count(Appointments.id)).scalar()

    # Total records count
    total_records = db.query(func.count(Records.id)).scalar()

    # Hospital-wise counts including doctors and records
    hospital_data = (
        db.query(
            Hospital.hospital_name,
            Hospital.hospital_address,
            func.count(Doctor.id).label("doctor_count"),
            func.count(Records.id).label("record_count"),
            func.count(Appointments.id).label("appointment_count")
        )
        .outerjoin(Doctor, Doctor.hospitalId == Hospital.id)
        .outerjoin(Records, Records.hospitalId == Hospital.id)
        .outerjoin(Appointments, Appointments.hospitalId == Hospital.id)
        .group_by(Hospital.id)
        .all()
    )

    detailed_hospital_data = [
        {
            # "hospital_name": data.hospital_name,
            # "hospital_address": data.hospital_address,
            "doctor_count": data.doctor_count,
            "record_count": data.record_count,
            "appointment_count": data.appointment_count,
        }
        for data in hospital_data
    ]

    return {
        "total_users": total_users,
        "total_hospitals": total_hospitals,
        "total_doctors": total_doctors,
        "total_nurses": total_nurses,
        "total_appointments": total_appointments,
        "total_records": total_records,
        "hospital_data": detailed_hospital_data
    }