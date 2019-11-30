from requests_html import HTMLSession
import pandas as pd

def get_products(html):
    products_elements = html.find('.product-item')
    product_list = []

    for product in products_elements:
        title = product.attrs['data-title']
        price = product.attrs['data-price']
        brand = product.attrs['data-brand']
        product_list.append({
            title,
            brand,
            price,
        })

    return list(product_list)

def main():
    urls = [
        "https://tiki.vn/laptop/c8095"
    ]
    session = HTMLSession()
    response = session.get(urls[0], allow_redirects=True)

    products = get_products(response.html)

    df = pd.DataFrame.from_records(products, columns=['title', 'brand', 'price'])
    df.to_csv('tiki.csv', sep=',')

if __name__ == "__main__":
    main()