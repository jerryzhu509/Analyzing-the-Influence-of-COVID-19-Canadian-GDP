"""CSC110 Fall 2021 Project, Part 2: Reading data sets

Notes:
===============================
This program extracts the data for building GDP prediction model.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC110 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC110 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2021 Jerry Zhu, Jack Sun, Nicholas Au
"""
import csv
import datetime
from dataclasses import dataclass


@dataclass
class HorizontalDataPosition:
    """
    Position information of a horizontally-displayed data set.

    Representation Invariants:
    - start_column >= 0
    - date_start_rows >= 0
    - indicator_start_rows >= 0
    """
    start_column: int
    date_start_rows: int
    indicator_start_rows: int


@dataclass
class VerticalDataPosition:
    """
    Position information of a vertical-displayed data set.

    Representation Invariants:
    - start_rows >= 0
    - date_start_columns >= 0
    - indicator_start_columns >= 0
    """
    start_rows: int
    date_start_columns: int
    indicator_start_columns: int


def loading_data() -> dict[str, list[tuple]]:
    """
    Return the dictionary of data, including unemployment rate,
    balance of payment, population,composite index,exchange rate,
    bond yield, inflation rate,overnight rate from 2008 to 2021.
    """
    unemployment_rate_1 = change_month_to_quarter(
        load_horizontal_data('Unemployment_Rate.csv',
                             2007, HorizontalDataPosition(2, 12, 14), 'full_month'))
    unemployment_rate_2 = change_month_to_quarter(
        load_horizontal_data('Unemployment_Rate_2.csv',
                             2007, HorizontalDataPosition(3, 13, 28), 'full_month'))
    unemployment_rate = combine_data(unemployment_rate_1, unemployment_rate_2)
    balance_of_payment = load_horizontal_data('balance_of_payments.csv', 2007,
                                              HorizontalDataPosition(3, 10, 38), 'quarter')
    gdp = load_horizontal_data('GDP.csv', 2007, HorizontalDataPosition(2, 12, 43), 'quarter')
    population = load_horizontal_data('Population.csv', 2007,
                                      HorizontalDataPosition(2, 9, 11), 'quarter')
    composite_index = change_month_to_quarter(
        load_horizontal_data('S_PTSX_Composite_Index.csv', 2007,
                             HorizontalDataPosition(2, 10, 14), 'full_month'))
    exchange_rate = change_month_to_quarter(
        reverse_data_order(load_vertical_data('USD_CAD_Exchange_Rate.csv',
                                              2007, VerticalDataPosition(2, 1, 2), 'short_month')))
    bond_yield = change_month_to_quarter(
        change_day_to_month(
            load_vertical_data('10-Year_Canadian_Government_Bond_Yield.csv',
                               2007, VerticalDataPosition(25, 1, 6), 'yyyymmdd')))
    inflation_rate = change_month_to_quarter(
        change_day_to_month(load_vertical_data('Inflation_Rate.csv',
                                               2007, VerticalDataPosition(12, 1, 2), 'yyyymmdd')))
    overnight_rate_1 = reverse_data_order(
        load_vertical_data('Bank_of_Canada_Overnight_Rate.csv',
                           2007, VerticalDataPosition(13, 1, 2), 'ddmmyyyy'))
    overnight_rate_2 = load_horizontal_data('Bank_of_Canada_Overnight_Rate_2.csv',
                                            2007, HorizontalDataPosition(2, 10, 12), 'mmddyyyy')
    overnight_rate = combine_data(overnight_rate_2, overnight_rate_1)
    overnight_rate = change_month_to_quarter(change_day_to_month(overnight_rate))

    return {'unemployment_rate': unemployment_rate,
            'balance_of_payment': balance_of_payment,
            'gdp': gdp,
            'population': population,
            'composite_index': composite_index,
            'exchange_rate': exchange_rate,
            'bond_yield': bond_yield,
            'inflation_rate': inflation_rate,
            'overnight_rate': overnight_rate}


def change_day_to_month(day_data: list[tuple[datetime.date, float]]) -> \
        list[tuple[datetime.date, float]]:
    """
    Return a list of tuples of the data in input file in which the date is from left to right.

    The first element of tuple contains the initial date of the month in datetime object,
    the second contains the average value of the corresponding indicator of that month.
    The second element of the tuple are rounded to the maximum number of decimal place
    that the input float has in the corresponding month.

    Preconditions:
    - datetime.date(2008, 1, 1) <= self.datetime.date <= datetime.date(2021, 6, 30)
    - [x[0] for x in day_data] == sorted([x[0] for x in day_data])

    >>> change_day_to_month([(datetime.date(2008,1,1), 5.0), (datetime.date(2008,1,2), 10.0),\
     (datetime.date(2008,1,30), 15.0), (datetime.date(2008,2,1), 20.0), \
     (datetime.date(2008, 3, 5), 25.0)])
    [(datetime.date(2008, 1, 1), 10.0), (datetime.date(2008, 2, 1), 20.0), (datetime.date(2008, 3, 1), 25.0)]

    >>> change_day_to_month([(datetime.date(2008,1,1), 5.0), (datetime.date(2008,1,2), 10.0),\
     (datetime.date(2008,1,30), 15.0), (datetime.date(2008,2,1), 20.0), \
     (datetime.date(2008,2,2), 25.0)])
    [(datetime.date(2008, 1, 1), 10.0), (datetime.date(2008, 2, 1), 22.5)]
    """
    month_data = []
    month_processing = (day_data[0][0].year, day_data[0][0].month)
    accumulator = 0
    counter = 0
    max_digit = 0
    n = len(day_data)
    for one_data in day_data:

        # The values are accumulated whenever they are in the same month.
        if (one_data[0].year, one_data[0].month) == month_processing:
            accumulator += one_data[1]
            counter += 1
            if isinstance(one_data[1], float) and max_digit < len(str(one_data[1]).split(".")[1]):
                max_digit = len(str(one_data[1]).split(".")[1])

        # When there is a different month, it concludes values in the previous month, and
        # override some indicators.
        else:
            add_data = (
                datetime.date(month_processing[0], month_processing[1], 1),
                round(accumulator / counter, max_digit))
            month_data.append(add_data)
            month_processing = (one_data[0].year, one_data[0].month)
            accumulator = one_data[1]
            counter = 1
            max_digit = len(str(one_data[1]).split(".")[1])

        # The below if statement is to concludes the data of the final month.
        # I chose to put as a separate if statement instead of putting it as another condition
        # for the first if statement, is to tackle the situation suggested in doctest 1.
        if one_data == day_data[n - 1]:
            add_data = (
                datetime.date(month_processing[0], month_processing[1], 1),
                round(accumulator / counter, max_digit))
            month_data.append(add_data)
    return month_data


def change_month_to_quarter(month_data: list[tuple[datetime.date, float]]) \
        -> list[tuple[datetime.date, float]]:
    """
    Return a list of tuples of the data in input file in which the date is from left to right.

    The first element of tuple contains the initial date of the quarter in datetime object,
    the second contains the average value of the corresponding indicator of that quarter.
    The second element of the tuple are rounded to the maximum number of decimal place
    that the input float has in the corresponding quarter.

    Preconditions:
    - all(datetime.date(2008, 1, 1) <= x[0] <= datetime.date(2021, 6, 30) for x in self.month_data)
    - [x[0] for x in self.month_data] == sorted([x[0] for x in self.month_data])
    - all(x[0].day == 1 for x in self.month_data)

     >>> change_month_to_quarter([(datetime.date(2008,1,1), 5.0), (datetime.date(2008,2,1), 10.0),\
     (datetime.date(2008,3,1), 15.0), (datetime.date(2008,4,1), 20.0), (datetime.date(2008, 5, 5)\
     , 25.0)])
     [(datetime.date(2008, 1, 1), 10.0), (datetime.date(2008, 4, 1), 22.5)]
    """
    quarter_data = []
    quarter_processing = (month_data[0][0].year, month_data[0][0].month)
    accumulator = 0
    counter = 0
    max_digit = 0
    for one_data in month_data:

        # The values are accumulated whenever they are in the same quarter.
        if one_data[0].year == quarter_processing[0] and \
                quarter_processing[1] <= one_data[0].month <= quarter_processing[1] + 2:
            accumulator += one_data[1]
            counter += 1
            if isinstance(one_data[1], float) and max_digit < len(str(one_data[1]).split(".")[1]):
                max_digit = len(str(one_data[1]).split(".")[1])

        # When there is a different quarter, it concludes values in the previous quarter, and
        # override some indicators.
        else:
            add_data = (
                datetime.date(quarter_processing[0], quarter_processing[1], 1),
                round(accumulator / counter, max_digit))
            quarter_data.append(add_data)
            quarter_processing = (one_data[0].year, one_data[0].month)
            accumulator = one_data[1]
            counter = 1
            max_digit = len(str(one_data[1]).split(".")[1])

        # The below if statement is to concludes the data of the final quarter.
        # I chose to put as a separate if statement instead of putting it as another condition
        # for the first if statement, is to tackle the situation suggested in doctest 1.
        if one_data == month_data[len(month_data) - 1]:
            add_data = (
                datetime.date(quarter_processing[0], quarter_processing[1], 1),
                round(accumulator / counter, max_digit))
            quarter_data.append(add_data)
    return quarter_data


def reverse_data_order(day_data: list[tuple[datetime.date, float]]) \
        -> list[tuple[datetime.date, float]]:
    """
    Return a list of data with the order reversed.

    Preconditions:
    - day_data != []

    >>> reverse_data_order([(datetime.date(2008, 1, 1), 10.0), (datetime.date(2008, 4, 1), 22.5)])
    [(datetime.date(2008, 4, 1), 22.5), (datetime.date(2008, 1, 1), 10.0)]
    """
    new_list = []
    for i in range(len(day_data), 0, -1):
        new_list.append(day_data[i - 1])
    return new_list


def combine_data(data_1: list[tuple], data_2: list[tuple]) -> list:
    """
    Return a concatenated list of two list of data.

    Preconditions:
    - data_1 != [] and data_2 != []
    >>> combine_data([(datetime.date(2008, 1, 1), 10.0)], [(datetime.date(2008, 4, 1), 22.5)])
    [(datetime.date(2008, 1, 1), 10.0), (datetime.date(2008, 4, 1), 22.5)]
    """
    return data_1 + data_2


def load_vertical_data(filename: str, after_year: int, position: VerticalDataPosition,
                       date_format: str) -> list[tuple[datetime.date, float]]:
    """Return a list of tuples based on the data in input file in which the date is from up to down.
    The first element of tuple contains date in datetime object,
    the second contains the corresponding indicator on that day.
    Only the data after or in 2012 will be returned.
    """
    data = []

    with open(filename, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        for _ in range(position.start_rows - 1):
            next(reader)  # skip the header

        for row in reader:
            if row:
                time = transform_to_datetime(row[position.date_start_columns - 1], date_format)
                indicator = row[position.indicator_start_columns - 1].replace(',', '')
                if indicator != ' Bank holiday':
                    t = time, float(indicator)
                    load_after_date(data, t, after_year)
    return data


def load_horizontal_data(filename: str, after_year: int, position: HorizontalDataPosition,
                         date_format: str) \
        -> list[tuple[datetime.date, float]]:
    """Return a list of tuples of the data in input file in which the date is from left to right.
    The first element of tuple contains date in datetime object,
    the second contains the corresponding indicator on that day.
    Only the data after or in 2012 will be returned.
    """

    with open(filename, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        total_lst = list(reader)
        date_lst = \
            total_lst[position.date_start_rows - 1][position.start_column - 1:]
        indicator_lst = \
            total_lst[position.indicator_start_rows - 1][position.start_column - 1:]
        new_date_lst = [transform_to_datetime(date, date_format) for date in date_lst]
        data = []
        for i in range(len(new_date_lst)):
            if indicator_lst[i].replace(',', '') != '..':
                t = new_date_lst[i], float(indicator_lst[i].replace(',', ''))
                load_after_date(data, t, after_year)
        return data


def load_after_date(data_list: list, data: tuple[datetime.date, float], after_year: int) -> None:
    """
    Append the data to the data_list if the year of data is after the specifc year
    and before 2021.

    Preconditions:
    - data_list != []
    - data != []
    """
    if data[0].year > after_year and (data[0].year != 2021 or data[0].month < 7):
        data_list.append(data)


def transform_to_datetime(date: str, date_format: str) -> datetime.date:
    """Return datetime object of the input date with known format.

    Preconditions:
    - date_format in {'mmddyyyy', 'yyyymmdd', 'ddmmyyyy', 'quarter', 'full_month', 'short_month'}
    - date variable is a valid date representation.

    >>> transform_to_datetime('29/11/2021', 'ddmmyyyy')
    datetime.date(2021, 11, 29)
    """
    new_date = datetime.date(2021, 11, 29)
    if date_format == 'mmddyyyy':
        new_date = mmddyyyy_to_datetime(date)
    if date_format == 'yyyymmdd':
        new_date = yyyymmdd_to_datetime(date)
    if date_format == 'ddmmyyyy':
        new_date = ddmmyyyy_to_datetime(date)
    if date_format == 'quarter':
        new_date = quarter_to_datetime(date)
    if date_format == 'full_month':
        new_date = full_month_to_datetime(date)
    if date_format == 'short_month':
        new_date = short_month_to_datetime(date)
    return new_date


def full_month_to_datetime(date: str) -> datetime.date:
    """Return datetime object of the input date in month-year format,
    where the month is not abbreviated.

    The month in input is treated as its start date. For example, January 2021 starts
    on January 1st, 2021, so the function outputs datetime.date(2021, 1, 1).

    Preconditions:
    - date variable is a valid date representation

    >>> full_month_to_datetime('January 2021')
    datetime.date(2021, 1, 1)
    """
    month_in_full = {'January': 1, 'February': 2, 'March': 3,
                     'April': 4, 'May': 5, 'June': 6,
                     'July': 7, 'August': 8, 'September': 9, 'October': 10,
                     'November': 11, 'December': 12}
    lst = date.split(' ')
    return datetime.date(int(lst[1]), month_in_full[lst[0]], 1)


def short_month_to_datetime(date: str) -> datetime.date:
    """Return datetime object of the input date in month-year format,
    where the month is abbreviated.

    The month in input is treated as its start date. For example, Jan 2021 starts
    on Jan 1st, 2021, so the function outputs datetime.date(2021, 1, 1).

    Preconditions:
    - date variable is a valid date representation

    >>> short_month_to_datetime('Jan 21')
    datetime.date(2021, 1, 1)
    """
    lst = date.split(' ')
    month_in_short = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                      'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
    return datetime.date(2000 + int(lst[1]), month_in_short[lst[0]], 1)


def mmddyyyy_to_datetime(date: str) -> datetime.date:
    """Return datetime object of the input date in mmddyyyy format

    Preconditions:
    - date variable is a valid date representation

    >>> mmddyyyy_to_datetime('January 1, 2008')
    datetime.date(2008, 1, 1)
    """
    month_in_full = {'January': 1, 'February': 2, 'March': 3,
                     'April': 4, 'May': 5, 'June': 6,
                     'July': 7, 'August': 8, 'September': 9, 'October': 10,
                     'November': 11, 'December': 12}
    date = date.replace(',', '')
    lst = date.split(' ')
    return datetime.date(int(lst[2]), month_in_full[lst[0]], int(lst[1]))


def yyyymmdd_to_datetime(date: str) -> datetime.date:
    """Return datetime object of the input date in yyyy-mm-dd format

    Preconditions:
    - date variable is a valid date representation

    >>> yyyymmdd_to_datetime('2021-11-29')
    datetime.date(2021, 11, 29)
    """

    lst = date.split('-')
    return datetime.date(int(lst[0]), int(lst[1]), int(lst[2]))


def ddmmyyyy_to_datetime(date: str) -> datetime.date:
    """Return datetime object of the input date in dd/mm/yyyy format

    Preconditions:
    - date variable is a valid date representation

    >>> ddmmyyyy_to_datetime('29/11/2021')
    datetime.date(2021, 11, 29)
    """
    lst = date.split('/')
    return datetime.date(int(lst[2]), int(lst[1]), int(lst[0]))


def quarter_to_datetime(date: str) -> datetime.date:
    """Return datetime object of the input date in quarter-year format

    The quarter in input is treated as its start date. For example, Q1 2021 starts
    on January 1st, 2021, so the function outputs datetime.date(2021, 1, 1).

    Preconditions:
    - date variable is a valid date representation

    >>> quarter_to_datetime('Q4 2021')
    datetime.date(2021, 10, 1)
    """
    quarter = {'Q1': 1, 'Q2': 4, 'Q3': 7, 'Q4': 10}
    lst = date.split(' ')
    return datetime.date(int(lst[1]), quarter[lst[0]], 1)


if __name__ == '__main__':
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    # Leave this code uncommented when you submit your files.
    import python_ta

    python_ta.check_all(config={
        'allowed-io': ['load_horizontal_data', 'load_vertical_data'],
        'extra-imports': ['csv', 'datetime'],
        'max-line-length': 110,
        'disable': ['R1705', 'C0200']
    })
#
#     import doctest
#
#     doctest.testmod()
