import wikipediaapi
import json
from database import db, WikipediaContent, APIKey
from datetime import datetime

class WikipediaManager:
    """Manages Wikipedia content fetching and caching"""
    
    def __init__(self):
        # Don't use ExtractFormat to avoid keyword errors
        self.wiki = wikipediaapi.Wikipedia(
            language='en',
            user_agent='WikiContentFetcher/1.0 (Wikipedia Content Fetcher)'
        )
    
    @staticmethod
    def validate_api_key(api_key):
        """Validate if API key is valid and active"""
        key = APIKey.query.filter_by(key=api_key, is_active=True).first()
        if key:
            key.requests_count += 1
            key.last_used = datetime.utcnow()
            db.session.commit()
            return True
        return False
    
    def search_wikipedia(self, topic):
        """Search Wikipedia for a topic"""
        try:
            page = self.wiki.page(title=topic)
            
            if page.exists():
                return {
                    'success': True,
                    'title': page.title,
                    'is_exists': True,
                    'summary': page.summary[:300] if page.summary else ''
                }
            else:
                return {
                    'success': False,
                    'is_exists': False,
                    'message': f'No Wikipedia page found for "{topic}"'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error searching Wikipedia: {str(e)}'
            }
    
    def fetch_wikipedia_content(self, topic):
        """Fetch complete content from Wikipedia"""
        try:
            page = self.wiki.page(title=topic)
            
            # If page doesn't exist or is too small, return error
            if not page.exists():
                return {
                    'success': False,
                    'message': f'No Wikipedia page found for "{topic}"'
                }
            
            # Check if page has sufficient content
            if not page.text or len(page.text.strip()) < 100:
                return {
                    'success': False,
                    'message': f'Insufficient content for "{topic}" on Wikipedia'
                }
            
            # Extract sections
            sections = []
            try:
                for section in page.sections:
                    section_title = section
                    section_content = page.section(section)
                    if section_content and len(section_content.strip()) > 0:
                        sections.append({
                            'title': section_title,
                            'content': section_content[:1000]  # Limit section length
                        })
            except Exception:
                pass  # Sections might not be available
            
            # Extract categories
            categories = []
            try:
                if hasattr(page, 'categories'):
                    categories = list(page.categories.keys())[:20]
            except Exception:
                pass
            
            # Extract links for references  
            links = []
            try:
                if hasattr(page, 'links'):
                    links = list(page.links.keys())[:15]
            except Exception:
                pass
            
            # Get full text
            full_text = page.text if page.text else ""
            
            # Limit full text to reasonable length
            if len(full_text) > 10000:
                full_text = full_text[:10000] + "..."
            
            # Format the content
            formatted_content = self._format_content(page, sections)
            
            # Cache the content
            try:
                cached = WikipediaContent(
                    topic_name=topic,
                    title=page.title,
                    content=formatted_content,
                    url=page.fullurl,
                    summary=page.summary[:500] if page.summary else "",
                    categories=json.dumps(categories),
                    references=json.dumps(links)
                )
                db.session.add(cached)
                db.session.commit()
            except Exception as cache_error:
                print(f"Cache error: {cache_error}")
                db.session.rollback()
            
            return {
                'success': True,
                'title': page.title,
                'url': page.fullurl,
                'content': formatted_content,
                'summary': page.summary if page.summary else "",
                'categories': categories,
                'references': links,
                'full_text': full_text
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching Wikipedia content: {str(e)}'
            }
    
    def _format_content(self, page, sections):
        """Format Wikipedia content with proper structure"""
        formatted = f"""
# {page.title}

## Summary
{page.summary}

## Overview
{page.text[:1000]}...

## Key Sections
"""
        for section in sections[:5]:  # Limit to first 5 sections
            if section['content']:
                formatted += f"\n### {section['title']}\n{section['content'][:500]}...\n"
        
        return formatted
    
    @staticmethod
    def get_cached_content(topic):
        """Get cached Wikipedia content"""
        cached = WikipediaContent.query.filter_by(topic_name=topic).first()
        if cached:
            return cached.to_dict()
        return None
    
    @staticmethod
    def search_cache(query):
        """Search cached Wikipedia content"""
        results = WikipediaContent.query.filter(
            WikipediaContent.title.ilike(f'%{query}%')
        ).all()
        return [result.to_dict() for result in results]
    
    @staticmethod
    def get_all_cached():
        """Get all cached Wikipedia content"""
        cached = WikipediaContent.query.order_by(WikipediaContent.fetched_at.desc()).all()
        return [item.to_dict() for item in cached]
