from bson import ObjectId
from fastapi import WebSocket
import re
from datetime import datetime


class ListField(ObjectId):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="list")

    @classmethod
    def validate(cls, v: list):
        return clear_objectid_in_list(v)
    

class DictField(ObjectId):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="dict")

    @classmethod
    def validate(cls, v: dict):
        return clear_objectid_in_dict(v)
    

def clear_objectid_in_list(list_: list):
    for count, value in enumerate(list_):
        if type(value) is ObjectId:
            list_[count] = str(value)
        if type(value) != dict:
            continue
        list_[count] = clear_objectid_in_dict(value, True)

    return list_


def clear_objectid_in_dict(dict_: dict, came_from_list: bool = False):
    for field in dict_.keys():
        if type(dict_[field]) is list: 
            clear_objectid_in_list(dict_[field])
        if type(dict_[field]) is ObjectId:
            dict_[field] = str(dict_[field])
        if type(dict_[field]) is datetime:
            dict_[field] = dict_[field].strftime("%Y-%m-%dT%H:%M:%S")
        if type(dict_[field]) is bytes:
            dict_[field] = "Para retornar o PDF em bytes consulte o documento sozinho!"\
                            if came_from_list else dict_[field].decode()
        if field == "columns":
            for count, iterable in enumerate(dict_[field]):
                dict_[field][count]["_id"] = str(iterable["_id"])
        if field == "headers":
            for count, iterable in enumerate(dict_[field]):
                dict_[field][count]["_id"] = str(iterable["_id"])
                dict_[field][count]["column_left"] = str(iterable["column_left"])
                dict_[field][count]["column_right"] = str(iterable["column_right"])
        if field == "parameters":
            clear_objectid_in_dict(dict_[field])

    return dict_