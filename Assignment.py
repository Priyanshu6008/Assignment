import requests
from bs4 import BeautifulSoup
import csv


# Function to scrape product data from the search page
def scrape_product_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    product_urls = []
    product_names = []
    product_prices = []
    ratings = []
    num_reviews = []

    # Find all the product listings on the page
    listings = soup.find_all('div', class_='sg-col-inner')

    # Extract the required data from each product listing
    for listing in listings:
        # Extract the product URL
        link = listing.find('a', class_='a-link-normal')
        if link:
            product_urls.append("https://www.amazon.in" + link['href'])

        # Extract the product name
        name = listing.find('span', class_='a-size-medium')
        if name:
            product_names.append(name.text)

        # Extract the product price
        price = listing.find('span', class_='a-offscreen')
        if price:
            product_prices.append(price.text)

        # Extract the rating
        rating = listing.find('span', class_='a-icon-alt')
        if rating:
            ratings.append(rating.text)

        # Extract the number of reviews
        reviews = listing.find('span', class_='a-size-base')
        if reviews:
            num_reviews.append(reviews.text)

    return product_urls, product_names, product_prices, ratings, num_reviews


# Function to fetch additional information from product URLs
def fetch_additional_info(urls):
    descriptions = []
    asins = []
    product_descriptions = []
    manufacturers = []

    for url in urls:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract the description
            description = soup.find('span', id='productTitle')
            if description:
                descriptions.append(description.text.strip())
            else:
                descriptions.append('')

            # Extract the ASIN
            asin = soup.find('th', string='ASIN')
            if asin:
                asins.append(asin.find_next_sibling('td').text.strip())
            else:
                asins.append('')

            # Extract the product description
            product_description = soup.find('div', id='productDescription')
            if product_description:
                product_descriptions.append(product_description.text.strip())
            else:
                product_descriptions.append('')

            # Extract the manufacturer
            manufacturer = soup.find('a', id='bylineInfo')
            if manufacturer:
                manufacturers.append(manufacturer.text.strip())
            else:
                manufacturers.append('')
        except:
            # Handle exceptions when fetching data from a product URL
            descriptions.append('')
            asins.append('')
            product_descriptions.append('')
            manufacturers.append('')

    return descriptions, asins, product_descriptions, manufacturers


# Define the base URL and parameters
base_url = 'https://www.amazon.in/s'
params = {
    'k': 'bags',
    'crid': '2M096C61O4MLT',
    'qid': '1653308124',
    'sprefix': 'ba,aps,283',
    'ref': 'sr_pg_'
}

# Define the number of pages to scrape
num_pages = 20

# Scrape product data from each page
product_urls_all = []
product_names_all = []
product_prices_all = []
ratings_all = []
num_reviews_all = []

for page in range(1, num_pages + 1):
    params['ref'] = f'sr_pg_{page}'
    url = base_url + '?' + '&'.join([f'{key}={value}' for key, value in params.items()])
    product_urls, product_names, product_prices, ratings, num_reviews = scrape_product_data(url)

    product_urls_all.extend(product_urls)
    product_names_all.extend(product_names)
    product_prices_all.extend(product_prices)
    ratings_all.extend(ratings)
    num_reviews_all.extend(num_reviews)

# Fetch additional information from product URLs
additional_info = fetch_additional_info(product_urls_all[:200])

# Combine the scraped data and additional information
combined_data = list(zip(product_urls_all[:200], product_names_all[:200], product_prices_all[:200],
                         ratings_all[:200], num_reviews_all[:200], *additional_info))

# Write the data to a CSV file
with open('scraped_data.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Product URL', 'Product Name', 'Product Price', 'Rating', 'Number of Reviews',
                     'Description', 'ASIN', 'Product Description', 'Manufacturer'])
    writer.writerows(combined_data)

print('Data exported to scraped_data.csv file.')
