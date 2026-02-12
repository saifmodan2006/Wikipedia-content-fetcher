from database import db, Topic, Content
from sqlalchemy import or_

class ContentManager:
    """Manages content retrieval and search operations"""

    @staticmethod
    def get_all_topics():
        """Get all topics"""
        return Topic.query.order_by(Topic.name).all()

    @staticmethod
    def get_topic_by_id(topic_id):
        """Get a specific topic by ID"""
        return Topic.query.get(topic_id)

    @staticmethod
    def get_topic_by_name(name):
        """Get a topic by name"""
        return Topic.query.filter_by(name=name).first()

    @staticmethod
    def search_topics(query):
        """Search topics by name or description"""
        search_term = f"%{query}%"
        return Topic.query.filter(
            or_(
                Topic.name.ilike(search_term),
                Topic.description.ilike(search_term)
            )
        ).order_by(Topic.name).all()

    @staticmethod
    def get_content_by_topic_id(topic_id):
        """Get all content for a specific topic"""
        return Content.query.filter_by(topic_id=topic_id).order_by(Content.created_at).all()

    @staticmethod
    def get_content_by_id(content_id):
        """Get a specific content by ID"""
        return Content.query.get(content_id)

    @staticmethod
    def get_topic_with_content(topic_id):
        """Get a topic with all its content"""
        topic = Topic.query.get(topic_id)
        if topic:
            topic_dict = topic.to_dict()
            topic_dict['content'] = [c.to_dict() for c in topic.content]
            return topic_dict
        return None

    @staticmethod
    def search_all(query):
        """Search across all topics and content"""
        search_term = f"%{query}%"

        # Search in topics
        topics = Topic.query.filter(
            or_(
                Topic.name.ilike(search_term),
                Topic.description.ilike(search_term)
            )
        ).all()

        # Search in content
        content = Content.query.filter(
            or_(
                Content.title.ilike(search_term),
                Content.explanation.ilike(search_term)
            )
        ).all()

        return {
            'topics': [t.to_dict() for t in topics],
            'content': [c.to_dict() for c in content]
        }

    @staticmethod
    def get_topic_count():
        """Get total number of topics"""
        return Topic.query.count()

    @staticmethod
    def get_content_count():
        """Get total number of content pieces"""
        return Content.query.count()

    @staticmethod
    def get_popular_topics():
        """Get topics with their download counts (most popular)"""
        from database import Download

        topics_with_downloads = db.session.query(
            Topic,
            db.func.count(Download.id).label('download_count')
        ).join(
            Content, Topic.id == Content.topic_id
        ).join(
            Download, Content.id == Download.content_id, isouter=True
        ).group_by(Topic.id).order_by(Download.count.desc()).all()

        return [
            {
                'topic': t[0].to_dict(),
                'download_count': t[1]
            }
            for t in topics_with_downloads
        ]
