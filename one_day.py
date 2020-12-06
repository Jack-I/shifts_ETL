import pandas as pd
from datetime import datetime
from os.path import isdir, isfile
from os import mkdir
import logging

from s_m_upload_class import Upload


def set_full_path(date, type_):
    """
    Return full path for saving uploads, with year directory and filename
    Check if proper year directory exists. If not - creates it.
    :param date: date to save in string format 'YYYY-MM-DD'
    :param type_: type of loadout: 's' for shifts, 'm' for motivation
    :return: path for saving in string format
    """
    #logger = logging.getLogger(__name__)
    date = datetime.strptime(date, '%Y-%m-%d').date()  # str -> datetime.date
    access_rights = 0o755  # readable and accessible by all users, and write access by only the owner

    path = f'//bigshare/Выгрузки ТФ/Выгрузки смен и мотивации/{date.year}'
    if not isdir(path):  # if year_directory not exists
        try:
            mkdir(path, access_rights)  # create it
        except OSError:
            print(f"Creation of the directory '{path}' failed")
            logger.error(f"Creation of the directory '{path}' failed")
        else:
            logger.info(f"Successfully created the directory '{path}'")
    month = date.strftime('%m') + '_' + date.strftime('%B')  # month num + _ + monthname
    path += '/' + month
    if type_ == 'm':
        path += '_Motivations.xlsx'
    elif type_ == 's':
        path += '_Shifts.xlsx'
    else:
        raise ValueError('Unknown type for set_full_filename()!')
    return path


def save_df(df, cities_df, date, type_):
    df['date'] = pd.to_datetime(df.date, yearfirst=True)
    # map city ids to names
    df = df.merge(cities_df, how='left', left_on='city', right_on='id')
    df.drop(columns=['city', 'id'], inplace=True)
    df.rename(columns={'name': 'city'}, inplace=True)
    # set full path for saving
    m_fullpath = set_full_path(date, type_=type_)
    if isfile(m_fullpath):  # check if saving file already exists
        month_df = pd.read_excel(m_fullpath)
        month_df = pd.concat([month_df, df], ignore_index=True)
        # get rid of possible duplicates
        month_df = month_df.drop_duplicates().reset_index(drop=True)
        month_df.to_excel(m_fullpath, index=False)
    else:  # month file not exists
        df.to_excel(m_fullpath, index=False)


def load_one_day(date):
    logger = logging.getLogger(__name__)
    logger.info(f"Loading {date} started...")
    cities_df = pd.read_excel(r'\\bigshare\Выгрузки ТФ\Общая база qvd\ID городов.xlsx')
    motivation_obj = Upload('motivation', date)
    motivation_df = pd.DataFrame(motivation_obj.upload())
    save_df(df=motivation_df, cities_df=cities_df, date=date, type_='m')
    logger.info('Motivations saved')

    shifts_obj = Upload('shifts', date)
    shifts_df = pd.DataFrame(shifts_obj.upload())
    shifts_df['date'] = pd.to_datetime(shifts_df.date, yearfirst=True)
    save_df(df=shifts_df, cities_df=cities_df, date=date, type_='s')
    logger.info('Shifts saved')
    print(f"{date} loaded")

if __name__ == '__main__':
    logging.basicConfig(filename='s_m_test.log',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filemode='w',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)
    # manual debug load
    # load_one_day("2020-11-29")
    # manual month upload
    # for i in range(1, 30):
    #     print(f"2020-11-{i}")
    #     from time import sleep
    #     load_one_day(f"2020-11-{i}")
    #     sleep(60)