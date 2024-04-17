"""Module for the hotel manager"""
import re
import json
from datetime import datetime
from uc3m_travel.hotel_management_exception import HotelManagementException
from uc3m_travel.hotel_reservation import HotelReservation
from uc3m_travel.hotel_stay import HotelStay
from uc3m_travel.hotel_management_config import JSON_FILES_PATH
from freezegun import freeze_time


class HotelManager:
    """Class with all the methods for managing reservations and stays"""
    def __init__(self):
        pass

    def validatecreditcard( self, x ):
        """validates the credit card number using luhn altorithm"""
        #taken form
        # https://allwin-raju-12.medium.com/
        # credit-card-number-validation-using-luhns-algorithm-in-python-c0ed2fac6234
        # PLEASE INCLUDE HERE THE CODE FOR VALIDATING THE GUID
        # RETURN TRUE IF THE GUID IS RIGHT, OR FALSE IN OTHER CASE

        myregex = re.compile(r"^[0-9]{16}")
        res = myregex.fullmatch(x)
        if not res:
            raise HotelManagementException("Invalid credit card format")
        def digits_of(n):
            return [int(d) for d in str(n)]


        digits = digits_of(x)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = 0
        checksum += sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        if not checksum % 10 == 0:
            raise HotelManagementException("Invalid credit card number (not luhn)")
        return x

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
    def validate_numdays(self,num_days):
        """validates the number of days"""
        try:
            days = int(num_days)
        except ValueError as ex:
            raise HotelManagementException("Invalid num_days datatype") from ex
        if (days < 1 or days > 10):
            raise HotelManagementException("Numdays should be in the range 1-10")
        return num_days


    @staticmethod
    def validate_dni( d ):
        """RETURN TRUE IF THE DNI IS RIGHT, OR FALSE IN OTHER CASE"""
        c = {"0": "T", "1": "R", "2": "W", "3": "A", "4": "G", "5": "M",
             "6": "Y", "7": "F", "8": "P", "9": "D", "10": "X", "11": "B",
             "12": "N", "13": "J", "14": "Z", "15": "S", "16": "Q", "17": "V",
             "18": "H", "19": "L", "20": "C", "21": "K", "22": "E"}
        v = int(d[ 0:8 ])
        r = str(v % 23)
        return d[8] == c[r]


    def validate_localizer(self, l):
        """validates the localizer format using a regex"""
        r = r'^[a-fA-F0-9]{32}$'
        myregex = re.compile(r)
        if not myregex.fullmatch(l):
            raise HotelManagementException("Invalid localizer")
        return l

    def validate_roomkey(self, l):
        """validates the roomkey format using a regex"""
        r = r'^[a-fA-F0-9]{64}$'
        myregex = re.compile(r)
        if not myregex.fullmatch(l):
            raise HotelManagementException("Invalid room key format")
        return l

    def read_data_from_json(self, fi):
        """reads the content of a json file with two fields: CreditCard and phoneNumber"""
        try:
            with open(fi, encoding='utf-8') as f:
                json_data = json.load(f)
        except FileNotFoundError as e:
            raise HotelManagementException("Wrong file or file path") from e
        except json.JSONDecodeError as e:
            raise HotelManagementException("JSON Decode Error - Wrong JSON Format") from e
        try:
            c = json_data["CreditCard"]
            p = json_data["phoneNumber"]
            req = HotelReservation(id_card="12345678Z",
                                   credit_card_number=c,
                                   name_surname="John Doe",
                                   phone_number=p,
                                   room_type="single",
                                   num_days=3,
                                   arrival="20/01/2024")
        except KeyError as e:
            raise HotelManagementException("JSON Decode Error - Invalid JSON Key") from e
        if not self.validatecreditcard(c):
            raise HotelManagementException("Invalid credit card number")
        # Close the file
        return req

    # pylint: disable=too-many-arguments
    def room_reservation(self,
                         credit_card:str,
                         name_surname:str,
                         id_card:str,
                         phone_number:str,
                         room_type:str,
                         arrival_date: str,
                         num_days:int)->str:
        """manges the hotel reservation: creates a reservation and saves it into a json file"""

        r = r'^[0-9]{8}[A-Z]{1}$'
        my_regex = re.compile(r)
        if not my_regex.fullmatch(id_card):
            raise HotelManagementException("Invalid IdCard format")
        if not self.validate_dni(id_card):
            raise HotelManagementException("Invalid IdCard letter")

        room_type = self.validate_room_type(room_type)


        r = r"^(?=^.{10,50}$)([a-zA-Z]+(\s[a-zA-Z]+)+)$"
        myregex = re.compile(r)
        regex_matches = myregex.fullmatch(name_surname)
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

        # escribo el fichero Json con todos los datos
        file_store = JSON_FILES_PATH + "store_reservation.json"

        #leo los datos del fichero si existe , y si no existe creo una lista vacia
        try:
            with open(file_store, "r", encoding="utf-8", newline="") as file:
                data_list = json.load(file)
        except FileNotFoundError:
            data_list = []
        except json.JSONDecodeError as ex:
            raise HotelManagementException ("JSON Decode Error - Wrong JSON Format") from ex

        #compruebo que esta reserva no esta en la lista
        for item in data_list:
            if my_reservation.localizer == item["_HotelReservation__localizer"]:
                raise HotelManagementException ("Reservation already exists")
            if my_reservation.id_card == item["_HotelReservation__id_card"]:
                raise HotelManagementException("This ID card has another reservation")
        #añado los datos de mi reserva a la lista , a lo que hubiera
        data_list.append(my_reservation.__dict__)

        #escribo la lista en el fichero
        try:
            with open(file_store, "w", encoding="utf-8", newline="") as file:
                json.dump(data_list, file, indent=2)
        except FileNotFoundError as ex:
            raise HotelManagementException("Wrong file  or file path") from ex

        return my_reservation.localizer

    def guest_arrival(self, file_input:str)->str:
        """manages the arrival of a guest with a reservation"""
        try:
            with open(file_input, "r", encoding="utf-8", newline="") as file:
                input_list = json.load(file)
        except FileNotFoundError as ex:
            raise HotelManagementException ("Error: file input not found") from ex
        except json.JSONDecodeError as ex:
            raise HotelManagementException ("JSON Decode Error - Wrong JSON Format") from ex

        # comprobar valores del fichero
        try:
            my_localizer = input_list["Localizer"]
            my_id_card = input_list["IdCard"]
        except KeyError as e:
            raise HotelManagementException("Error - Invalid Key in JSON") from e

        r = r'^[0-9]{8}[A-Z]{1}$'
        my_regex = re.compile(r)
        if not my_regex.fullmatch(my_id_card):
            raise HotelManagementException("Invalid IdCard format")
        if not self.validate_dni(my_id_card):
            raise HotelManagementException("Invalid IdCard letter")

        self.validate_localizer(my_localizer)
        # self.validate_localizer() hay que validar

        #buscar en almacen
        file_store = JSON_FILES_PATH + "store_reservation.json"

        #leo los datos del fichero , si no existe deber dar error porque el almacen de reservaa
        # debe existir para hacer el checkin
        try:
            with open(file_store, "r", encoding="utf-8", newline="") as file:
                store_list = json.load(file)
        except FileNotFoundError as ex:
            raise HotelManagementException ("Error: store reservation not found") from ex
        except json.JSONDecodeError as ex:
            raise HotelManagementException ("JSON Decode Error - Wrong JSON Format") from ex
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
        # regenrar clave y ver si coincide
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

        # compruebo si hoy es la fecha de checkin
        reservation_format = "%d/%m/%Y"
        date_obj = datetime.strptime(reservation_date_arrival, reservation_format)
        if date_obj.date()!= datetime.date(datetime.utcnow()):
            raise HotelManagementException("Error: today is not reservation date")

        # genero la room key para ello llamo a Hotel Stay
        my_checkin = HotelStay(idcard=my_id_card, numdays=int(reservation_days),
                               localizer=my_localizer, roomtype=reservation_room_type)

        #Ahora lo guardo en el almacen nuevo de checkin
        # escribo el fichero Json con todos los datos
        file_store = JSON_FILES_PATH + "store_check_in.json"

        # leo los datos del fichero si existe , y si no existe creo una lista vacia
        try:
            with open(file_store, "r", encoding="utf-8", newline="") as file:
                room_key_list = json.load(file)
        except FileNotFoundError as ex:
            room_key_list = []
        except json.JSONDecodeError as ex:
            raise HotelManagementException("JSON Decode Error - Wrong JSON Format") from ex

        # comprobar que no he hecho otro ckeckin antes
        for item in room_key_list:
            if my_checkin.room_key == item["_HotelStay__room_key"]:
                raise HotelManagementException ("ckeckin  ya realizado")

        #añado los datos de mi reserva a la lista , a lo que hubiera
        room_key_list.append(my_checkin.__dict__)

        try:
            with open(file_store, "w", encoding="utf-8", newline="") as file:
                json.dump(room_key_list, file, indent=2)
        except FileNotFoundError as ex:
            raise HotelManagementException("Wrong file  or file path") from ex

        return my_checkin.room_key

    def guest_checkout(self, room_key:str)->bool:
        """manages the checkout of a guest"""
        self.validate_roomkey(room_key)
        #check thawt the roomkey is stored in the checkins file
        file_store = JSON_FILES_PATH + "store_check_in.json"
        try:
            with open(file_store, "r", encoding="utf-8", newline="") as file:
                room_key_list = json.load(file)
        except FileNotFoundError as ex:
            raise HotelManagementException("Error: store checkin not found") from ex
        except json.JSONDecodeError as ex:
            raise HotelManagementException("JSON Decode Error - Wrong JSON Format") from ex

        # comprobar que esa room_key es la que me han dado
        found = False
        for item in room_key_list:
            if room_key == item["_HotelStay__room_key"]:
                departure_date_timestamp = item["_HotelStay__departure"]
                found = True
        if not found:
            raise HotelManagementException ("Error: room key not found")

        today = datetime.utcnow().date()
        if datetime.fromtimestamp(departure_date_timestamp).date() != today:
            raise HotelManagementException("Error: today is not the departure day")

        file_store_checkout = JSON_FILES_PATH + "store_check_out.json"
        try:
            with open(file_store_checkout, "r", encoding="utf-8", newline="") as file:
                room_key_list = json.load(file)
        except FileNotFoundError as ex:
            room_key_list = []
        except json.JSONDecodeError as ex:
            raise HotelManagementException("JSON Decode Error - Wrong JSON Format") from ex

        for checkout in room_key_list:
            if checkout["room_key"] == room_key:
                raise HotelManagementException("Guest is already out")

        room_checkout={"room_key":  room_key, "checkout_time":datetime.timestamp(datetime.utcnow())}

        room_key_list.append(room_checkout)

        try:
            with open(file_store_checkout, "w", encoding="utf-8", newline="") as file:
                json.dump(room_key_list, file, indent=2)
        except FileNotFoundError as ex:
            raise HotelManagementException("Wrong file  or file path") from ex

        return True
