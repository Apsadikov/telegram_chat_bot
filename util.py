import re


def is_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None


def extract_google_spreadsheet_id(url):
    url = url.replace('https://docs.google.com/spreadsheets/d/', '')
    url = url.replace('/edit?usp=sharing', '')
    return url


def extract_google_disc_folder(url):
    url = url.replace('https://drive.google.com/drive/folders/', '')
    url = url.replace('?usp=sharing', '')
    return url
