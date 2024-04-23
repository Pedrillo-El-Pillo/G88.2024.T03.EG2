"""Module for the hotel manager"""
import re
import json
from datetime import datetime

from uc3m_travel.hotel_management_exception import HotelManagementException
from uc3m_travel.hotel_reservation import HotelReservation
from uc3m_travel.hotel_stay import HotelStay
from uc3m_travel.hotel_management_config import JSON_FILES_PATH
from freezegun import freeze_time


class ValidateParameters:
    """Superclass extracted from HotelManager()"""
    def validatecreditcard(self, credit_card):
        """validates the credit card number using luhn algorithm"""
        #taken form
        # https://allwin-raju-12.medium.com/
        # credit-card-number-validation-using-luhn's-algorithm-in-python-c0ed2fac6234
        # PLEASE INCLUDE HERE THE CODE FOR VALIDATING THE GUID
        # RETURN TRUE IF THE GUID IS RIGHT, OR FALSE IN OTHER CASE

        myregex = re.compile(r"^[0-9]{16}")
        res = myregex.fullmatch(credit_card)
        if not res:
            raise HotelManagementException("Invalid credit card format")

        def digits_of(n):
            return [int(d) for d in str(n)]

        digits = digits_of(credit_card)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = 0
        checksum += sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        if not checksum % 10 == 0:
            raise HotelManagementException("Invalid credit card number (not luhn)")
        return credit_card

    def validate_room_type(self, room_type):
        """validates the room type value using regex"""
        myregex = re.compile(r"(SINGLE|DOUBLE|SUITE)")
        res = myregex.fullmatch(room_type)
        if not res:
            raise HotelManagementException("Invalid roomtype value")
        return room_type

    def validate_arrival_date(self, arrival_date):
        """validates the arrival date format  using regex"""
        myregex = re.compile(r"^(([0-2]\d|-3[0-1])\/(0\d|1[0-2])\/\d\d\d\d)$")
        res = myregex.fullmatch(arrival_date)
        if not res:
            raise HotelManagementException("Invalid date format")
        return arrival_date

    def validate_phonenumber(self, phone_number):
        """validates the phone number format  using regex"""
        myregex = re.compile(r"^(\+)[0-9]{9}")
        res = myregex.fullmatch(phone_number)
        if not res:
            raise HotelManagementException("Invalid phone number format")
        return phone_number

    def validate_numdays(self, num_days):
        """validates the number of days"""
        try:
            days = int(num_days)
        except ValueError as ex:
            raise HotelManagementException("Invalid num_days datatype") from ex
        if (days < 1 or days > 10):
            raise HotelManagementException("Numdays should be in the range 1-10")
        return num_days

    @staticmethod
    def validate_dni(dni):
        """RETURN TRUE IF THE DNI IS RIGHT, OR FALSE IN OTHER CASE"""
        dni_letter_dict = {"0": "T", "1": "R", "2": "W", "3": "A", "4": "G", "5": "M",
             "6": "Y", "7": "F", "8": "P", "9": "D", "10": "X", "11": "B",
             "12": "N", "13": "J", "14": "Z", "15": "S", "16": "Q", "17": "V",
             "18": "H", "19": "L", "20": "C", "21": "K", "22": "E"}
        dni_numbers = int(dni[0:8])
        dni_choose_letter = str(dni_numbers % 23)
        return dni[8] == dni_letter_dict[dni_choose_letter]

    def validate_localizer(self, room_key):
        """validates the localizer format using a regex"""
        regex_format = r'^[a-fA-F0-9]{32}$'
        myregex = re.compile(regex_format)
        if not myregex.fullmatch(room_key):
            raise HotelManagementException("Invalid localizer")
        return room_key


class HotelManager(ValidateParameters):
    """Class with all the methods for managing reservations and stays"""

    def __init__(self):
        pass

    def read_data_from_json(self, json_file):
        """reads the content of a json file with two fields: CreditCard and phoneNumber"""
        json_data = self.store_json_into_list(json_file, "Wrong file or file path")
        try:
            credit_card = json_data["CreditCard"]
            phone_number = json_data["phoneNumber"]
            req = HotelReservation(id_card="12345678Z",
                                   credit_card_number=credit_card,
                                   name_surname="John Doe",
                                   phone_number=phone_number,
                                   room_type="single",
                                   num_days=3,
                                   arrival="20/01/2024")
        except KeyError as e:
            raise HotelManagementException("JSON Decode Error - Invalid JSON Key") from e
        if not self.validatecreditcard(credit_card):
            raise HotelManagementException("Invalid credit card number")
        # Close the file
        return req

    # pylint: disable=too-many-arguments
    def room_reservation(self,
                         credit_card: str,
                         name_surname: str,
                         id_card: str,
                         phone_number: str,
                         room_type: str,
                         arrival_date: str,
                         num_days: int) -> str:
        """manages the hotel reservation: creates a reservation and saves it into a json file"""

        self.check_id_card(id_card)

        room_type = self.validate_room_type(room_type)

        my_reservation = self.check_data(arrival_date, credit_card, id_card,
                                         name_surname, num_days, phone_number,
                                         room_type)

        # escribo el fichero Json con todos los datos
        file_store = JSON_FILES_PATH + "store_reservation.json"

        #leo los datos del fichero si existe , y si no existe creo una lista vacia
        data_list = self.store_data_into_list_if_file_exists(file_store)

        #compruebo que esta reserva no esta en la lista
        for item in data_list:
            if my_reservation.localizer == item["_HotelReservation__localizer"]:
                raise HotelManagementException("Reservation already exists")
            if my_reservation.id_card == item["_HotelReservation__id_card"]:
                raise HotelManagementException("This ID card has another reservation")
        #añado los datos de mi reserva a la lista , a lo que hubiera
        data_list.append(my_reservation.__dict__)

        #escribo la lista en el fichero
        self.write_into_json(file_store, data_list)

        return my_reservation.localizer

    def check_data(self, arrival_date, credit_card, id_card,
                   name_surname, num_days, phone_number, room_type):
        """checks that the main data is correct"""
        regex_format = r"^(?=^.{10,50}$)([a-zA-Z]+(\s[a-zA-Z]+)+)$"
        my_regex = re.compile(regex_format)
        regex_matches = my_regex.fullmatch(name_surname)
        if not regex_matches:
            raise HotelManagementException("Invalid name format")
        credit_card = self.validatecreditcard(credit_card)
        arrival_date = self.validate_arrival_date(arrival_date)
        num_days = self.validate_numdays(num_days)
        phone_number = self.validate_phonenumber(phone_number)
        my_reservation = HotelReservation(id_card=id_card,
                                          credit_card_number=credit_card,
                                          name_surname=name_surname,
                                          phone_number=phone_number,
                                          room_type=room_type,
                                          arrival=arrival_date,
                                          num_days=num_days)
        return my_reservation

    def check_id_card(self, id_card):
        """checks that the id_card format is correct"""
        regex_format = r'^[0-9]{8}[A-Z]{1}$'
        my_regex = re.compile(regex_format)
        if not my_regex.fullmatch(id_card):
            raise HotelManagementException("Invalid IdCard format")
        if not self.validate_dni(id_card):
            raise HotelManagementException("Invalid IdCard letter")

    def guest_arrival(self, file_input: str) -> str:
        """manages the arrival of a guest with a reservation"""
        input_list = self.store_json_into_list(file_input, "Error: file input not found")

        my_id_card, my_localizer = self.get_and_validate_json(input_list)
        # self.validate_localizer() hay que validar

        #buscar en almacén
        file_store = JSON_FILES_PATH + "store_reservation.json"
        #leo los datos del fichero , si no existe deber dar error porque el almacen de reservaa
        # debe existir para hacer el checkin
        store_list = self.store_json_into_list(file_store, "Error: store reservation not found")
        (reservation_date_arrival,
         reservation_days,
         reservation_room_type) = self.create_new_reservation(my_id_card,
                                                              my_localizer,
                                                              store_list)

        self.check_equals_date(reservation_date_arrival)

        # genero la room key para ello llamo a Hotel Stay
        my_checkin = HotelStay(idcard=my_id_card, numdays=int(reservation_days),
                               localizer=my_localizer, roomtype=reservation_room_type)

        self.save_checkin(my_checkin)

        return my_checkin.room_key

    def save_checkin(self, my_checkin):
        """saves the information obtained from the checkin"""
        # Ahora lo guardo en el almacen nuevo de checkin
        # escribo el fichero Json con todos los datos
        file_store = JSON_FILES_PATH + "store_check_in.json"
        room_key_list = self.store_data_into_list_if_file_exists(file_store)
        # comprobar que no he hecho otro ckeckin antes
        for item in room_key_list:
            if my_checkin.room_key == item["_HotelStay__room_key"]:
                raise HotelManagementException("ckeckin  ya realizado")
        # añado los datos de mi reserva a la lista , a lo que hubiera
        room_key_list.append(my_checkin.__dict__)
        self.write_into_json(file_store, room_key_list)

    def get_and_validate_json(self, input_list):
        """gets JSON info and then validates it"""
        try:
            my_localizer = input_list["Localizer"]
            my_id_card = input_list["IdCard"]
        except KeyError as e:
            raise HotelManagementException("Error - Invalid Key in JSON") from e
        self.check_id_card(my_id_card)
        self.validate_localizer(my_localizer)
        return my_id_card, my_localizer


    def create_new_reservation(self, my_id_card, my_localizer, store_list):
        """checks that the reservation is correct, then creates it"""
        # compruebo si esa reserva esta en el almacen
        found = False
        for item in store_list:
            if my_localizer == item["_HotelReservation__localizer"]:
                reservation_days = item["_HotelReservation__num_days"]
                reservation_room_type = item["_HotelReservation__room_type"]
                reservation_date_timestamp = item["_HotelReservation__reservation_date"]
                reservation_credit_card = item["_HotelReservation__credit_card_number"]
                reservation_date_arrival = item["_HotelReservation__arrival"]
                reservation_name = item["_HotelReservation__name_surname"]
                reservation_phone = item["_HotelReservation__phone_number"]
                reservation_id_card = item["_HotelReservation__id_card"]
                found = True
        if not found:
            raise HotelManagementException("Error: localizer not found")
        if my_id_card != reservation_id_card:
            raise HotelManagementException("Error: Localizer is not correct for this IdCard")
        self.generate_reservation(my_localizer, reservation_credit_card,
                                  reservation_date_arrival,
                                  reservation_date_timestamp,
                                  reservation_days,
                                  reservation_id_card,
                                  reservation_name,
                                  reservation_phone,
                                  reservation_room_type)
        return reservation_date_arrival, reservation_days, reservation_room_type

    def generate_reservation(self, my_localizer, reservation_credit_card,
                             reservation_date_arrival,
                             reservation_date_timestamp,
                             reservation_days,
                             reservation_id_card,
                             reservation_name,
                             reservation_phone,
                             reservation_room_type):
        """generation a reservation instance"""
        # regenerate clave y ver si coincide
        reservation_date = datetime.fromtimestamp(reservation_date_timestamp)
        with freeze_time(reservation_date):
            new_reservation = HotelReservation(credit_card_number=reservation_credit_card,
                                               id_card=reservation_id_card,
                                               num_days=reservation_days,
                                               room_type=reservation_room_type,
                                               arrival=reservation_date_arrival,
                                               name_surname=reservation_name,
                                               phone_number=reservation_phone)
        if new_reservation.localizer != my_localizer:
            raise HotelManagementException("Error: reservation has been manipulated")

    def check_equals_date(self, reservation_date_arrival):
        """checks if the date corresponds to the expected"""
        # compruebo si hoy es la fecha de checkin
        reservation_format = "%d/%m/%Y"
        date_obj = datetime.strptime(reservation_date_arrival, reservation_format)
        if date_obj.date() != datetime.date(datetime.utcnow()):
            raise HotelManagementException("Error: today is not reservation date")

    def store_data_into_list_if_file_exists(self, file_store) -> list:
        """in charge of loading the json into a list, if the file does not exist,
        we will receive an empty list"""
        # leo los datos del fichero si existe , y si no existe creo una lista vacia
        try:
            with open(file_store, "r", encoding="utf-8", newline="") as file:
                room_key_list = json.load(file)
        except FileNotFoundError:
            room_key_list = []
        except json.JSONDecodeError as ex:
            raise HotelManagementException("JSON Decode Error - Wrong JSON Format") from ex
        return room_key_list

    def write_into_json(self, file_store, room_key_list):
        """write into the JSON the information needed"""
        try:
            with open(file_store, "w", encoding="utf-8", newline="") as file:
                json.dump(room_key_list, file, indent=2)
        except FileNotFoundError as ex:
            raise HotelManagementException("Wrong file  or file path") from ex

    def store_json_into_list(self, file_input, error_message) -> list:
        """in charge of loading the json into a list"""
        try:
            with open(file_input, "r", encoding="utf-8", newline="") as file:
                input_list = json.load(file)
        except FileNotFoundError as ex:
            raise HotelManagementException(error_message) from ex
        except json.JSONDecodeError as ex:
            raise HotelManagementException("JSON Decode Error - Wrong JSON Format") from ex
        return input_list

    def guest_checkout(self, room_key: str) -> bool:
        """manages the checkout of a guest"""
        successful = GuestCheckout(room_key).checkout()
        return successful


class GuestCheckout:
    """Class with all the methods related to GuestCheckout"""
    def __init__(self, room_key: str):
        self.room_key = room_key
        self.hotel_manager = HotelManager()

    def checkout(self):
        """Functionality of the given function"""
        self.validate_roomkey(self.room_key)
        # check thawt the roomkey is stored in the checkins file
        file_store = JSON_FILES_PATH + "store_check_in.json"
        room_key_list = self.hotel_manager.store_json_into_list(file_store, "Error: store checkin not found")

        # comprobar que esa room_key es la que me han dado
        found = False
        for item in room_key_list:
            if self.room_key == item["_HotelStay__room_key"]:
                departure_date_timestamp = item["_HotelStay__departure"]
                found = True
        if not found:
            raise HotelManagementException("Error: room key not found")

        today = datetime.utcnow().date()
        if datetime.fromtimestamp(departure_date_timestamp).date() != today:
            raise HotelManagementException("Error: today is not the departure day")

        file_store_checkout = JSON_FILES_PATH + "store_check_out.json"
        room_key_list = self.hotel_manager.store_data_into_list_if_file_exists(file_store_checkout)

        for checkout in room_key_list:
            if checkout["room_key"] == self.room_key:
                raise HotelManagementException("Guest is already out")

        room_checkout = {"room_key": self.room_key,
                         "checkout_time": datetime.timestamp(datetime.utcnow())}

        room_key_list.append(room_checkout)

        self.hotel_manager.write_into_json(file_store_checkout, room_key_list)

        return True

    def validate_roomkey(self, room_key):
        """validates the roomkey format using a regex"""
        r = r'^[a-fA-F0-9]{64}$'
        myregex = re.compile(r)
        if not myregex.fullmatch(room_key):
            raise HotelManagementException("Invalid room key format")
        return room_key
