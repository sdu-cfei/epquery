import requests
import sys


def get_idd(ver, save_path):
    """
    Download IDD from EnergyPlus repository and save to a file.

    :param int ver: EnergyPlus version (only major release number)
    :param str save_path: Destination path including .idd extension
    :return: None
    """
    idd = requests.get("https://raw.githubusercontent.com/NREL/EnergyPlus/develop/idd/V{}-0-0-Energy%2B.idd"\
        .format(ver))

    if sys.version_info[0] >= 3:
        with open(save_path, 'wb') as f:
            f.write(idd.content)
    else:
        with open(save_path, 'w') as f:
            f.write(str(idd.text.encode('utf8')))


def get_test_idf(name, ver, save_path):
    """
    Download test IDF from EnergyPlus repository and save to a file.

    :param str name: Model name excluding .idf extension
    :param str ver: EnergyPlus full version, e.g. '8.8.0'
    :param str save_path: Destination path including .idf extension
    :return: None
    """
    idf = requests.get("https://raw.githubusercontent.com/NREL/EnergyPlus/v{}/testfiles/{}.idf".format(ver, name))

    if sys.version_info[0] >= 3:
        with open(save_path, 'wb') as f:
            f.write(idf.content)
    else:
        with open(save_path, 'w') as f:
            f.write(str(idf.text.encode('utf8')))
