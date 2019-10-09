import csv
import os


class CSVWriter:
    def __init__(self, dir_path, fieldnames):
        self.__fieldnames = fieldnames
        self.__writer = csv.DictWriter
        try:
            self.__csv_file = open(dir_path + os.sep + 'output_data.csv', 'w', newline='')
        except IOError:
            print('Could not open csv file.')
        self.__writer = csv.DictWriter(self.__csv_file, fieldnames=fieldnames)
        self.__writer.writeheader()

    def add_to_csv(self, values_dict):
        self.__writer.writerow(values_dict)

    def get_fieldnames(self):
        return self.__fieldnames

    def close(self):
        self.__csv_file.close()
