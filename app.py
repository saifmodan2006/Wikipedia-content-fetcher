import os
from flask import Flask, render_template, request, jsonify, send_file
from config import config
from database import db, init_db, seed_db
from content_manager import ContentManager
from wikipedia_manager import WikipediaManager
from file_generator import FileGenerator
from datetime import datetime

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize database
    db.init_app(app)

    with app.app_context():
        init_db(app)
        seed_db(app)

    # Initialize file generator
    file_gen = FileGenerator(app.config['DOWNLOAD_FOLDER'])

    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    # ====== WEB ROUTES ======
    @app.route('/')
    def index():
        """Home page with topic listing"""
        return render_template('index.html')

    @app.route('/search')
    def search_page():
        """Search page"""
        return render_template('search.html')

    @app.route('/wikipedia')
    def wikipedia_page():
        """Wikipedia content fetcher page"""
        return render_template('wikipedia.html')

    @app.route('/preview/<int:content_id>')
    def preview(content_id):
        """Preview content page"""
        content = ContentManager.get_content_by_id(content_id)
        if not content:
            return render_template('error.html', message='Content not found'), 404

        topic = ContentManager.get_topic_by_id(content.topic_id)
        return render_template('preview.html', topic=topic, content=content)

    # ====== API ROUTES ======
    @app.route('/api/topics', methods=['GET'])
    def api_topics():
        """Get all available topics"""
        topics = ContentManager.get_all_topics()
        return jsonify({
            'success': True,
            'data': [topic.to_dict() for topic in topics]
        })

    @app.route('/api/topics/search', methods=['GET'])
    def api_search():
        """Search topics"""
        query = request.args.get('q', '').strip()

        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter required'
            }), 400

        if len(query) < 2:
            return jsonify({
                'success': False,
                'error': 'Query must be at least 2 characters long'
            }), 400

        results = ContentManager.search_topics(query)
        return jsonify({
            'success': True,
            'data': [topic.to_dict() for topic in results]
        })

    @app.route('/api/topics/<int:topic_id>', methods=['GET'])
    def api_topic_detail(topic_id):
        """Get a specific topic"""
        topic = ContentManager.get_topic_by_id(topic_id)

        if not topic:
            return jsonify({
                'success': False,
                'error': 'Topic not found'
            }), 404

        return jsonify({
            'success': True,
            'data': topic.to_dict()
        })

    @app.route('/api/topics/<int:topic_id>/content', methods=['GET'])
    def api_topic_content(topic_id):
        """Get all content for a specific topic"""
        topic = ContentManager.get_topic_by_id(topic_id)

        if not topic:
            return jsonify({
                'success': False,
                'error': 'Topic not found'
            }), 404

        content_list = ContentManager.get_content_by_topic_id(topic_id)
        return jsonify({
            'success': True,
            'topic': topic.to_dict(),
            'content': [c.to_dict() for c in content_list]
        })

    @app.route('/api/content/<int:content_id>', methods=['GET'])
    def api_content_detail(content_id):
        """Get specific content details"""
        content = ContentManager.get_content_by_id(content_id)

        if not content:
            return jsonify({
                'success': False,
                'error': 'Content not found'
            }), 404

        topic = ContentManager.get_topic_by_id(content.topic_id)
        return jsonify({
            'success': True,
            'topic': topic.to_dict(),
            'content': content.to_dict()
        })

    @app.route('/api/download/<int:content_id>', methods=['POST'])
    def api_download(content_id):
        """Generate and download file"""
        content = ContentManager.get_content_by_id(content_id)

        if not content:
            return jsonify({
                'success': False,
                'error': 'Content not found'
            }), 404

        # Get format from query parameter
        format_type = request.args.get('format', 'pdf').lower()

        # Validate format
        if format_type not in ['pdf', 'text', 'txt', 'markdown', 'md']:
            return jsonify({
                'success': False,
                'error': f'Invalid format: {format_type}'
            }), 400

        try:
            topic = ContentManager.get_topic_by_id(content.topic_id)
            content_dict = content.to_dict()

            # Generate file
            filename, filepath = file_gen.generate_file(
                topic.name,
                content_dict,
                format_type
            )

            # Record download
            from database import Download
            download_record = Download(
                content_id=content_id,
                format=format_type,
                file_name=filename
            )
            db.session.add(download_record)
            db.session.commit()

            # Return file for download
            return send_file(
                filepath,
                as_attachment=True,
                download_name=filename
            )

        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error generating file: {str(e)}'
            }), 500

    # Initialize Wikipedia Manager
    wiki_manager = WikipediaManager()

    @app.route('/api/stats', methods=['GET'])
    def api_stats():
        """Get API statistics"""
        return jsonify({
            'success': True,
            'data': {
                'total_topics': ContentManager.get_topic_count(),
                'total_content': ContentManager.get_content_count()
            }
        })

    # ====== WIKIPEDIA API ROUTES ======
    @app.route('/api/wikipedia/search', methods=['POST'])
    def api_wikipedia_search():
        """Search for Wikipedia content"""
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key required'
            }), 401
        
        if not WikipediaManager.validate_api_key(api_key):
            return jsonify({
                'success': False,
                'error': 'Invalid API key'
            }), 401
        
        data = request.get_json()
        topic = data.get('topic', '').strip() if data else ''
        
        if not topic:
            return jsonify({
                'success': False,
                'error': 'Topic is required'
            }), 400
        
        if len(topic) < 2:
            return jsonify({
                'success': False,
                'error': 'Topic must be at least 2 characters'
            }), 400
        
        result = wiki_manager.search_wikipedia(topic)
        return jsonify(result)

    @app.route('/api/wikipedia/fetch', methods=['POST'])
    def api_wikipedia_fetch():
        """Fetch complete Wikipedia content"""
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key required'
            }), 401
        
        if not WikipediaManager.validate_api_key(api_key):
            return jsonify({
                'success': False,
                'error': 'Invalid API key'
            }), 401
        
        data = request.get_json()
        topic = data.get('topic', '').strip() if data else ''
        
        if not topic:
            return jsonify({
                'success': False,
                'error': 'Topic is required'
            }), 400
        
        result = wiki_manager.fetch_wikipedia_content(topic)
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 404

    @app.route('/api/wikipedia/cached/<topic>', methods=['GET'])
    def api_wikipedia_cached(topic):
        """Get cached Wikipedia content"""
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key required'
            }), 401
        
        if not WikipediaManager.validate_api_key(api_key):
            return jsonify({
                'success': False,
                'error': 'Invalid API key'
            }), 401
        
        cached = WikipediaManager.get_cached_content(topic)
        
        if cached:
            return jsonify({
                'success': True,
                'data': cached
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No cached content found'
            }), 404

    @app.route('/api/wikipedia/cache/search', methods=['GET'])
    def api_wikipedia_cache_search():
        """Search cached Wikipedia content"""
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key required'
            }), 401
        
        if not WikipediaManager.validate_api_key(api_key):
            return jsonify({
                'success': False,
                'error': 'Invalid API key'
            }), 401
        
        query = request.args.get('q', '').strip()
        
        if not query:
            results = WikipediaManager.get_all_cached()
        else:
            results = WikipediaManager.search_cache(query)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'data': results
        })

    @app.route('/api/wikipedia/download/<int:content_id>', methods=['GET'])
    def api_wikipedia_download(content_id):
        """Download Wikipedia content"""
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key required'
            }), 401
        
        if not WikipediaManager.validate_api_key(api_key):
            return jsonify({
                'success': False,
                'error': 'Invalid API key'
            }), 401
        
        from database import WikipediaContent
        content = WikipediaContent.query.get(content_id)
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'Content not found'
            }), 404
        
        format_type = request.args.get('format', 'pdf').lower()
        
        if format_type not in ['pdf', 'text', 'txt', 'markdown', 'md']:
            return jsonify({
                'success': False,
                'error': f'Invalid format: {format_type}'
            }), 400
        
        try:
            content_dict = {
                'title': content.title,
                'explanation': content.content,
                'references': content.references
            }
            
            filename, filepath = file_gen.generate_file(
                content.topic_name,
                content_dict,
                format_type
            )
            
            return send_file(
                filepath,
                as_attachment=True,
                download_name=filename
            )
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error generating file: {str(e)}'
            }), 500

    @app.route('/api/keys/generate', methods=['POST'])
    def api_generate_key():
        """Generate a new API key (development only)"""
        from database import APIKey
        
        data = request.get_json()
        key_name = data.get('name', 'Generated Key').strip() if data else 'Generated Key'
        
        if len(key_name) < 2:
            return jsonify({
                'success': False,
                'error': 'Key name must be at least 2 characters'
            }), 400
        
        new_key = APIKey(
            key=APIKey.generate_key(),
            name=key_name,
            is_active=True
        )
        db.session.add(new_key)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'API key generated successfully',
            'data': new_key.to_dict()
        }), 201

    @app.route('/api/keys/list', methods=['GET'])
    def api_list_keys():
        """List all API keys (development only)"""
        from database import APIKey
        
        keys = APIKey.query.all()
        return jsonify({
            'success': True,
            'count': len(keys),
            'data': [key.to_dict() for key in keys]
        })

    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)
