import csv

import requests

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json',
    'Origin': 'https://online.metro-cc.ru',
    'Accept-Language': 'ru',
    'Host': 'api.metro-cc.ru',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 '
                  'YaBrowser/24.1.0.0 Safari/537.36',
    'Referer': 'https://online.metro-cc.ru/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

category_slug = "vino"
product_number = 1000
shops_response = requests.get(
    "https://api.metro-cc.ru/api/v1/C98BB1B547ECCC17D8AEBEC7116D6/tradecenters"
)
shops = shops_response.json()['data']
shops_id = []

for shop in shops:
    store_id = shop.get('store_id')
    city = shop.get('city')
    if city in ('Москва', 'Санкт-Петербург'):
        shops_id.append(store_id)


def parse_metro_shop(shop_id):
    data = (
        f'{{"query":"\\n query Query($storeId: Int!, $slug: String!, '
        f'$attributes:[AttributeFilter], $filters: [FieldFilter], '
        f'$from: Int!, $size: Int!, $sort: InCategorySort, $in_stock: Boolean,'
        f' $eshop_order: Boolean, $is_action: Boolean, $price_levels: Boolean)'
        f' {{\\n category (storeId: $storeId, slug: $slug, inStock: $in_stock,'
        f' eshopAvailability: $eshop_order, isPromo: $is_action,'
        f' priceLevels: $price_levels) {{\\n id\\n name\\n slug\\n id\\n '
        f'parent_id\\n# treeBranch {{\\n# id\\n# name\\n# slug\\n# children '
        f'{{\\n# category_type\\n# id\\n# name\\n# slug\\n# children {{\\n# '
        f'category_type\\n# id\\n# name\\n# slug\\n# children {{\\n# '
        f'category_type\\n# id\\n# name\\n# slug\\n# children {{\\n# '
        f'category_type\\n# id\\n# name\\n# slug\\n# }}\\n# }}\\n# }}\\n# }}'
        f'\\n# }}\\n products(attributeFilters: $attributes, from: $from, '
        f'size: $size, sort: $sort, fieldFilters: $filters) {{\\n id\\n'
        f' slug\\n name\\n name_highlight\\n article\\n main_article\\n '
        f'main_article_slug\\n is_target\\n category_id\\n url\\n images\\n '
        f'pick_up\\n rating\\n manufacturer {{\\n id\\n image\\n name\\n }}'
        f'\\n packing {{\\n size\\n type\\n pack_factors {{\\n instamart\\n }}'
        f'\\n }}\\n stocks {{\\n value\\n text\\n eshop_availability\\n '
        f'scale\\n prices_per_unit {{\\n old_price\\n price\\n is_promo\\n '
        f'discount\\n }}\\n }}\\n }}\\n }}\\n }}\\n",'
        f'"variables":{{"storeId":{shop_id},'
        f'"sort":"default","size":{product_number},'
        f'"from":0,"filters":[{{"field":"main_article","value":"0"}}],'
        f'"attributes":[],"in_stock":true,"eshop_order":false,'
        f'"allStocks":false,"slug":"{category_slug}"}}}}'
    )

    response = requests.post(
        'https://api.metro-cc.ru/products-api/graph',
        headers=headers,
        data=data
    )
    products = response.json()['data']['category']['products']
    product_data = []

    for product in products:
        product_id = product.get('id')
        name = product.get('name')
        url = product.get('url')
        price = product.get('stocks')[0]['prices_per_unit']
        is_promo = product.get('stocks')[0]['prices_per_unit']['is_promo']
        if is_promo:
            regular_price = price.get('old_price')
        else:
            regular_price = price.get('price')
        promo_price = price.get('price')
        brand = product.get('manufacturer')['name']
        product_data.append({
            'id': product_id,
            'name': name,
            'url': url,
            'regular_price': regular_price,
            'promo_price': promo_price,
            'brand': brand
        })
    return product_data


metro_data = []
for num in shops_id:
    metro_data += parse_metro_shop(num)

with open('metro_data.csv', mode='w', encoding='utf-8', newline='') as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            'id', 'name', 'url', 'regular_price', 'promo_price', 'brand'
        ]
    )
    writer.writeheader()
    for product in metro_data:
        writer.writerow(product)
