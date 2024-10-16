from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

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

@app.route('/search', methods=['GET'])
def search():
    search_term = request.args.get('query', 'science')  # Termes de recherche
    page = int(request.args.get('page', 0))  # Page par défaut (convertie en entier)
    
    results = scrape_philomag(search_term, page)
    
    return jsonify(results)

# Nouvelle route /recherche qui permet de filtrer par auteur ou sujet
@app.route('/recherche', methods=['GET'])
def recherche():
    query = request.args.get('query', '')  # Terme de recherche (auteur ou autre sujet)
    page = int(request.args.get('page', 0))  # Page par défaut
    
    # Récupérer les résultats en fonction de la recherche
    results = scrape_philomag(query, page)
    articles = results.get('articles', [])
    
    # Filtrer les articles où l'auteur correspond à la requête ou si le terme de recherche apparaît dans le titre ou le résumé
    filtered_articles = [
        article for article in articles
        if query.lower() in article['author'].lower() or query.lower() in article['title'].lower() or query.lower() in article['summary'].lower()
    ]
    
    # Si aucun article trouvé
    if not filtered_articles:
        return jsonify({"message": f"Aucun article trouvé pour la recherche '{query}'."})
    
    return jsonify(filtered_articles)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Écoute sur toutes les adresses (0.0.0.0) et le port 5000
        
