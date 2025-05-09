#  services/mentors_service.py:

from database.neo4j_db import Neo4jDatabase

class MentorsService:
    def __init__(self):
        self.db = Neo4jDatabase()
        
    def get_mentors(self, search=None, company=None, service=None, limit=10):
        mentors = self.db.get_mentors(search, company, service, limit)
        return mentors
    
    def get_companies(self):
        return self.db.get_mentor_companies()
    
    def get_services(self):
        return self.db.get_mentor_services()
    
    def close(self):
        self.db.close()
