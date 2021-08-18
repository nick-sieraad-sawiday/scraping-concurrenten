import io
from ftplib import *

import pandas as pd


def load_ftp_excel(file: str, ftp_link: str, user: str, passwd: str, cwd: str) -> pd.DataFrame:
    """
    Extracts excel, csv or xml file from the ftp server

    :param file: The pandas dataframe you want to save
    :param ftp_link: The link of the ftp server
    :param user: The username of the ftp server
    :param passwd: The password of the ftp server
    :param cwd: The path of the ftp server
    :return: Pandas DataFrame created from the file
    """

    ftp = FTP(ftp_link)  # connect to host, default port
    ftp.login(user=user, passwd=passwd)  # credentials for Omnia FTP
    ftp.cwd(cwd)  # open needed folder

    # download the file but first create a virtual file object for it
    download_file = io.BytesIO()  # open virtual file
    ftp.retrbinary("RETR {}".format(file), download_file.write)  # get the file from FTP and write it as virtual.
    download_file.seek(0)  # after writing go back to the start of the virtual file
    output = pd.read_excel(download_file)
    download_file.close()  # close virtual file

    ftp.quit()

    return output
