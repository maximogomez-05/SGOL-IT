import requests
from bs4 import BeautifulSoup
import re
import random
from abc import ABC, abstractmethod

class ScraperInterface(ABC):
    """
    Interfaz base para todos los scrapers de precios.
    Fuerza a implementar el método obtener_precio.
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

    @abstractmethod
    def obtener_precio(self, url: str) -> float:
        """
        Extrae el precio del producto desde la URL.
        Retorna None si no se puede obtener.
        """
        pass

    def _realizar_peticion(self, url: str):
        """Método auxiliar protegido para hacer la petición HTTP."""
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            print(f"[SCRAPER] Error de conexión al scrapear {url}: {e}")
            return None

class MercadoLibreScraper(ScraperInterface):
    """Implementación específica para scrapear MercadoLibre."""
    
    def obtener_precio(self, url: str) -> float:
        html = self._realizar_peticion(url)
        if not html: return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Estrategia 1: Meta etiqueta (más seguro si está presente)
        meta_price = soup.find('meta', itemprop='price')
        if meta_price and meta_price.get('content'):
            try:
                return float(meta_price.get('content'))
            except ValueError:
                pass
                
        # Estrategia 2: Elemento visual HTML
        price_span = soup.find('span', class_='andes-money-amount')
        if price_span:
            fraction = price_span.find('span', class_='andes-money-amount__fraction')
            if fraction:
                try:
                    return float(fraction.text.strip().replace('.', '').replace(',', '.'))
                except ValueError:
                    pass
        return None

class CompraGamerScraper(ScraperInterface):
    """Implementación específica para scrapear Compra Gamer (SPA Angular)."""
    
    def obtener_precio(self, url: str) -> float:
        html = self._realizar_peticion(url)
        if not html: return None
        
        # CompraGamer carga dinámicamente mediante Angular/JS.
        # Buscamos patrones de precios en el texto base.
        json_price = re.findall(r'"price"\s*:\s*(\d+)', html)
        if json_price:
            return float(json_price[0])
            
        text_price = re.findall(r'(\d+)\s*Precio Especial', html)
        if text_price:
            return float(text_price[0])
            
        return None

class FullH4rdScraper(ScraperInterface):
    """Implementación específica para scrapear FullH4rd."""
    
    def obtener_precio(self, url: str) -> float:
        html = self._realizar_peticion(url)
        if not html: return None
        
        soup = BeautifulSoup(html, 'html.parser')
        # FullH4rd suele tener clases específicas para el precio (ej. price)
        price_div = soup.find('div', class_='price')
        if price_div:
            # extraemos números
            numeros = re.findall(r'[\d\.]+', price_div.text.replace('.', ''))
            if numeros:
                try:
                    return float(numeros[0])
                except ValueError:
                    pass
        
        # Fallback si cambia la clase, buscamos en un span de precio
        text_price = re.findall(r'\$\s*([\d\.]+)', html.replace('.', ''))
        if text_price:
            try:
                return float(text_price[0])
            except ValueError:
                pass
                
        return None

import urllib.parse

class DefaultFallbackScraper(ScraperInterface):
    """Scraper por defecto o de fallback si no se reconoce el dominio."""
    def obtener_precio(self, url: str) -> float:
        print(f"[SCRAPER] No hay scraper específico para el dominio de {url}.")
        return None

class HardGamersScraper(ScraperInterface):
    """Implementación específica para scrapear HardGamers (páginas de producto)."""
    def obtener_precio(self, url: str) -> float:
        html = self._realizar_peticion(url)
        if not html: return None
        soup = BeautifulSoup(html, 'html.parser')
        price_tag = soup.find('span', itemprop='price')
        if price_tag:
            try:
                return float(price_tag.get('content'))
            except (ValueError, TypeError):
                pass
        return None

class ScraperFactory:
    """
    Factory que retorna la instancia correcta de scraper 
    basándose en el dominio de la URL.
    """
    @staticmethod
    def crear_scraper(url: str) -> ScraperInterface:
        if not url:
            return DefaultFallbackScraper()
            
        url_lower = url.lower()
        if "mercadolibre.com" in url_lower:
            return MercadoLibreScraper()
        elif "compragamer.com" in url_lower:
            return CompraGamerScraper()
        elif "fullh4rd.com.ar" in url_lower:
            return FullH4rdScraper()
        elif "hardgamers.com.ar" in url_lower:
            return HardGamersScraper()
        else:
            return DefaultFallbackScraper()

class ScraperPrecios:
    """
    Servicio de fachada principal (Facade).
    Mantiene compatibilidad con el código cliente existente.
    """
    @staticmethod
    def obtener_precio_en_vivo(url, precio_catalogo=None, descripcion=None):
        if precio_catalogo is not None:
            try:
                precio_catalogo = float(precio_catalogo)
            except (ValueError, TypeError):
                pass

        precio_obtenido = None
        final_url = url

        if url and url.startswith("http"):
            scraper = ScraperFactory.crear_scraper(url)
            precio_obtenido = scraper.obtener_precio(url)

        if precio_obtenido is not None and precio_obtenido > 0:
            return precio_obtenido, final_url

        # Fallback a HardGamers si el scraping directo falla/bloquea
        print(f"[SCRAPER] Fallback: No se pudo obtener precio directo de {url}. Buscando en HardGamers...")
        
        query = ScraperPrecios._extract_query_from_url(url)
        if (not query or len(query) < 5) and descripcion:
            query = descripcion

        if query:
            clean_query = re.sub(r'[^a-zA-Z0-9\s]', '', query)
            words = [w.lower() for w in clean_query.split() if len(w) > 2]
            stopwords = {'para', 'con', 'del', 'los', 'las', 'una', 'uno', 'un', 'placa', 'madre'}
            keywords = [w for w in words if w not in stopwords]
            if not keywords:
                keywords = words
                
            precio_fb, url_fb = ScraperPrecios._buscar_en_hardgamers(keywords)
            if precio_fb and precio_fb > 0:
                print(f"[SCRAPER] Fallback exitoso: ${precio_fb} en {url_fb}")
                return precio_fb, url_fb

        print(f"[SCRAPER] Fallback fallido para {url}.")
        return None, url

    @staticmethod
    def _extract_query_from_url(url):
        if not url:
            return ""
        try:
            parsed = urllib.parse.urlparse(url)
            path = parsed.path.strip("/")
            segments = path.split("/")
            if not segments:
                return ""
            last_segment = segments[-1]
            
            if "mercadolibre" in parsed.netloc:
                parts = last_segment.split("-")
                cleaned_parts = []
                for p in parts:
                    if p.lower() in ("mla", "_jm") or p.isdigit():
                        continue
                    cleaned_parts.append(p)
                return " ".join(cleaned_parts)
            elif "compragamer" in parsed.netloc:
                name = last_segment.replace("_", " ")
                name = re.sub(r'\b\d+\s*$', '', name)
                return name.strip()
            elif "fullh4rd" in parsed.netloc:
                name = last_segment.replace("-", " ")
                return name.strip()
            else:
                return last_segment.replace("-", " ").replace("_", " ")
        except Exception:
            return ""

    @staticmethod
    def _buscar_en_hardgamers(keywords):
        if not keywords:
            return None, None
            
        search_keywords = keywords[:4] if len(keywords) > 4 else keywords
        search_str = " ".join(search_keywords)
        encoded = urllib.parse.quote_plus(search_str)
        hg_url = f"https://www.hardgamers.com.ar/search?text={encoded}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        try:
            r = requests.get(hg_url, headers=headers, timeout=10)
            if r.status_code != 200:
                return None, None
                
            soup = BeautifulSoup(r.text, 'html.parser')
            articles = soup.find_all('article', class_='One-Bit-Product')
            
            matches = []
            for art in articles:
                name_tag = art.find(itemprop='name')
                if not name_tag:
                    continue
                name = name_tag.text.strip()
                name_lower = name.lower()
                
                # Coincidencia de palabras clave
                match_count = sum(1 for kw in keywords if kw in name_lower)
                match_ratio = match_count / len(keywords) if keywords else 0
                
                price_tag = art.find('span', itemprop='price')
                price_val = None
                if price_tag:
                    try:
                        price_val = float(price_tag.get('content'))
                    except (ValueError, TypeError):
                        pass
                
                link_tag = art.find('a')
                link = link_tag.get('href') if link_tag else ""
                if link and not link.startswith("http"):
                    link = "https://www.hardgamers.com.ar" + link
                    
                matches.append({
                    "name": name,
                    "price": price_val,
                    "link": link,
                    "ratio": match_ratio,
                    "count": match_count
                })
                
            matches.sort(key=lambda x: x['ratio'], reverse=True)
            # Requisito mínimo: al menos 35% de coincidencia y al menos 2 palabras clave coincidiendo
            valid_matches = [m for m in matches if m['ratio'] >= 0.35 and m['count'] >= 2]
            
            if valid_matches:
                best = valid_matches[0]
                return best['price'], best['link']
                
        except Exception as e:
            print(f"[SCRAPER] Error de conexión al buscar fallback en HardGamers: {e}")
            
        return None, None

