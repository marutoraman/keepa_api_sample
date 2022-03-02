from crawl.keepa import *


def test_fetch_products():
    keepa = KeepaAPI()
    response = keepa.fetch_products(
        asins=[
            "B07ZCSDPD3",
            "B01BEPNPF6",
            "B07RWWZT8J"
        ]
    )
    print(response)
    
    assert len(response) == 3
    assert response[0].title 
    assert response[0].price 
    

def test_fetch_products_by_jan():
    keepa = KeepaAPI()
    response = keepa.fetch_products(
        jan_codes= [
            "4953759010027",
            "4901987254256",
            "4580543940866"
        ]
    )
    print(response)
    
    assert len(response) == 3
    assert response[0].title 
    assert response[0].price 
    
    
def test_fetch_best_seller():
    keepa = KeepaAPI()
    response = keepa.fetch_best_seller_product_asins("71588051")
    print(response)
    
    assert response
    
    
def test_token_status():
    keepa = KeepaAPI()
    res = keepa.get_tokens_left()
    print(res)