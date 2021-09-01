import io
import os
from ftplib import *
from typing import Tuple

import pandas as pd
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


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


def get_data(competitor: str) -> Tuple[list, list]:
    """ Extracts the data from the ftp server
    It contains a table with our products with alternatives from the competitors

    :return: (1) List with the url's of the products of the competitor (2) List with our sku's
    """
    private_label_conc = load_ftp_excel(
        "private_label_omzet.xlsx", os.getenv("FTP_LINK"), os.getenv("USER"), os.getenv("PASSWD"), os.getenv("CWD")
    )
    df = private_label_conc[private_label_conc[competitor] != "geen alternatief"]
    df = df[df[competitor].notna()]
    product_urls = list(df[competitor])
    swnl = list(df["productcode_match"])

    return swnl, product_urls


def write_excel(filename: str, sheet_name: str, dataframe: pd.DataFrame):
    """
    Saves the alternatives with their marge_abs and a sheet that defines is a product is org or alternative.
    This excel file is used to create a dashboard in Tableau.

    :param filename: The name of the file you want to save the sheet on
    :param sheet_name: How you want to name the sheet
    :param dataframe: The dataframe you want to save
    """

    with pd.ExcelWriter(filename, engine="openpyxl", mode="a") as writer:
        dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
        writer.save()