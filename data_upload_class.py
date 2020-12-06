import base64
import json
import zlib
import requests

import secrets


class Upload:
    """
    Class load a shifts or motivation data, selected by 'load_type'
    """
    @staticmethod
    def __server_request(api_url, params):
        """
        GET request to server
        :param api_url: url address of the API
        :param params: dictionary with request parameters (type_query, type, name, pass, date, lang)
        :return: full content of the request in form of dictionary
        """
        res = requests.get(url=api_url, params=params)
        if res.status_code != 200:
            print("Status_code is not 200")
            print(f"status_code: {res.status_code}")
            raise RuntimeError("Server gives not ok respond")
        else:
            res_content = json.loads(res.content)  # res.content - "binary" data, not html-formatted
            # debug:
            # print(f"Ответ вызова {params['type_query']} содержит следующие поля: ")
            # for key, val in res_content.items():
            #     print(key)
            if res_content['status'] != "1":
                print('API respond.content["status"] is not "1")')
                print(f"it is {res_content['status']}")
                raise RuntimeError("API gives not ok respond")
        return res_content

    @staticmethod
    def __decode_decompress(data):
        """
        Takes 'data' part of the server respond and transforms it into readable format.
        The chain of transformations is: data (UTF8 encoded string) -> byte encoding -> base64 decoding ->
        zlib decompress -> byte decoding -> JSON loading -> dictionary with data
        :param data: 'data' part of the server respond
        :return: whole data in dictionary format
        """
        encoded_data_bytes = data.encode('UTF-8')  # string into a bytes-like object
        decoded_data_bytes = base64.b64decode(encoded_data_bytes)  # bytes-like object base64 decoded
        final_data_bytes = zlib.decompress(decoded_data_bytes)  # bytes-like object zlib decompressed
        final_data_json = final_data_bytes.decode('utf-8')  # encoded string to decoded plain string with JSON data
        final_data = json.loads(final_data_json)  # parse JSON to python (list)
        return final_data

    def __init__(self, load_type, load_date):
        """
        Choose upload type: shifts or motivation data, and upload date
        :param load_type: 'shifts' or 'motivation'
        :param load_date: date in YYYY-MM-DD string format
        """
        assert load_type == 'shifts' or load_type == 'motivation', 'load_type should be "shifts" or "motivation"'
        self.load_type = load_type
        self.load_date = load_date
        self._request_params = None  # initiates in upload method

    def upload(self):
        """
        Calls class methods and loads data by selected date and type
        :return: dictionary with desired data
        """
        if self.load_type == 'motivation':
            u_type = 129
        elif self.load_type == 'shifts':
            u_type = 127
        else:
            raise TypeError('Unknown type')
        self._request_params = {
            'type_query': secrets.type_query,
            'type': u_type,
            'name': secrets.login,
            'pass': secrets.password,
            'date': self.load_date,
            'lang': 'ru'
        }
        request_content = self.__server_request(secrets.api_url, self._request_params)
        s_m_dict = self.__decode_decompress(request_content['data'])
        return s_m_dict
