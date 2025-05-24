from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration GitHub API
GITHUB_API_BASE = "https://api.github.com"

@app.route('/api/commits/<path:repo>', methods=['GET'])
def get_commits(repo):
    """
    Récupère les commits d'un dépôt GitHub
    Format attendu: owner/repo-name
    """
    try:
        # Validation du format du repo
        if '/' not in repo or repo.count('/') != 1:
            return jsonify({
                'error': 'Format de dépôt invalide. Utilisez le format: owner/repo-name'
            }), 400
        
        # Paramètres de la requête
        per_page = request.args.get('per_page', 30, type=int)
        page = request.args.get('page', 1, type=int)
        
        # Limite pour éviter les abus
        per_page = min(per_page, 100)
        
        # URL de l'API GitHub
        url = f"{GITHUB_API_BASE}/repos/{repo}/commits"
        params = {
            'per_page': per_page,
            'page': page
        }
        
        # Headers pour l'API GitHub (optionnel: ajouter un token pour augmenter les limites)
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Git-Log-Analyzer'
        }
        
        # Ajouter le token GitHub si disponible (recommandé pour éviter les limites de taux)
        github_token = os.environ.get('GITHUB_TOKEN')
        if github_token:
            headers['Authorization'] = f'token {github_token}'
        
        # Requête à l'API GitHub
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 404:
            return jsonify({
                'error': 'Dépôt non trouvé. Vérifiez que le dépôt existe et est public.'
            }), 404
        
        if response.status_code == 403:
            return jsonify({
                'error': 'Limite de taux API atteinte. Réessayez plus tard ou configurez un token GitHub.'
            }), 403
        
        if response.status_code != 200:
            return jsonify({
                'error': f'Erreur API GitHub: {response.status_code}'
            }), response.status_code
        
        commits_data = response.json()
        
        # Formatage des données pour le frontend
        formatted_commits = []
        for commit in commits_data:
            commit_info = {
                'sha': commit['sha'][:7],  # SHA court
                'full_sha': commit['sha'],
                'message': commit['commit']['message'],
                'author': {
                    'name': commit['commit']['author']['name'],
                    'email': commit['commit']['author']['email'],
                    'avatar_url': commit['author']['avatar_url'] if commit['author'] else None
                },
                'date': commit['commit']['author']['date'],
                'formatted_date': format_date(commit['commit']['author']['date']),
                'url': commit['html_url']
            }
            formatted_commits.append(commit_info)
        
        return jsonify({
            'success': True,
            'repository': repo,
            'commits': formatted_commits,
            'total_commits': len(formatted_commits),
            'page': page,
            'per_page': per_page
        })
        
    except requests.exceptions.Timeout:
        return jsonify({
            'error': 'Timeout lors de la requête à GitHub. Réessayez plus tard.'
        }), 408
    
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': f'Erreur de connexion: {str(e)}'
        }), 500
    
    except Exception as e:
        return jsonify({
            'error': f'Erreur interne: {str(e)}'
        }), 500

@app.route('/api/repo-info/<path:repo>', methods=['GET'])
def get_repo_info(repo):
    """
    Récupère les informations générales d'un dépôt
    """
    try:
        url = f"{GITHUB_API_BASE}/repos/{repo}"
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Git-Log-Analyzer'
        }
        
        github_token = os.environ.get('GITHUB_TOKEN')
        if github_token:
            headers['Authorization'] = f'token {github_token}'
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return jsonify({'error': 'Dépôt non trouvé'}), 404
        
        repo_data = response.json()
        
        return jsonify({
            'name': repo_data['name'],
            'full_name': repo_data['full_name'],
            'description': repo_data['description'],
            'language': repo_data['language'],
            'stars': repo_data['stargazers_count'],
            'forks': repo_data['forks_count'],
            'created_at': repo_data['created_at'],
            'updated_at': repo_data['updated_at'],
            'url': repo_data['html_url']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def format_date(iso_date):
    """
    Formate une date ISO en format lisible
    """
    try:
        dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y à %H:%M')
    except:
        return iso_date

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Point de terminaison pour vérifier l'état du serveur
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint non trouvé'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erreur interne du serveur'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🚀 Serveur Flask démarré sur le port {port}")
    print(f"📡 API disponible sur: http://localhost:{port}/api")
    
    if not os.environ.get('GITHUB_TOKEN'):
        print("⚠️  Conseil: Définissez GITHUB_TOKEN pour éviter les limites de taux")
    
    app.run(host='0.0.0.0', port=port, debug=debug)