#jobs_service.py
from database.neo4j_db import Neo4jDatabase

class JobsService:
    def __init__(self):
        self.db = Neo4jDatabase()
        
    def search_jobs(self, search=None, location=None, remote=None, limit=7, page=1):
        jobs = self.db.search_jobs(search, location, remote, limit)
        
        return {
            "results": jobs,
            "total": len(jobs)
        }
    
    def get_locations(self):
        return self.db.get_job_locations()
    
    def close(self):
        self.db.close()
