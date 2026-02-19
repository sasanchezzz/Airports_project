from enum import Enum


class AircraftModelType(str, Enum):
    airbus_319 = "Airbus A319-100"
    airbus_320 = "Airbus A320-200"
    airbus_321 = "Airbus A321-200"
    airbus_330 = "Airbus А330-300"
    airbus_350 = "Airbus A350-900"
    boieng_737_300 = "Boeing 737-300"
    boieng_737_800 = "Boeing 737-800"
    boieng_767 = "Boeing 767-300"
    boieng_777 = "Boeing 777-300"
    cessna_208 = "Cessna 208 Caravan"
    bombardier_200 = "Bombardier CRJ-200"
    sukhoi_100 = "Sukhoi SuperJet-100"
    mc_21_2 = "МС-21-200"
    mc_21_3 = "МС-21-310"
    mc_21_4 = "МС-21-400"
    ty_204 = "Ту-204-100"
    ty_214 = "Ту-214-200"
