from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Fonction pour scraper les articles en fonction d'un terme de recherche
def scrape_philomag(search_term='science', page=0):
    url = f'https://www.philomag.com/search?search_api_fulltext={search_term}&page={page}'
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": "Impossible de récupérer la page."}

    soup = BeautifulSoup(response.content, 'html.parser')
    articles = []
    rows = soup.find_all('article', class_='node')

    for row in rows:
        title_element = row.find('h3')
        title = title_element.get_text(strip=True) if title_element else 'Titre non trouvé'
        
        summary_element = row.find('p')
        summary = summary_element.get_text(strip=True) if summary_element else 'Résumé non trouvé'
        
        author_element = row.find('span', class_='author')
        author = author_element.get_text(strip=True) if author_element else 'Auteur non trouvé'
        
        date_element = row.find('time')
        date = date_element.get_text(strip=True) if date_element else 'Date non trouvée'

        articles.append({
            'title': title,
            'summary': summary,
            'author': author,
            'date': date
        })
    
    return {
        'articles': articles,
        'next_page': f"https://www.philomag.com/search?search_api_fulltext={search_term}&page={page + 1}" if articles else None
    }

# Nouvelle fonction pour scraper les citations d'un auteur
def scrape_citations(author_name):
    url = f"https://www.philomag.com/search?search_api_fulltext={author_name}"
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": "Impossible de récupérer la page."}

    soup = BeautifulSoup(response.content, 'html.parser')
    citations = []
    
    rows = soup.find_all('article', class_='node')
    
    for row in rows:
        quote_text = row.find('p').get_text(strip=True)  # Les citations semblent être dans des <p>
        author_element = row.find('span', class_='author')
        author = author_element.get_text(strip=True) if author_element else 'Auteur inconnu'
        
        if author.lower() == author_name.lower():  # Filtrer par l'auteur recherché
            citations.append(quote_text)
    
    return {
        'author': author_name,
        'citations': citations
    }

# Route pour rechercher des articles
@app.route('/search', methods=['GET'])
def search():
    search_term = request.args.get('query', 'science')
    page = int(request.args.get('page', 0))

    results = scrape_philomag(search_term, page)
    return jsonify(results)

# Nouvelle route pour rechercher des citations par auteur
@app.route('/recherche', methods=['GET'])
def search_citations():
    author_name = request.args.get('query', None)
    if not author_name:
        return jsonify({"error": "Nom de l'auteur non fourni"}), 400
    
    results = scrape_citations(author_name)
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
