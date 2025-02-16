import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import pytz

# Function to scrape APOD data from the given URL
def scrape_apod(url):
    response = requests.get(url)
    response.encoding = 'ISO-8859-1'
    soup = BeautifulSoup(response.text, 'html.parser')

    data = []
    # For English page
    archive_section = soup.find('body').find_all('b')[1]
    if archive_section:
        # Split the content by <br> tags
        lines = str(archive_section).split('\n')
        print(lines)
        for line in lines:
            text = BeautifulSoup(line, 'html.parser').get_text().strip()
            if ': ' in text:
                date_str, title = text.split(': ', 1)
                try:
                    date = datetime.strptime(date_str, '%Y %B %d')  # Parse date in '2001 July 01' format
                except ValueError as e:
                    try:
                        date = datetime.strptime(date_str, '%B %d %Y')
                    except ValueError as e:
                        print(f"Error parsing date '{date_str}': {e}")
                        continue
                data.append((date, title))
    else:
        print("Error: <b> tag not found")

    return data

# Function to save data to SQLite database
def save_to_sqlite(data, table_name, db_name='apod_archive.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            title TEXT NOT NULL
        )
    ''')

    cursor.executemany(f'''
        INSERT INTO {table_name} (date, title) VALUES (?, ?)
    ''', data)

    conn.commit()
    conn.close()
    print(f"Data saved to table {table_name}")

# URL
english_url = 'https://apod.nasa.gov/apod/archivepixFull.html'

# Scrape data
print("Scraping English data...")
english_data = scrape_apod(english_url)
print(f"English data extracted: {len(english_data)} records")
print(english_data[:5])  # Print first 5 records for debugging

# Save to SQLite
print("Saving English data to SQLite...")
save_to_sqlite(english_data, 'apod_english')

print('Data has been successfully scraped and saved to SQLite database.')
