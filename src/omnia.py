from ftplib import FTP
from xml.etree.ElementTree import parse
import pandas as pd
import io


# This one is to get Omnia data from an XML form to a dataframe
def parse_xml(xml_file, df_cols):
    """
    Parse the input XML file and store the result in a pandas
    DataFrame with the given columns.

    The first element of df_cols is supposed to be the identifier
    variable, which is an attribute of each node element in the
    XML data; other features will be parsed from the text content
    of each sub-element.
    """

    xtree = parse(xml_file)
    xroot = xtree.getroot()
    rows = []

    for node in xroot:
        res = [node.attrib.get(df_cols[0])]
        for el in df_cols[1:]:
            if node is not None and node.find(el) is not None:
                res.append(node.find(el).text)
            else:
                res.append(None)
        rows.append({df_cols[i]: res[i]
                     for i, _ in enumerate(df_cols)})

    out_df = pd.DataFrame(rows, columns=df_cols)

    return out_df


def omnia_feed_df(columns: dict, ftp_link, user, passwd, cwd="feeds"):
    """
    Get the xml of omnia feed per site and make a pandas dataframe from
    by giving 1) a dict of all need site and the names of the xml elements,
    2) the ftp_url and its credentials and where sub-folder name where the
    xml located

    This func returns a df of omnia xml feeds

    :param columns: List with the columns for the dataframe
    :param ftp_link: The link of the ftp server
    :param user: The username of the ftp server
    :param passwd: The password of the ftp server
    :param cwd: The path of the ftp server
    :return: (1) Dict containing all the siteviews with their products and info, (2) SWNL with their products and
    info, (3) prod_dict is created, containing the admin ids of the products
    """
    pd.set_option("float_format", "{:f}".format)
    all_df = {}

    for site in columns:
        ftp = FTP(ftp_link)  # connect to host, default port
        ftp.login(user=user, passwd=passwd)  # credentials for Omnia FTP
        ftp.cwd(cwd)  # open needed folder
        filenames = ftp.nlst()  # get filenames within the directory

        site_file = [f for f in filenames if site in f][0]  # get file that has sitename

        # download the file but first create a virtual file object for it
        download_file = io.BytesIO()  # open virtual file
        ftp.retrbinary("RETR {}".format(site_file),
                       download_file.write)  # get the file from FTP and write it as virtual.
        download_file.seek(0)  # after writing go back to the start of the virtual file
        omnia_feed = parse_xml(download_file,
                               columns[site]).drop("ONE_STEP", axis=1)  # read virtual file into pandas
        download_file.close()  # close virtual file
        all_df[site] = omnia_feed
        ftp.quit()

    return all_df


swnl_columns = {"swnl": ["ONE_STEP", "id", "productCode", "sku", "ean", "productName", "brand", "serie",
                         "topLevelCategory", "midLevelCategory", "LowLevelCategory", "productType", "mpn",
                         "identifierExists", "deepLink", "condition", "dateAdded", "firstActivationDate", "obsolete",
                         "obsoleteDate", "shippingMethod", "availability", "availability_date", "showroom_ros",
                         "showroom_ams", "showroom_rot", "showroom_arn", "showroom_alk", "showroom_til", "showroom_bre",
                         "sellingPrice", "shippingCosts", "logisticalCosts", "purchasePrice", "purchasePriceAll",
                         "vat", "marketingCost", "supplierBonus", "inOffer", "sale_price", "amountInStock",
                         "deliveryTime", "unitsSoldTotalYesterday", "unitsSoldTotalLastWeek",
                         "unitsSoldOnlineYesterday", "unitsSoldOnlineLastWeek", "supplier", "dropshipping",
                         "localStock", "localStockCentralWarehouse", "supplierStock", "description", "color",
                         "material", "size", "imageUrl", "imageUrl2", "imageUrl3", "imageUrl4", "imageUrl5"]}


def main():

    all_df = omnia_feed_df(columns=swnl_columns, ftp_link='ftp.production.rorix.nl',
                           user='omnia', passwd='c4KZEs+gs-J9@UYX')

    all_df["swnl"]["sku"] = all_df["swnl"]["sku"].str.upper()
    omnia = all_df["swnl"][["sku", "sellingPrice", "deliveryTime", "topLevelCategory", "midLevelCategory",
                            "LowLevelCategory", "productType"]]
    omnia = omnia.rename(columns={"sellingPrice": "prijs_swnl", "deliveryTime": "levertijd_swnl"})

    return omnia


if __name__ == "__main__":
    main()
