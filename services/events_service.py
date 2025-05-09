#events_service.py
from database.neo4j_db import Neo4jDatabase

class EventsService:
    def __init__(self):
        self.db = Neo4jDatabase()
        
    def get_events(self, category=None, location=None):
        events = self.db.get_events(category, location)
        return events
    
    def get_categories(self):
        return self.db.get_event_categories()
    
    def get_locations(self):
        return self.db.get_event_locations()
        
    def close(self):
        self.db.close()
