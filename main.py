
import os
import requests
import re
import csv
import traceback

#---------------------------FUNKCIJE------------------------------------------------------------------------------------------------------------
#---------------------------FUNKCIJE------------------------------------------------------------------------------------------------------------
#---------------------------FUNKCIJE------------------------------------------------------------------------------------------------------------
#---------------------------FUNKCIJE------------------------------------------------------------------------------------------------------------
#---------------------------FUNKCIJE------------------------------------------------------------------------------------------------------------
#Komenatrji kode so v main (na dnu).



def download_url_to_string(url):
    """Funkcija kot argument sprejme niz in poskusi vrniti vsebino te spletne
    strani kot niz. V primeru, da med izvajanje pride do napake vrne None.
    """
    try:
        # del kode, ki morda sproži napako
        page_content = requests.get(url)
        if page_content.status_code == 200:
            return page_content.text
        else:
            raise ValueError(f"Čudna koda: {page_content.status_code}")
    except Exception:
        # koda, ki se izvede pri napaki
        # dovolj je če izpišemo opozorilo in prekinemo izvajanje funkcije
        print(f"Prišlo je do spodnje napake:\n{traceback.format_exc()}")



def create_all_links(frontpage_string):
    incomplete_subURLs = re.findall(r'<a[^>]*>(.*?)</a>', frontpage_string)
    all_subURLs = [frontpage_url + incomplete_subURL for incomplete_subURL in incomplete_subURLs]

    start_date = '20220101.html'
    end_date = '20230101.html'
    start_index = None
    end_index = None

    for i, link in enumerate(all_subURLs):
        if start_date in link:
            start_index = i
        if end_date in link:
            end_index = i
            break

    if start_index is not None:
        filtered_subURLs = all_subURLs[start_index:end_index]

    return filtered_subURLs


def save_string_to_file(text, directory, filename):
    """Funkcija zapiše vrednost parametra "text" v novo ustvarjeno datoteko
    locirano v "directory"/"filename", ali povozi obstoječo. V primeru, da je
    niz "directory" prazen datoteko ustvari v trenutni mapi.
    """
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as file_out:
        file_out.write(text)
    return None


def table_from_page(subpage_url):
    subpage_string = download_url_to_string(subpage_url)
    table_pattern = re.compile(r'<table\b[^>]*>(.*?)</table>', re.DOTALL)
    match = table_pattern.search(subpage_string)
    
    if match:
        table_content = match.group(1)
        return table_content
    return "no table"

def header_from_table(table_content):
    header_match = re.search(r'<thead[^>]*>(.*?)</thead>', table_content, re.DOTALL)
    if header_match:
        header = header_match.group(1)
        return header
    else:
        return "Header not found in table content"
    
def check_required_countries(subpage_url):
    table = table_from_page(subpage_url)
    header = header_from_table(table)
    for country in required_countries:
        if country not in header:
            return False
    return True


def body_from_table(table_content):
    tbody_match = re.search(r'<tbody[^>]*>(.*?)</tbody>', table_content, re.DOTALL)
    if tbody_match:
        header = tbody_match.group(1)
        return header 
    else:
        return "Body not found in table content"
    
def extract_entries_from_body(tbody):
    entries = []

    tr_matches = re.findall(r'<tr[^>]*>(.*?)</tr>', tbody, re.DOTALL)
    for tr_match in tr_matches:
        td_matches = re.findall(r'<td[^>]*>(.*?)</td>', tr_match)
        entry = [td.strip() for td in td_matches]
        entries.append(entry)
    
    return entries

def extract_entries_from_header(theader):
    entries = re.findall(r'<th[^>]*>([^<]+)</th>', theader)

    return entries

def create_output_entry(entry, header, subpage_url):
    out_array = []
    
    positions = ['Pos', 'Artist and Title', 'Days', 'Pk', '(x?)'] + required_countries
    year, month, day = extract_date_from_link(subpage_url)
    for pos in positions:
        index = header.index(pos)
        out_array.append(entry[index])

    out_array = [str(year), str(month), str(day)] + out_array

    out_array[4] = re.sub(r'<div>(.*?)</div>', r'\1', out_array[4])
    out_array[6] = re.sub(r'<b>(.*?)</b>', r'\1', out_array[6])

    artist, title = out_array[4].split(' - ', 1)

    out_array[4] = artist
    out_array.insert(4, title)

    x_value = out_array[8]
    x_number = re.search(r'\(x(\d+)\)', x_value)

    if x_number:
        extracted_number = x_number.group(1)
        out_array[8] = extracted_number
        
    return out_array

def extract_date_from_link(link):
    date_match = re.search(r'(\d{4})(\d{2})(\d{2})\.html', link)
    if date_match:
        year, month, day = date_match.groups()
        return int(year), int(month), int(day)
    else:
        return None

#---------------------------FUNKCIJE------------------------------------------------------------------------------------------------------------
#---------------------------FUNKCIJE------------------------------------------------------------------------------------------------------------
#---------------------------FUNKCIJE------------------------------------------------------------------------------------------------------------
#---------------------------FUNKCIJE------------------------------------------------------------------------------------------------------------
#---------------------------FUNKCIJE------------------------------------------------------------------------------------------------------------



#---------------------------MAIN------------------------------------------------------------------------------------------------------------
#---------------------------MAIN------------------------------------------------------------------------------------------------------------
#---------------------------MAIN------------------------------------------------------------------------------------------------------------
#---------------------------MAIN------------------------------------------------------------------------------------------------------------
#---------------------------MAIN------------------------------------------------------------------------------------------------------------

csv_file_path = 'output.csv'

with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)

        # zapišem header row
        header_csv = ['Year', 'Month', 'Day', 'Position', 'Title', 'Artist', 'Days On Chart', 'Peak Chart Poistion', 'Days At PCP', 'US', 'UK', 'AU', 'DE', 'FR', 'RU', 'JP', 'ES', 'CZ', 'PL', 'SI', 'AT', 'CR', 'HU', 'IT']
        csv_writer.writerow(header_csv)

# Zaradi ne konstantnih podatkov o držav sem se odločil, da bom vzel
# podatke od samo določenih držav za katere se mi zdijo relevantne
required_countries = ['US', 'UK', 'AU', 'DE', 'FR', 'RU', 'JP', 'ES', 'CZ', 'PL', 'SI', 'AT', 'CR', 'HU', 'IT']

# najprej vsebino glavne spletne strani sharnim v string
frontpage_url = 'https://kworb.net/ww/archive/'
frontpage_string = download_url_to_string(frontpage_url)

#to bo glavni array v katerega bom shranil vsako vrstico s podatki
entries = []

#glavna stran je index na kateri je pod stran na kateri so objavljeni podatki za tisti dan
# ta funkcija vzame vse href iz glavne strani (frontpage) in jih pretvori direktno v linke 
# do posamezne podstrani
subpage_URLs_array = create_all_links(frontpage_string)

#zdaj moram narediti loop, ki bo šel skozi vse podstrani v zgornjem array-ju... :
for subpage_URL in subpage_URLs_array:
    
    #najprej pregledam če ima stran kompatibilno tabelo
    #kompatibilna tabela je tabela, ki ima vse izmed "required countries"
    #v headerju
    if check_required_countries(subpage_URL) == False:
        continue

    #ko preverim, da je tabela vredu jo vzamem iz html-ja s
    #pomočjo regexa
    table = table_from_page(subpage_URL)
    
    #iz tabelce vzamem vn "grd" header in body v obliki htmlja, ki je ubistvu string (zato je grd)
    full_header = header_from_table(table)
    full_body = body_from_table(table)

    #iz grdih header, body zdaj filtriram samo podatke (tako bo zdaj vse v arrajih)
    header = extract_entries_from_header(full_header)
    body = extract_entries_from_body(full_body)

    #v body je zdaj več elementov (entries - arrajov) 
    #header je samo en array


    with open(csv_file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for entry in body:
            final_entry = create_output_entry(entry, header, subpage_URL)
            writer.writerow(final_entry)

    #loopam skozi vse body elemente in jih uredim v formatu ki želim:
    #[DATE, 'Pos', 'Title', 'Artist' 'Days', 'Pk', '(x?)'] + required_countries
    

#20160616.html

#---------------------------MAIN------------------------------------------------------------------------------------------------------------
#---------------------------MAIN------------------------------------------------------------------------------------------------------------
#---------------------------MAIN------------------------------------------------------------------------------------------------------------
#---------------------------MAIN------------------------------------------------------------------------------------------------------------
#---------------------------MAIN------------------------------------------------------------------------------------------------------------
