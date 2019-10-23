import csv
import logging
import bs4
import requests
from states import state_list


def main():

    logging.basicConfig(
        filename='mastersindatascience/scrape.log',
        level=logging.INFO,
        format='%(levelname)s:%(asctime)s:%(message)s',
    )
    
    logging.info('Beginning program.')

    degrees = []

    for state in state_list:
        
        logging.info(f'Beginning state: {state}')
        
        url = f'https://www.mastersindatascience.org/schools/{state}/'

        try:
            r = requests.get(url)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(e)
            logging.warning(f'Skipping state {state}')
            continue
        
        data = r.text
        soup = bs4.BeautifulSoup(data, 'html.parser')

        for d in soup.find_all(class_="schoolinfo"):

            logging.debug(f'Beginning degree {d.get("id")}')

            institution = d.find(class_='schoolname').string
            location = d.find(class_='citystate').string
            location = location.replace(f', {state.capitalize()}', '')
            degree_name = d.find(class_='schoolprogram').find('h4').find('a').string
            url = d.find(class_='schoolprogram').find('h4').find('a').get('href')
            
            degrees.append({
                'institution':institution,
                'location': location,
                'degree_name': degree_name,
                'url': url,
                'state': state
            })
    
    logging.info('Writing results to file')

    with open('mastersindatascience/scrape_results.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=degrees[0].keys())
        writer.writeheader()
        writer.writerows(degrees)

    logging.info('Program complete.')


if __name__ == '__main__':
    main()