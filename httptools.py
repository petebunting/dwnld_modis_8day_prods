#!/usr/bin/env python
"""
THIS IS EDITED FROM RSGISLIB TO AVOID DEPENDENCY IN THIS REPO.

The tools.httptools
"""
from typing import Dict
import json
import os

import tqdm
import requests

def create_md5_hash(input_file: str, block_size: int = 4096) -> str:
    """
    A function which calculates finds the MD5 hash string of the input file.

    :param input_file: the input file for which the MD5 hash string with be found.
    :param block_size: the size of the blocks the file is read in in bytes
                       (default 4096; i.e., 4kb)
    :return: MD5 hash string of the file.

    """
    import hashlib

    md5_hash = hashlib.md5()
    with open(input_file, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(block_size), b""):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()

class RSGISPyResponseException(Exception):
    def __init__(self, value, response=None):
        """
        Init for the RSGISPyResponseException class
        """
        self.value = value
        self.response = response

    def __str__(self):
        """
        Return a string representation of the exception
        """
        return "HTTP status {0} {1}: {2}".format(
            self.response.status_code, self.response.reason, repr(self.value)
        )


def check_http_response(response: requests.Response, url: str) -> bool:
    """
    Check the HTTP response and raise an exception with appropriate error message
    if request was not successful.

    :param response:
    :param url:
    :return:

    """
    try:
        response.raise_for_status()
        success = True
    except (requests.HTTPError, ValueError):
        success = False
        excpt_msg = "Invalid API response."
        try:
            excpt_msg = response.headers["cause-message"]
        except:
            try:
                excpt_msg = response.json()["error"]["message"]["value"]
            except:
                excpt_msg = (
                    "Unknown error ('{0}'), check url in a web browser: '{1}'".format(
                        response.reason, url
                    )
                )
        api_error = RSGISPyResponseException(excpt_msg, response)
        api_error.__cause__ = None
        raise api_error
    return success


def send_http_json_request(
    url: str,
    data: Dict = None,
    api_key: str = None,
    convert_to_json: bool = True,
    header_data: Dict = None,
) -> Dict:
    """
    A function which sends a http request with a json data packet.
    If an error occurs an exception will be raised.

    :param url: The URL for the request to be sent.
    :param data: dictionary of data which can be converted to str
                 using json.dumps.
    :param api_key: if provided then the api-key will be provided
                    via the http header.
    :param convert_to_json:
    :param header_data: a dict of header information.
    :return: A dict of data returned from the server.

    """
    if convert_to_json:
        if data is None:
            params_data = None
        else:
            params_data = json.dumps(data)
    else:
        params_data = data

    if api_key == None:
        response = requests.post(url, params_data, headers=header_data)
    else:
        if header_data is not None:
            header_data["X-Auth-Token"] = api_key
        else:
            header_data = {"X-Auth-Token": api_key}
        response = requests.post(url, params_data, headers=header_data)

    try:
        http_status_code = response.status_code
        if response == None:
            raise Exception("No output from service")

        if http_status_code == 404:
            raise Exception("404 Not Found")
        elif http_status_code == 401:
            raise Exception("401 Unauthorized")
        elif http_status_code == 400:
            raise Exception(f"Error Code: {http_status_code}")

        output = json.loads(response.text)
    except Exception as e:
        response.close()
        raise Exception(f"{e}")
    response.close()

    return output


def download_file_http(
    input_url: str,
    out_file_path: str,
    username: str = None,
    password: str = None,
    no_except: bool = True,
):
    """

    :param input_url:
    :param out_file_path:
    :param username:
    :param password:
    :return:

    """
    session_http = requests.Session()
    if (username is not None) and (password is not None):
        session_http.auth = (username, password)
    user_agent = "pbdwnld/0.1"
    session_http.headers["User-Agent"] = user_agent

    tmp_dwnld_path = out_file_path + ".incomplete"

    headers = {}

    try:
        with session_http.get(
            input_url, stream=True, auth=session_http.auth, headers=headers
        ) as r:
            if check_http_response(r, input_url):
                total = int(r.headers.get("content-length", 0))
                chunk_size = 2 ** 20
                n_chunks = int(total / chunk_size) + 1

                with open(tmp_dwnld_path, "wb") as f:
                    for chunk in tqdm.tqdm(
                        r.iter_content(chunk_size=chunk_size), total=n_chunks
                    ):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
        if os.path.exists(tmp_dwnld_path):
            os.rename(tmp_dwnld_path, out_file_path)
            print("Download Complete: {}".format(out_file_path))

    except Exception as e:
        if no_except:
            print(e)
        else:
            raise Exception("{}".format(e))
        return False
    return True


def wget_download_file(
    input_url: str,
    out_file_path: str,
    username: str = None,
    password: str = None,
    try_number: int = 10,
    time_out: int = 60,
    input_url_md5: str = None,
) -> (bool, str):
    """
    A function which downloads a file from a url using the wget command line tool.
    If a username or password are provided then both must be provided.

    :param input_url_md5:
    :param input_url: string with the URL to be downloaded.
    :param out_file_path: output file name and path.
    :param username: username for the download, if required. Default is None meaning
                     it will be ignored.
    :param password: password for the download, if required. Default is None meaning
                     it will be ignored.
    :param try_number: number of attempts at the download. Default is 10.
    :param time_out: number of seconds to time out Default is 60.
    :return: boolean specifying whether the file had been successfully downloaded
             and a string with user feedback (e.g., error message)

    """
    import subprocess

    try_number = str(try_number)
    time_out = str(time_out)
    success = False
    out_message = ""
    command = [
        "wget",
        "-c",
        "-O",
        out_file_path,
        "-t",
        f"{try_number}",
        "-T",
        f"{time_out}",
        "--no-check-certificate",
    ]
    if (username is not None) and (password is not None):
        command.append("--user")
        command.append(username)
        command.append("--password")
        command.append(password)
    command.append(input_url)

    download_state = -1
    try:
        download_state = subprocess.call(command)
    except Exception as e:
        out_message = (
            f"Download of file ({out_file_path}) failed.: Exception:\n" + e.__str__()
        )

    if download_state == 0:
        if input_url_md5 is not None:
            dwnld_file_md5 = create_md5_hash(out_file_path)
            if dwnld_file_md5 == input_url_md5:
                success = True
                out_message = "File Downloaded and MD5 to checked."
            else:
                success = False
                out_message = "File Downloaded but MD5 did not match."
        else:
            success = True
            out_message = "File Downloaded but no MD5 to check against."

    if out_message == "":
        out_message = "File did not successfully download but no exception thrown."

    return success, out_message
