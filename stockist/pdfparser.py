import pandas as pd
import numpy as np
import pdfplumber
import re
import zipfile
import os


def unzipper(zip):
    """
    unzips zipfile and stores content in tempfolder on same level directory.
    returns list of directories of pdf files in temp folder.
    ______
    takes in the zipfile.
    """
    path = 'data'
    with zipfile.ZipFile(zip, 'r') as zip_ref:
        zip_ref.extractall(path)

    files = os.listdir(path)
    dirs = [os.path.join(path, file) for file in files if file.endswith('.pdf') or file.endswith('.PDF')]

    return dirs

def pdf_parser(files):
    """
    Returns a df filled with buy and sell information of the input PDF files.
    ________
    Takes in files, a list of directories or bytes files (pdfplumber).
    """
    print('pdf_parser was called.')

    df = pd.DataFrame()
    for file in files:
        with pdfplumber.open(file) as pdf:
            pages = [page.extract_text() for page in pdf.pages]

        match = [p.start() for p in re.finditer('Nominale', pages[0])]
        trans = pages[0][match[0]:].split('\n')
        action = re.findall('Wertpapier Abrechnung (\w+)', pages[0])

        if action:
            # if 'Abrechnung' was found
            val = re.findall(r'Stück (\d+)', trans[1])[0]
            wkn = trans[1].replace(')', '').split('(')[1]
            date = re.findall(r'Datum (\d+.\d+.\d+)', pages[0])[0]

            # assemble df
            data = [val, wkn, date]
            columns = [action[0], 'WKN', 'Datum']


            # scan 2nd page
            if action[0] == 'Verkauf':
                buy = [p.start() for p in re.finditer('Ber\wcksichtigte Anschaffungsgesch\wfte', pages[1])][0]
    #             columns2 = columns + pages[1][buy:].split('\n')[1].split()
                columns2 = columns + ['Geschäft',
                                      'Auftragsnr.',
                                      'Ausführ.-tag',
                                      'Whr./St.',
                                      'Nennwert/Stück',
                                      'AS-Kosten',
                                      'Erlös', 'ant.Ergebnis',
                                      'Land']
                data2 = data + pages[1][buy:].split('\n')[2].split()
                try:
                    new_df = pd.DataFrame([data2], columns=columns2)
                except:
                    new_df = (pd.DataFrame([data], columns=columns))
                    print(f"couldn't process 2nd page of file: {file}")

            else:
                rate = re.findall(r'Ausf\whrungskurs(\d+,\d+)', pages[0])[0]
                data.append(rate)
                columns.append('Kurs')
                new_df = pd.DataFrame([data], columns=columns)


            df = pd.concat([df, new_df])

    return df
