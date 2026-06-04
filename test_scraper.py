import sys
import os

from servicios.scraper import ScraperPrecios

def test_scraping():
    urls = [
        "https://articulo.mercadolibre.com.ar/MLA-933391789-pasta-termica-arctic-mx-4-4g-_JM",
        "https://www.compragamer.com/producto/Memoria_Kingston_DDR4_8GB_3200MHz_Fury_Beast_12040",
        "https://www.fullh4rd.com.ar/prod/26815/fuente-gigabyte-650w-80-plus-bronze-p650b"
    ]
    
    for url in urls:
        print(f"Testing URL: {url}")
        precio, matched_url = ScraperPrecios.obtener_precio_en_vivo(url, precio_catalogo=1000)
        print(f"Precio obtenido: {precio} | URL final: {matched_url}\n")

if __name__ == '__main__':
    test_scraping()
