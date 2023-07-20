import xml.etree.ElementTree as ET

import requests


def check_link(argument):
    base_url = "http://validator.w3.org/feed/check.cgi?url="
    validator = requests.post(base_url + argument + "&output=soap12")
    status = validator.status_code
    resp_length = len(validator.content)
    response = validator.text

    if status == 200:
        root = ET.fromstring(response)
        ns = {"env": "Envelope", "m": "http://www.w3.org/2005/10/feed-validator"}
        error_nums = root.find(".//m:errorcount", ns)

        # print(a)
        if int(error_nums.text) == 1:  # type:ignore
            a = root.iterfind(".//m:errorlist/error/type", ns)
            b = root.iterfind(".//m:errorlist/error/text", ns)
            for item in a:
                if item.text == "UnicodeError":
                    message = "**Subscribed!**"
                    error_message = "no_error"
                    error_message2 = "no_error"
                    return message, error_message, error_message2
                else:
                    for text_rsp in b:
                        message = f"**{item.text}** -> {text_rsp.text}"
                        error_message = "no_error"
                        error_message2 = "no_error"
                        return message, error_message, error_message2

        elif int(error_nums.text) > 1:  # type: ignore
            message = "There seems to be an error regarding your RSS feed link.\nBelow are the error(s): "

            a = root.iterfind(".//m:errorlist/error/type", ns)
            b = root.iterfind(".//m:errorlist/error/text", ns)
            for error_type, error_text in zip(a, b):
                message = f"**{error_type.text}** -> {error_text.text}"
                error_message = "no_error"
                error_message2 = "no_error"
                return message, error_message, error_message2
        else:
            message = "**Subscribed!**"
            error_message = "no_error"
            error_message2 = "no_error"
            return message, error_message, error_message2

    elif status == 301:
        if resp_length > 2000:
            message = f"**{status} Moved Permanently**"
            error_message = "**Error Message**:\n> {}".format(validator.content[:1900])
            error_message2 = "**Continued**:\n> {}".format(validator.content[1901:])
            return message, error_message, error_message2

        else:
            message = f"**{status} Moved Permanently**"
            error_message = "**Error Message**: \n> {}".format(validator.content)
            error_message2 = "no_error"
            return message, error_message, error_message2

    elif status == 308:
        if resp_length > 2000:
            message = f"**{status} Permanent Redirect**"
            error_message = "**Error Message**:\n> {}".format(validator.content[:1900])
            error_message2 = "**Continued**:\n> {}".format(validator.content[1901:])
            return message, error_message, error_message2

        else:
            message = f"**{status} Permanent Redirect**"
            error_message = "**Error Message:** \n> {}".format(validator.content)
            error_message2 = "no_error"
            return message, error_message, error_message2

    elif status == 401:
        if resp_length > 2000:
            message = f"**{status} Unauthorized**"
            error_message = "**Error Message**:\n> {}".format(validator.content[:1900])
            error_message2 = "**Continued**:\n> {}".format(validator.content[1901:])
            return message, error_message, error_message2

        else:
            message = f"**{status} Unauthorized**"
            error_message = "**Error Message**: \n> {}".format(validator.content)
            error_message2 = "no_error"
            return message, error_message, error_message2

    elif status == 403:
        if resp_length > 2000:
            message = f"**{status} Forbidden Error**"
            error_message = "**Error Message**:\n> {}".format(validator.content[:1900])
            error_message2 = "**Continued**:\n> {}".format(validator.content[1901:])
            return message, error_message, error_message2

        else:
            message = f"**{status} Forbidden**"
            error_message = "**Error Message:** \n> {}".format(validator.content)
            error_message2 = "no_error"
            return message, error_message, error_message2

    elif status == 404:
        if resp_length > 2000:
            message = f"**{status} Not Found Error**"
            error_message = "**Error Message**:\n> {}".format(validator.content[:1900])
            error_message2 = "**Continued**:\n> {}".format(validator.content[1901:])
            return message, error_message, error_message2

        else:
            message = f"**{status} Not Found Error**"
            error_message = "**Error Message:** \n> {}".format(validator.content)
            error_message2 = "no_error"
            return message, error_message, error_message2

    elif status == 500:
        if resp_length > 2000:
            message = f"**{status} Internal Server Error**"
            error_message = "**Error Message**:\n> {}".format(validator.text[:1900])
            error_message2 = "**Continued**:\n> {}".format(validator.text[1901:])
            return message, error_message, error_message2
        else:
            message = f"**{status} Internal Server Error**"
            error_message = "**Error Message:** \n> {}".format(validator.content)
            error_message2 = "no_error"
            return message, error_message, error_message2

    elif status == 502:
        if resp_length > 2000:
            message = f"**{status} Bad Gateway Error**"
            error_message = "**Error Message**:\n> {}".format(validator.content[:1900])
            error_message2 = "**Continued**:\n> {}".format(validator.content[1901:])
            return message, error_message, error_message2

        else:
            message = f"**{status} Bad Gateway Error**"
            error_message = "**Error Message:** \n> {}".format(validator.content)
            error_message2 = "no_error"
            return message, error_message, error_message2

    elif status == 504:
        if resp_length > 2000:
            message = f"**{status} Gateway Timeout Error**"
            error_message = "**Error Message**:\n> {}".format(validator.content[:1900])
            error_message2 = "**Continued**:\n> {}".format(validator.content[1901:])
            return message, error_message, error_message2

        else:
            message = f"**{status} Gateway Timeout Error**"
            error_message = "**Error Message:** \n> {}".format(validator.content)
            error_message2 = "no_error"
            return message, error_message, error_message2

    else:
        if resp_length > 2000:
            message = f"**{status} code**"
            error_message = "**Error Message**:\n> {}".format(validator.content[:1900])
            error_message2 = "**Continued**:\n> {}".format(validator.content[1901:])
            return message, error_message, error_message2

        else:
            message = f"**{status} code**"
            error_message = "**Error Message:** \n> {}".format(validator.content)
            error_message2 = "no_error"
            return message, error_message, error_message2
