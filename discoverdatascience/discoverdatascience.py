import collections
import csv
import logging

import bs4
import requests


def main():
    states = [
        'alabama', 'arizona', 'arkansas', 'california', 'colorado',
        'connecticut', 'delaware', 'district of columbia', 'florida',
        'georgia', 'hawaii', 'idaho', 'illinois', 'indiana', 'iowa', 'kansas',
        'kentucky', 'louisiana', 'maine', 'maryland', 'massachusetts',
        'michigan', 'minnesota', 'mississippi', 'missouri', 'montana',
        'nebraska', 'nevada', 'new hampshire', 'new jersey', 'new mexico',
        'new york', 'north carolina', 'north dakota', 'ohio', 'oklahoma',
        'oregon', 'pennsylvania', 'rhode island', 'south carolina',
        'south dakota', 'tennessee', 'texas', 'utah', 'vermont', 'virginia',
        'washington', 'west virginia', 'wisconsin'
    ]

    page_urls = {
        'ba': 'bachelors-in-data-science',
        'ma': 'masters-in-data-science',
        'phd': 'data-science-phd',
        'certificate': 'data-science-certification',
        'mba': 'mba-data-science'
    }

    site_url = 'https://www.discoverdatascience.org/programs/'

    logging.basicConfig(
        filename='scrape.log',
        level=logging.INFO,
        format='%(levelname)s:%(asctime)s:%(message)s',
    )
    logging.info('Beginning program.')

    degrees = []
    counter = collections.Counter()
    for degree_type, page_name in page_urls.items():
        url = f'{site_url}{page_name}/'
        logging.info(f'Beginning page: {url}')
        try:
            r = requests.get(url)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(e)
            logging.warning(f'Skipping page {url}')
            continue
        data = r.text
        soup = bs4.BeautifulSoup(data, 'html.parser')
        for p in soup.find_all('p'):
            info = [string for string in p.stripped_strings]
            if len(info) == 4 and info[0] != 'Program Length:' and p.a.get('href'):
                location = info[1][2:].strip()
                before, sep, after = location.partition(',')
                if after and after.lower().strip() in states:
                    state = after.strip()
                    city = before.strip()
                else:
                    city = location.strip()
                    state = None

                logging.debug(f'Beginning degree {info[2]}')

                degrees.append({
                    'institution': info[0],
                    'degree_name': info[2],
                    'degree_type': degree_type,
                    'city': city,
                    'state': state,
                    'url': p.a.get('href'),
                    'description': info[3]
                })
                counter.update({degree_type: 1})
        logging.info(f'Added {counter[degree_type]} degrees.')

    logging.info(f'Total degrees collected: {sum(counter.values())}')
    logging.info('Writing results to file')

    with open('scrape_results.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=degrees[0].keys())
        writer.writeheader()
        writer.writerows(degrees)

    logging.info('Program complete.')

if __name__ == '__main__':
    main()
