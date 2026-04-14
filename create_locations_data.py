import json
import os

from app.core.custom_exceptions import ObjectAlreadyExistsException
from app.core.dependencies.database_dependency import db_session_dependency
from app.locations.repositories.district_repository import DistrictRepository
from app.locations.repositories.facility_contact_repository import FacilityContactRepository
from app.locations.repositories.facility_repository import FacilityRepository
from app.locations.repositories.region_repository import RegionRepository
from app.locations.schemas.request.district import CreateDistrictSchema

# def create_locations(*, file_path: str) -> None:
#     """Create default locations data from facilities.json.

#     Args:
#         file_path (str): The path to the facilities.json file.
#     """
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"Facilities json file not found: {file_path}")

#     region_ids = {}
#     district_ids = {}

#     print("-------------------------CREATING LOCATIONS-------------------------")
#     with open(file_path, mode="r", encoding="utf-8") as facilities_file:
#         try:
#             db_session = next(db_session_dependency())  # type: ignore

#             region_repository = RegionRepository(db_session=db_session)
#             district_repository = DistrictRepository(db_session=db_session)
#             facility_repository = FacilityRepository(db_session=db_session)
#             facility_contact_repository = FacilityContactRepository(db_session=db_session)

#             facilities_data = json.load(facilities_file)

#             print("\n")
#             print("--------------------CREATING REGIONS---------------------------")
#             unique_regions = set(facility["region"] for facility in facilities_data)
#             for number, region_name in enumerate(unique_regions, start=1):
#                 new_region_data = CreateRegionSchema(name=region_name)
#                 try:
#                     new_region = region_repository.create(data=new_region_data)
#                     print(f"{number}. Region {new_region.name} created.")
#                     region_ids[new_region.name] = str(new_region.id)
#                 except ObjectAlreadyExistsException:
#                     print(f"Region {region_name} already exists.")
#                     existing_region = region_repository.get_by_field(
#                         field_name="name", value=region_name, operator="eq"
#                     )
#                     region_ids[region_name] = str(existing_region.id)  # type: ignore

#             print("DONE")

#             print("\n")
#             print("--------------------CREATING DISTRICTS------------------------")
#             unique_districts = set((facility["region"], facility["district"]) for facility in facilities_data)
#             for number, (region_name, district_name) in enumerate(unique_districts, start=1):
#                 region_id = region_ids.get(region_name)
#                 if not region_id:
#                     print(f"Skipping district {district_name} for unknown region: {region_name}")
#                     continue
#                 if district_name is None:
#                     continue
#                 new_district_data = CreateDistrictSchema(name=district_name, region_id=region_id)
#                 try:
#                     new_district = district_repository.create(data=new_district_data)
#                     print(f"{number}. District {new_district.name} created.")
#                     district_ids[new_district.name] = str(new_district.id)
#                 except ObjectAlreadyExistsException:
#                     print(f"District {district_name} already exists.")
#                     existing_districts = district_repository.get_all(
#                         filters_without_joins=["name", "region_id"],
#                         filters={
#                             "name": {"value": district_name, "operator": "eq"},
#                             "region_id": {"value": region_id, "operator": "eq"},
#                         },
#                     )
#                     if existing_districts:
#                         district_ids[district_name] = str(existing_districts[0].id)
#                     else:
#                         print(f"Could not find existing district {district_name} in region {region_name}")
#                         continue

#             print("DONE")

#             print("\n")
#             print("-----------------CREATING FACILITIES------------------------")
#             for number, facility in enumerate(facilities_data, start=1):
#                 district_id = district_ids.get(facility["district"])
#                 if not district_id:
#                     print(f"Skipping facility {facility['name']} for unknown district: {facility['district']}")
#                     continue

#                 # Process phone numbers
#                 phone_numbers = []
#                 if facility.get("phone"):
#                     raw_phone = str(facility["phone"]).strip()
#                     if "/" in raw_phone:
#                         # Split multiple phone numbers
#                         phone_numbers = [phone.strip() for phone in raw_phone.split("/") if phone.strip()]
#                     else:
#                         phone_numbers = [raw_phone]

#                 # Prefix each phone number with 233 and validate
#                 processed_phone_numbers = []
#                 for phone in phone_numbers:
#                     if phone.startswith("0"):
#                         phone = phone[1:]  # Remove leading 0
#                     processed_phone = f"233{phone}"
#                     # Basic validation - should be 12 digits after 233
#                     if len(processed_phone) == 12 and processed_phone.isdigit():
#                         processed_phone_numbers.append(processed_phone)

#                 if not processed_phone_numbers:
#                     print(f"Skipping facility {facility['name']} - no valid phone numbers")
#                     continue

#                 new_facility_data = {
#                     "name": facility["name"],
#                     "district_id": district_id,
#                     "facility_type": facility["type"],
#                     "ownership": facility["ownership"],
#                     "registration_number": facility.get("registration_number"),
#                     "is_approved": facility.get("is_approved", False),
#                 }
#                 try:
#                     new_facility = facility_repository.create(data=new_facility_data)
#                     print(f"{number}. Facility {new_facility.name} created.")

#                     # Create facility contacts
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
#             print("\n")
#         finally:
#             db_session.close()

#     print("CREATED LOCATIONS SUCCESSFULLY!")

db_session_generator = db_session_dependency()
db_session = next(db_session_generator)  # type: ignore

region_repository = RegionRepository(db_session=db_session)
district_repository = DistrictRepository(db_session=db_session)
facility_repository = FacilityRepository(db_session=db_session)
facility_contact_repository = FacilityContactRepository(db_session=db_session)


def create_regions(*, file_path: str) -> None:
    """Create default regions data from regions file

    Args:
        file_path (str): The path to the regions json file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Regions json file not found: {file_path}")

    print("-------------------------CREATING REGIONS-------------------------")
    with open(file_path, mode="r", encoding="utf-8") as regions_file:
        try:
            regions_data: list[dict] = json.load(regions_file)

            for number, region in enumerate(regions_data, start=1):
                try:
                    new_region = region_repository.create(data=region)
                    print(f"{number}. Region {new_region.name} created.")
                except ObjectAlreadyExistsException:
                    print(f"Region {region['name']} already exists.")

            print("DONE")

        except Exception as e:
            print(f"Error creating regions: {str(e)}")


def create_districts(*, file_path: str) -> None:
    """Create default districts data from districts file

    Args:
        file_path (str): The path to the districts json file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Districts json file not found: {file_path}")

    print("-------------------------CREATING DISTRICTS-------------------------")
    with open(file_path, mode="r", encoding="utf-8") as districts_file:
        try:
            districts_data: list[dict] = json.load(districts_file)

            for number, district in enumerate(districts_data, start=1):
                try:
                    district_region = region_repository.get_by_field(
                        field_name="name", value=district["region"], operator="eq"
                    )
                    district_data = CreateDistrictSchema(name=district["name"], region_id=str(district_region.id))  # type: ignore
                    new_district = district_repository.create(data=district_data.model_dump())
                    print(f"{number}. District {new_district.name} created.")
                except ObjectAlreadyExistsException:
                    print(f"District {district['name']} already exists.")

            print("DONE")

        except Exception as e:
            print(f"Error creating districts: {str(e)}")


def create_facilities_facilities_contacts(*, file_path: str) -> None:
    """Create default facilities and facility contacts data from facilities file

    Args:
        file_path (str): The path to the facilities json file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Facilities json file not found: {file_path}")

    print("-------------------------CREATING FACILITIES AND FACILITY CONTACTS-------------------------")
    with open(file_path, mode="r", encoding="utf-8") as facilities_file:
        try:
            facilities_data: list[dict] = json.load(facilities_file)

            for number, facility in enumerate(facilities_data, start=1):
                try:
                    district = district_repository.get_by_field(
                        field_name="name", value=facility["district"], operator="eq"
                    )
                    if district is None:
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

                    # Create facility contacts
                    phone_numbers = []
                    if facility.get("phone"):
                        raw_phone = str(facility["phone"]).strip()
                        if "/" in raw_phone:
                            # Split multiple phone numbers
                            phone_numbers = [phone.strip() for phone in raw_phone.split("/") if phone.strip()]
                        else:
                            phone_numbers = [raw_phone]

                    # Prefix each phone number with 233 and validate
                    processed_phone_numbers = []
                    for phone in phone_numbers:
                        if phone.startswith("0"):
                            phone = phone[1:]  # Remove leading 0
                        processed_phone = f"233{phone}"
                        # Basic validation - should be 12 digits after 233
                        if len(processed_phone) == 12 and processed_phone.isdigit():
                            processed_phone_numbers.append(processed_phone)

                    for phone_number in processed_phone_numbers:
                        contact_data = {
                            "facility_id": str(new_facility.id),
                            "contact_number": phone_number,
                        }
                        facility_contact_repository.create(data=contact_data)
                        print(f"  - Contact: {phone_number}")
                except ObjectAlreadyExistsException:
                    print(f"Facility {facility['name']} already exists.")
            print("DONE")
        except Exception as e:
            print(f"Error creating facilities: {str(e)}")


if __name__ == "__main__":
    # locations_file_path = os.path.join(os.path.dirname(__file__), "facilities.json")
    # create_locations(file_path=locations_file_path)
    try:
        regions_file_path = os.path.join(os.path.dirname(__file__), "regions.json")
        districts_file_path = os.path.join(os.path.dirname(__file__), "districts.json")
        facilities_file_path = os.path.join(os.path.dirname(__file__), "facilities.json")
        create_regions(file_path=regions_file_path)
        create_districts(file_path=districts_file_path)
        create_facilities_facilities_contacts(file_path=facilities_file_path)
    finally:
        db_session.commit()
        db_session.close()
        db_session_generator.close()
