"""Guest arrival test cases"""
import csv
import json
import os.path
import shutil
import hashlib
from unittest import TestCase
from os import remove
from freezegun import freeze_time
from uc3m_travel import (JSON_FILES_PATH,
                         JSON_FILES_GUEST_ARRIVAL,
                         HotelManager,
                         HotelManagementException)

class TestHotelReservation(TestCase):
    """Class for testing deliver_product"""

    def setUp(self):
        """ initilize the content of the json files """
        fichero = "store_check_in.json"
        my_file = JSON_FILES_PATH + fichero
        if os.path.exists(my_file):
            print("deleted checkin")
            remove(my_file)

        fichero = "store_reservation.json"
        my_file = JSON_FILES_PATH + fichero
        if os.path.exists(my_file):
            print("deleted reservation")
            remove(my_file)


        ##insert the reservation
        with freeze_time("2024/03/22 13:00:00"):
            hotel_mngr = HotelManager()
            #first reservation for valid
            localizer = hotel_mngr.room_reservation(credit_card="5105105105105100",
                                                    name_surname="JOSE LOPEZ",
                                                    id_card="12345678Z",
                                                    phone_number="+341234567",
                                                    room_type="SINGLE",
                                                    arrival_date="01/07/2024",
                                                    num_days=1)
            self.assertEqual(localizer, "450a53be9b39944e62e7164ca5f5aadf")


    @staticmethod
    def read_file():
        """ this method read a Json file and return the value """
        my_file = JSON_FILES_PATH + "store_check_in.json"
        try:
            with open(my_file, "r", encoding="utf-8", newline="") as file:
                data = json.load(file)
        except FileNotFoundError as ex:
            raise HotelManagementException("Wrong file or file path") from ex
        except json.JSONDecodeError as ex:
            raise HotelManagementException("JSON Decode Error - Wrong JSON Format") from ex
        return data

    @freeze_time("2024/07/02 13:00:00")
    def test_case_valid_reservation_invalid_arrival_date(self):
        """Invalid arrival date"""
        test_file = JSON_FILES_GUEST_ARRIVAL + "key_ok.json"
        mngr = HotelManager()
        checkins_file = JSON_FILES_PATH + "store_check_in.json"
        #we calculater the files signature bejore calling the tested method
        if os.path.isfile(checkins_file):
            with open(checkins_file, "r", encoding="utf-8", newline="") as file_org:
                hash_original = hashlib.md5(str(file_org).encode()).hexdigest()
        else:
            hash_original = ""

        with self.assertRaises(HotelManagementException) as c_m:
            mngr.guest_arrival(test_file)
        self.assertEqual(c_m.exception.message, "Error: today is not reservation date")

        #now we check that the signature of the file is the same (the file didn't change)
        if os.path.isfile(checkins_file):
            with open(checkins_file, "r", encoding="utf-8", newline="") as file:
                hash_new = hashlib.md5(str(file).encode()).hexdigest()
        else:
            hash_new = ""
        self.assertEqual(hash_new, hash_original)

    @freeze_time("2024/07/01 13:00:00")
    #pylint: disable=too-many-locals
    def test_parametrized_cases_tests(self):
        """Parametrized cases read from testingCases_RF2.csv
        time is set to 01/07/2024 since it is the chosen for the valid case"""
        my_cases = JSON_FILES_PATH + "GE2_TestCasesTemplate_2024_F2.csv"
        with open(my_cases, newline='', encoding='utf-8') as csvfile:
            param_test_cases = csv.DictReader(csvfile, delimiter=';')
            mngr = HotelManager()
            for row in param_test_cases:
                # VALID INVALID;ID TEST;FILE;EXPECTED RESULT
                test_id = row['ID_TEST']
                valid = row["VALID_INVALID"]
                result = row["EXPECTED_RESULT"]
                test_file = JSON_FILES_GUEST_ARRIVAL + row["FILE"]
                if valid == "VALID":
                    with self.subTest(test_id + valid):
                        valor = mngr.guest_arrival(test_file)
                        self.assertEqual(result, valor)
                        # Check if this DNI is store in storeRequest.json
                        my_data = self.read_file()
                        found = False
                        for k in my_data:
                            if k["_HotelStay__room_key"] == valor:
                                found = True
                        # if found is False , this assert fails
                        self.assertTrue(found)
                else:
                    with self.subTest(test_id + valid):
                        # read the file to compare file content before and after method call
                        checkins_file = JSON_FILES_PATH + "store_check_in.json"
                        if os.path.isfile(checkins_file):
                            with open(checkins_file, "r", encoding="utf-8", newline="") as file_org:
                                hash_original = hashlib.md5(str(file_org).encode()).hexdigest()
                        else:
                            hash_original = ""

                        with self.assertRaises(HotelManagementException) as c_m:
                            valor = mngr.guest_arrival(test_file)
                        self.assertEqual(c_m.exception.message, result)
                        if os.path.isfile(checkins_file):
                            with open(checkins_file, "r", encoding="utf-8", newline="") as file:
                                hash_new = hashlib.md5(str(file).encode()).hexdigest()
                        else:
                            hash_new = ""
                        self.assertEqual(hash_new, hash_original)


    @freeze_time("2024/07/01 13:00:00")
    def test_get_reservation_data_manipulated_tests( self ):
        """store_reservation_manipulated.json has a reservation manipulated with SUITE and 5 days
        insetad of SINGLE one day reservation"""
        file_test = JSON_FILES_GUEST_ARRIVAL + "key_ok.json"
        my_manager = HotelManager()
        reservations_file = JSON_FILES_PATH + "store_reservation.json"
        checkins_file = JSON_FILES_PATH + "store_check_in.json"
        #swap file preserves an eventual previous reservation json file
        if os.path.isfile(JSON_FILES_PATH + "swap.json"):
            os.remove(JSON_FILES_PATH + "swap.json")
        if not os.path.isfile(JSON_FILES_PATH + "store_reservation_manipulated.json"):
            shutil.copy(JSON_FILES_GUEST_ARRIVAL + "store_reservation_manipulated.json",
                        JSON_FILES_PATH + "store_reservation_manipulated.json")
        #rename the manipulated order's store
        if os.path.isfile(reservations_file):
            os.rename(reservations_file, JSON_FILES_PATH + "swap.json")
        os.rename(JSON_FILES_PATH + "store_reservation_manipulated.json",reservations_file)

        # read the file to compare file content before and after method call
        if os.path.isfile(checkins_file):
            with open(checkins_file, "r", encoding="utf-8", newline="") as file_org:
                hash_original = hashlib.md5(str(file_org).encode()).hexdigest()
        else:
            hash_original = ""

        # check the method
        exception_message = "Exception not raised"
        try:
            my_manager.guest_arrival(file_test)
        #pylint: disable=broad-except
        except Exception as exception_raised:
            #we catch a generic exception to avoid unexpected problems
            exception_message = str(exception_raised)

        #restore the original orders' store
        os.rename(reservations_file, JSON_FILES_PATH + "store_reservation_manipulated.json")
        if os.path.isfile(JSON_FILES_PATH + "swap.json"):

            os.rename(JSON_FILES_PATH + "swap.json", reservations_file)
        # read the file again to campare
        if os.path.isfile(checkins_file):
            with open(checkins_file, "r", encoding="utf-8", newline="") as file:
                hash_new = hashlib.md5(str(file).encode()).hexdigest()
        else:
            hash_new = ""

        self.assertEqual(exception_message, "Error: reservation has been manipulated")
        self.assertEqual(hash_new, hash_original)
