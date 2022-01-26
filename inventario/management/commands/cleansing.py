from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import os
import csv
import json

from django.db import close_old_connections


def get_tables(file: str = 'tables.json') -> dict:
    """ Get the list list of the tables availables to compare,
        and some metadata to do the comparison
    """

    with open(file, encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data

def wrong_words(table, cols, wildcard):
    words = set()

    path = os.path.join(settings.BASE_DIR, 'CSV', f'{table}.csv')

    with open(path, 'r', encoding="ISO-8859-1") as csv_file:
        print(f'[{table}] Reading csv...')
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            for col in cols:
                for word in row[col].split():
                    if wildcard in word:
                        words.add(word.replace(',', '').replace('.', ''))
        return words

class Command(BaseCommand):
    help = 'Gather words with weird characters and replaces with a dictionary'

    def handle(self, *args, **options):
        repl = 'ï¿½'
        meta = get_tables('tables.json')
        tables = list(meta.keys())
        words = set()

        #tables = ['CAT_AREAC']

        for table in tables:
            if meta[table]['encoded'] != []:
                subset = wrong_words(table, meta[table]['encoded'], repl)
                words = words.union(subset)
            
        with open("words.csv", 'w', encoding="ISO-8859-1") as f2:
            for word in words:
                f2.write(word)
                f2.write(',')
                f2.write(word.replace('iï¿½n', 'ión').replace(repl, '$'))
                f2.write('\n')