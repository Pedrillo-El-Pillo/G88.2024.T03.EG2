"""Module for testing guest_checkout"""
from unittest import TestCase
import os
import hashlib
import json
from freezegun import freeze_time
from uc3m_travel import HotelManager
from uc3m_travel import HotelManagementException
from uc3m_travel import JSON_FILES_PATH
from uc3m_travel import JSON_FILES_GUEST_ARRIVAL


class TestDeliverProduct(TestCase):
    """Class for testing guest_checkout"""
    @freeze_time("2023-03-08")
    def setUp(self):
        """first prepare the stores"""
        store_reservation = JSON_FILES_PATH + "store_reservation.json"
        store_checkin = JSON_FILES_PATH + "store_check_in.json"
        file_store_ckeck_out = JSON_FILES_PATH + "store_check_out.json"


        if os.path.isfile(store_reservation):
            os.remove(store_reservation)
        if os.path.isfile(store_checkin):
            os.remove(store_checkin)
        if os.path.isfile(file_store_ckeck_out):
            os.remove(file_store_ckeck_out)

        #add orders and shipping info in the stores
        my_manager = HotelManager()
        # add an order in the store
        file_test = JSON_FILES_GUEST_ARRIVAL + "key_ok.json"
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
        with freeze_time("2024/07/01 13:00:00"):
            my_manager.guest_arrival(file_test)



    @freeze_time("2024-07-02")
    def test_checkout_ok(self):
        """basic path , tracking_code is found , and date = today"""
        my_manager = HotelManager()
        value = my_manager.guest_checkout(
            "4f57880d4240350db9b276c84edaacc923a63906a408cc8da2b52c49213d3859")
        self.assertTrue(value)

        file_store_ckeck_out = JSON_FILES_PATH + "store_check_out.json"
        # check store_ckeck_out
        with open(file_store_ckeck_out, "r", encoding="utf-8", newline="") as file:
            data_list = json.load(file)
        found = False
        print(data_list)
        for checkout in data_list:
            if (checkout["room_key"] ==
                    "4f57880d4240350db9b276c84edaacc923a63906a408cc8da2b52c49213d3859"):
                found = True
        self.assertTrue(found)

    @freeze_time("2024-07-02")
    def test_already_checkout(self):
        """basic path , tracking_code is found , and date = today"""
        my_manager = HotelManager()
        value = my_manager.guest_checkout(
            "4f57880d4240350db9b276c84edaacc923a63906a408cc8da2b52c49213d3859")
        self.assertTrue(value)

        file_store_ckeck_out = JSON_FILES_PATH + "store_check_out.json"

        # read the file  to compare
        if os.path.isfile(file_store_ckeck_out):
            with open(file_store_ckeck_out, "r", encoding="utf-8", newline="") as file:
                hash_original = hashlib.md5(str(file).encode()).hexdigest()
        else:
            hash_original = ""


        with self.assertRaises(HotelManagementException) as context_manager:
            my_manager.guest_checkout(
                "4f57880d4240350db9b276c84edaacc923a63906a408cc8da2b52c49213d3859")
        self.assertEqual(context_manager.exception.message, "Guest is already out")

        # read the file again to compare
        if os.path.isfile(file_store_ckeck_out):
            with open(file_store_ckeck_out, "r", encoding="utf-8", newline="") as file:
                hash_new = hashlib.md5(str(file).encode()).hexdigest()
        else:
            hash_new = ""

        self.assertEqual(hash_new, hash_original)
    @freeze_time("2024-07-04")
    def test_guest_checkout_no_date(self):
        """path tracking_code is found , and date is not today"""
        file_store_ckeck_out = JSON_FILES_PATH + "store_check_out.json"
        my_manager = HotelManager()

        # read the file  to compare
        if os.path.isfile(file_store_ckeck_out):
            with open(file_store_ckeck_out, "r", encoding="utf-8", newline="") as file:
                hash_original = hashlib.md5(str(file).encode()).hexdigest()
        else:
            hash_original = ""

        with self.assertRaises(HotelManagementException) as context_manager:
            my_manager.guest_checkout(
                "4f57880d4240350db9b276c84edaacc923a63906a408cc8da2b52c49213d3859")
        self.assertEqual(context_manager.exception.message, "Error: today is not the departure day")

        # read the file again to compare
        if os.path.isfile(file_store_ckeck_out):
            with open(file_store_ckeck_out, "r", encoding="utf-8", newline="") as file:
                hash_new = hashlib.md5(str(file).encode()).hexdigest()
        else:
            hash_new = ""

        self.assertEqual(hash_new, hash_original)

    @freeze_time("2024-07-02")
    def test_guest_checkout_bad_date_signature(self):
        """path signature is not valid format , only 63 chars"""
        file_store_shipments = JSON_FILES_PATH + "store_check_out.json"
        my_manager = HotelManager()
        # read the file  to compare

        if os.path.isfile(file_store_shipments):
            with open(file_store_shipments, "r", encoding="utf-8", newline="") as file:
                hash_original = hashlib.md5(str(file).encode()).hexdigest()
        else:
            hash_original = ""

        with self.assertRaises(HotelManagementException) as context_manager:
            my_manager.guest_checkout(
                "a06c7bede3d584e934e2f5bd3861e625cb31937f9f1a5362a51fbbf38486f1c")
        self.assertEqual(context_manager.exception.message, "Invalid room key format")

        # read the file again to compare
        if os.path.isfile(file_store_shipments):
            with open(file_store_shipments, "r", encoding="utf-8", newline="") as file:
                hash_new = hashlib.md5(str(file).encode()).hexdigest()
        else:
            hash_new = ""

        self.assertEqual(hash_new, hash_original)

    @freeze_time("2024-07-02")
    def test_checkin_code_not_found_date_signature(self):
        """path: signature is not found in store_check_in"""
        file_store_ckeck_out = JSON_FILES_PATH + "store_check_out.json"
        my_manager = HotelManager()
        # read the file  to compare

        if os.path.isfile(file_store_ckeck_out):
            with open(file_store_ckeck_out, "r", encoding="utf-8", newline="") as file:
                hash_original = hashlib.md5(str(file).encode()).hexdigest()
        else:
            hash_original = ""

        with self.assertRaises(HotelManagementException) as context_manager:
            my_manager.guest_checkout(
                "7a8403d8605804cf2534fd7885940f3c3d8ec60ba578bc158b5dc2b9fb68d524")
        self.assertEqual(context_manager.exception.message, "Error: room key not found")

        # read the file again to compare
        if os.path.isfile(file_store_ckeck_out):
            with open(file_store_ckeck_out, "r", encoding="utf-8", newline="") as file:
                hash_new = hashlib.md5(str(file).encode()).hexdigest()
        else:
            hash_new = ""

        self.assertEqual(hash_new, hash_original)

    @freeze_time("2024-07-02")
    def test_guest_checkout_no_store_check_in(self):
        """path: store_check_in is not found, so remove shimpents_store.json"""
        file_store_check_in = JSON_FILES_PATH + "store_check_in.json"
        if os.path.isfile(file_store_check_in):
            os.remove(file_store_check_in)

        my_manager = HotelManager()
        with self.assertRaises(HotelManagementException) as context_manager:
            my_manager.guest_checkout(
                "4f57880d4240350db9b276c84edaacc923a63906a408cc8da2b52c49213d3859")
        self.assertEqual(context_manager.exception.message, "Error: store checkin not found")

    @freeze_time("2023-03-18")
    def test_guest_checkout_store_check_in_is_empty(self):
        """for testing: store_check_in is empty"""
        #write a store_check_in empty
        file_store_check_in = JSON_FILES_PATH + "store_check_in.json"
        data_list=[]
        with open(file_store_check_in, "w", encoding="utf-8", newline="") as file:
            json.dump(data_list, file, indent=2)

        my_manager = HotelManager()
        with self.assertRaises(HotelManagementException) as context_manager:
            my_manager.guest_checkout(
                "847dfd443d86c9c222242010c11a44bd9a09c37b42b6e956db97ba173abefe83")
        self.assertEqual(context_manager.exception.message, "Error: room key not found")
