from requests_html import HTMLSession
import pandas as pd
import re

def get_products(html):
    products_elements = html.find('.product-item')
    product_list = list()

    for product in products_elements:
        title = product.attrs['data-title']
        price = product.attrs['data-price']
        brand = product.attrs['data-brand']
        product_list.append({
            'title': title,
            'brand': brand,
            'price': price,
        })

    return list(product_list)

def main():
    url = "https://tiki.vn/laptop/c8095"
    session = HTMLSession()
    products = list()
    page = 1
    total = 1

    while True:
        response = session.get(url, params={'page': page}, allow_redirects=True)
        if not response.ok:
            break;

        total_text = response.html.find('.product-box [name=results-count]', first=True).text
        total_text_number = re.findall(r'\d+', total_text)
        if (len(total_text_number)):
            total = int(total_text_number[0])

        products += get_products(response.html)
        print(f"Crawled page {page}")
        page += 1
        if (len(products) >= total):
            break;

    df = pd.DataFrame(products, columns=['title', 'brand', 'price'])
    df.to_csv('tiki_meta.csv', sep='\t')

if __name__ == "__main__":
    main()