# import json
# import os

# from app.core.custom_exceptions import ObjectAlreadyExistsException
# from app.core.dependencies.database_dependency import db_session_dependency
# from app.locations.repositories.district_repository import DistrictRepository
# from app.locations.repositories.facility_contact_repository import FacilityContactRepository
# from app.locations.repositories.facility_repository import FacilityRepository
# from app.locations.repositories.region_repository import RegionRepository
# from app.locations.schemas.request.district import CreateDistrictSchema

# db_session_generator = db_session_dependency()
# db_session = next(db_session_generator)  # type: ignore

# region_repository = RegionRepository(db_session=db_session)
# district_repository = DistrictRepository(db_session=db_session)
# facility_repository = FacilityRepository(db_session=db_session)
# facility_contact_repository = FacilityContactRepository(db_session=db_session)


# def create_regions(*, file_path: str) -> None:
#     """Create default regions data from regions file

#     Args:
#         file_path (str): The path to the regions json file.
#     """
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"Regions json file not found: {file_path}")

#     print("-------------------------CREATING REGIONS-------------------------")
#     with open(file_path, mode="r", encoding="utf-8") as regions_file:
#         try:
#             regions_data: list[dict] = json.load(regions_file)

#             for number, region in enumerate(regions_data, start=1):
#                 try:
#                     new_region = region_repository.create(data=region)
#                     print(f"{number}. Region {new_region.name} created.")
#                 except ObjectAlreadyExistsException:
#                     print(f"Region {region['name']} already exists.")

#             print("DONE")

#         except Exception as e:
#             print(f"Error creating regions: {str(e)}")


# def create_districts(*, file_path: str) -> None:
#     """Create default districts data from districts file

#     Args:
#         file_path (str): The path to the districts json file.
#     """
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"Districts json file not found: {file_path}")

#     print("-------------------------CREATING DISTRICTS-------------------------")
#     with open(file_path, mode="r", encoding="utf-8") as districts_file:
#         try:
#             districts_data: list[dict] = json.load(districts_file)

#             for number, district in enumerate(districts_data, start=1):
#                 try:
#                     district_region = region_repository.get_by_field(
#                         field_name="name", value=district["region"], operator="eq"
#                     )
#                     district_data = CreateDistrictSchema(name=district["name"], region_id=str(district_region.id))
# # type: ignore
#                     new_district = district_repository.create(data=district_data.model_dump())
#                     print(f"{number}. District {new_district.name} created.")
#                 except ObjectAlreadyExistsException:
#                     print(f"District {district['name']} already exists.")

#             print("DONE")

#         except Exception as e:
#             print(f"Error creating districts: {str(e)}")


# def create_facilities_facilities_contacts(*, file_path: str) -> None:
#     """Create default facilities and facility contacts data from facilities file

#     Args:
#         file_path (str): The path to the facilities json file.
#     """
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"Facilities json file not found: {file_path}")

#     print("-------------------------CREATING FACILITIES AND FACILITY CONTACTS-------------------------")
#     with open(file_path, mode="r", encoding="utf-8") as facilities_file:
#         try:
#             facilities_data: list[dict] = json.load(facilities_file)

#             for number, facility in enumerate(facilities_data, start=1):
#                 try:
#                     district = district_repository.get_by_field(
#                         field_name="name", value=facility["district"], operator="eq"
#                     )
#                     if district is None:
#                         continue
#                     facility_data = {
#                         "name": facility["name"],
#                         "district_id": str(district.id),  # type: ignore
#                         "facility_type": facility["type"],
#                         "ownership": facility["ownership"],
#                         "registration_number": facility.get("registration_number"),
#                         "is_approved": facility.get("is_approved", False),
#                     }
#                     new_facility = facility_repository.create(data=facility_data)
#                     print(f"{number}. Facility {new_facility.name} created.")

#                     # Create facility contacts
#                     phone_numbers = []
#                     if facility.get("phone"):
#                         raw_phone = str(facility["phone"]).strip()
#                         if "/" in raw_phone:
#                             # Split multiple phone numbers
#                             phone_numbers = [phone.strip() for phone in raw_phone.split("/") if phone.strip()]
#                         else:
#                             phone_numbers = [raw_phone]

#                     # Prefix each phone number with 233 and validate
#                     processed_phone_numbers = []
#                     for phone in phone_numbers:
#                         if phone.startswith("0"):
#                             phone = phone[1:]  # Remove leading 0
#                         processed_phone = f"233{phone}"
#                         # Basic validation - should be 12 digits after 233
#                         if len(processed_phone) == 12 and processed_phone.isdigit():
#                             processed_phone_numbers.append(processed_phone)

#                     for phone_number in processed_phone_numbers:
#                         contact_data = {
#                             "facility_id": str(new_facility.id),
#                             "contact_number": phone_number,
#                         }
#                         facility_contact_repository.create(data=contact_data)
#                         print(f"  - Contact: {phone_number}")
#                 except ObjectAlreadyExistsException:
#                     print(f"Facility {facility['name']} already exists.")
#             print("DONE")
#         except Exception as e:
#             print(f"Error creating facilities: {str(e)}")


# if __name__ == "__main__":
#     # locations_file_path = os.path.join(os.path.dirname(__file__), "facilities.json")
#     # create_locations(file_path=locations_file_path)
#     try:
#         regions_file_path = os.path.join(os.path.dirname(__file__), "regions.json")
#         districts_file_path = os.path.join(os.path.dirname(__file__), "districts.json")
#         facilities_file_path = os.path.join(os.path.dirname(__file__), "facilities.json")
#         create_regions(file_path=regions_file_path)
#         create_districts(file_path=districts_file_path)
#         create_facilities_facilities_contacts(file_path=facilities_file_path)
#     finally:
#         db_session.commit()
#         db_session.close()
#         db_session_generator.close()


import json
import os

from app.core.custom_exceptions import ObjectAlreadyExistsException
from app.database.session import SessionLocal
from app.locations.repositories.district_repository import DistrictRepository
from app.locations.repositories.facility_contact_repository import FacilityContactRepository
from app.locations.repositories.facility_repository import FacilityRepository
from app.locations.repositories.region_repository import RegionRepository
from app.locations.schemas.request.district import CreateDistrictSchema


def create_regions(region_repository: RegionRepository, file_path: str) -> None:
    """Create default regions data from regions file

    Args:
        region_repository (RegionRepository): The region repository instance.
        file_path (str): The path to the regions json file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Regions json file not found: {file_path}")

    print("-------------------------CREATING REGIONS-------------------------")

    with open(file_path, mode="r", encoding="utf-8") as file:
        regions_data = json.load(file)

        for number, region in enumerate(regions_data, start=1):
            try:
                new_region = region_repository.create(data=region)
                print(f"{number}. Region {new_region.name} created.")
            except ObjectAlreadyExistsException:
                print(f"Region {region['name']} already exists.")

    print("DONE")


def create_districts(
    region_repository: RegionRepository, district_repository: DistrictRepository, file_path: str
) -> None:
    """Create default districts data from districts file

    Args:
        region_repository (RegionRepository): The region repository instance.
        district_repository (DistrictRepository): The district repository instance.
        file_path (str): The path to the districts json file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Districts json file not found: {file_path}")

    print("-------------------------CREATING DISTRICTS-------------------------")

    with open(file_path, mode="r", encoding="utf-8") as file:
        districts_data = json.load(file)

        for number, district in enumerate(districts_data, start=1):
            try:
                region = region_repository.get_by_field(
                    field_name="name",
                    value=district["region"],
                    operator="eq",
                )

                if not region:
                    print(f"Skipping district {district['name']} (region not found)")
                    continue

                district_data = CreateDistrictSchema(
                    name=district["name"],
                    region_id=str(region.id),  # type: ignore
                )

                new_district = district_repository.create(data=district_data.model_dump())

                print(f"{number}. District {new_district.name} created.")

            except ObjectAlreadyExistsException:
                print(f"District {district['name']} already exists.")

    print("DONE")


def create_facilities(
    district_repository: DistrictRepository,
    facility_repository: FacilityRepository,
    facility_contact_repository: FacilityContactRepository,
    file_path: str,
) -> None:
    """Create default facilities and facility contacts data from facilities file

    Args:
        district_repository (DistrictRepository): The district repository instance.
        facility_repository (FacilityRepository): The facility repository instance.
        facility_contact_repository (FacilityContactRepository): The facility contact repository instance.
        file_path (str): The path to the facilities json file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Facilities json file not found: {file_path}")

    print("-------------------------CREATING FACILITIES AND CONTACTS-------------------------")

    with open(file_path, mode="r", encoding="utf-8") as file:
        facilities_data = json.load(file)

        for number, facility in enumerate(facilities_data, start=1):
            try:
                district = district_repository.get_by_field(
                    field_name="name",
                    value=facility["district"],
                    operator="eq",
                )

                if not district:
                    print(f"Skipping facility {facility['name']} (district not found)")
                    continue

                facility_data = {
                    "name": facility["name"],
                    "district_id": str(district.id),  # type: ignore
                    "facility_type": facility["type"],
                    "ownership": facility["ownership"],
                    "registration_number": facility.get("registration_number"),
                    "is_approved": facility.get("is_approved", False),
                }

                new_facility = facility_repository.create(data=facility_data)
                print(f"{number}. Facility {new_facility.name} created.")

                # Process phone numbers
                raw_phone = str(facility.get("phone", "")).strip()
                phone_numbers = []

                if "/" in raw_phone:
                    phone_numbers = [p.strip() for p in raw_phone.split("/") if p.strip()]
                elif raw_phone:
                    phone_numbers = [raw_phone]

                for phone in phone_numbers:
                    if phone.startswith("0"):
                        phone = phone[1:]

                    processed_phone = f"233{phone}"

                    if len(processed_phone) == 12 and processed_phone.isdigit():
                        facility_contact_repository.create(
                            data={
                                "facility_id": str(new_facility.id),
                                "contact_number": processed_phone,
                            }
                        )
                        print(f"  - Contact: {processed_phone}")

            except ObjectAlreadyExistsException:
                print(f"Facility {facility['name']} already exists.")

    print("DONE")


if __name__ == "__main__":
    db_session = SessionLocal()

    try:
        region_repo = RegionRepository(db_session=db_session)
        district_repo = DistrictRepository(db_session=db_session)
        facility_repo = FacilityRepository(db_session=db_session)
        facility_contact_repo = FacilityContactRepository(db_session=db_session)

        base_path = os.path.dirname(__file__)

        # ✅ Step-by-step commits (VERY IMPORTANT)
        create_regions(region_repo, os.path.join(base_path, "regions.json"))
        db_session.commit()

        create_districts(region_repo, district_repo, os.path.join(base_path, "districts.json"))
        db_session.commit()

        create_facilities(
            district_repo,
            facility_repo,
            facility_contact_repo,
            os.path.join(base_path, "facilities.json"),
        )
        db_session.commit()

    except Exception as e:
        db_session.rollback()
        print("ERROR:", str(e))

    finally:
        db_session.close()
