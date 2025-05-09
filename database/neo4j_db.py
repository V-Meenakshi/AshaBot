#neo4j_db.py
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Neo4jDatabase:
    def __init__(self):
        self._driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"), 
            auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
        )
        
    def close(self):
        self._driver.close()
        
    # Event-related methods
    def get_events(self, category=None, location=None):
        with self._driver.session() as session:
            if category and location:
                query = """
                MATCH (e:Event)-[:RELATED_TO]->(c:Category {name: $category})
                MATCH (e)-[:OCCURS_AT]->(l:Location {name: $location})
                RETURN e, collect(c.name) AS categories
                """
                result = session.run(query, category=category, location=location)
            elif category:
                query = """
                MATCH (e:Event)-[:RELATED_TO]->(c:Category {name: $category})
                WITH e, collect(c.name) AS categories
                RETURN e, categories
                """
                result = session.run(query, category=category)
            elif location:
                query = """
                MATCH (e:Event)-[:OCCURS_AT]->(l:Location {name: $location})
                MATCH (e)-[:RELATED_TO]->(c:Category)
                WITH e, collect(c.name) AS categories
                RETURN e, categories
                """
                result = session.run(query, location=location)
            else:
                query = """
                MATCH (e:Event)
                OPTIONAL MATCH (e)-[:RELATED_TO]->(c:Category)
                WITH e, collect(c.name) AS categories
                RETURN e, categories
                LIMIT 10
                """
                result = session.run(query)
                
            return [self._format_event_with_categories(record) for record in result]
    
    # Rest of your existing methods...
    def _format_event_with_categories(self, record):
        event = record["e"]
        categories = record["categories"]
        
        return {
            "name": event["name"],
            "mode": event["mode"],
            "location": event["location"],
            "start_date": event["start_date"],
            "end_date": event["end_date"],
            "timing": event["timing"],
            "about": event["about"],
            "categories": categories
        }
            
    def get_event_categories(self):
        with self._driver.session() as session:
            query = """
            MATCH (c:Category)
            RETURN c.name AS category
            """
            result = session.run(query)
            return [record["category"] for record in result]
            
    def get_event_locations(self):
        with self._driver.session() as session:
            query = """
            MATCH (l:Location)
            WHERE EXISTS((l)<-[:OCCURS_AT]-(:Event))
            RETURN DISTINCT l.name AS location
            """
            result = session.run(query)
            return [record["location"] for record in result]
    
    # Job-related methods
    def search_jobs(self, search=None, location=None, remote=None, limit=7):
        with self._driver.session() as session:
            parameters = {}
            query_parts = [
                "MATCH (j:Job)-[:BELONGS_TO]->(c:Company)"
            ]
            
            if location:
                query_parts.append("MATCH (j)-[:LOCATED_AT]->(l:Location {name: $location})")
                parameters["location"] = location
            else:
                query_parts.append("MATCH (j)-[:LOCATED_AT]->(l:Location)")
            
            where_conditions = []
            
            if search:
                where_conditions.append("(j.title CONTAINS $search OR c.name CONTAINS $search OR j.qualifications CONTAINS $search)")
                parameters["search"] = search
                
            if remote is not None:
                if remote:
                    where_conditions.append("j.work_model CONTAINS 'Remote'")
                else:
                    where_conditions.append("NOT j.work_model CONTAINS 'Remote'")
            
            if where_conditions:
                query_parts.append("WHERE " + " AND ".join(where_conditions))
            
            # Include all relevant fields in the return statement
            query_parts.append("RETURN j, c, l")
            query_parts.append(f"LIMIT {limit}")
            
            final_query = " ".join(query_parts)
            result = session.run(final_query, **parameters)
            
            return [self._format_job(record) for record in result]
    
    def _format_job(self, record):
        job = record["j"]
        company = record["c"]
        location = record["l"]
        
        return {
            "role": job["title"],
            "company_name": company["name"],
            "company_industry": company.get("industry", ""),
            "company_size": company.get("size", ""),
            "location": location["name"],
            "remote": "Remote" in job.get("work_model", ""),
            "hire_time": job.get("hire_time", ""),
            "graduate_time": job.get("graduate_time", ""),
            "salary": job.get("salary", ""),
            "text": job.get("qualifications", ""),
            "url": job.get("apply_link", ""),
            "date_posted": job.get("date_posted", "")
        }
    
    def get_job_locations(self):
        with self._driver.session() as session:
            query = """
            MATCH (l:Location)<-[:LOCATED_AT]-(j:Job)
            RETURN DISTINCT l.name AS location
            """
            result = session.run(query)
            return [record["location"] for record in result]

    # Mentors-related methods
    def get_mentors(self, search=None, company=None, service=None, limit=10):
        with self._driver.session() as session:
            parameters = {}
            query_parts = [
                "MATCH (m:Mentor)-[:WORKS_FOR]->(c:Company)"
            ]
            
            where_conditions = []
            
            if search:
                where_conditions.append("(m.name CONTAINS $search OR m.role CONTAINS $search OR c.name CONTAINS $search)")
                parameters["search"] = search
                
            if company:
                where_conditions.append("c.name CONTAINS $company")
                parameters["company"] = company
                
            if service:
                where_conditions.append("m.services CONTAINS $service")
                parameters["service"] = service
            
            if where_conditions:
                query_parts.append("WHERE " + " AND ".join(where_conditions))
            
            query_parts.append("RETURN m, c")
            query_parts.append(f"LIMIT {limit}")
            
            final_query = " ".join(query_parts)
            result = session.run(final_query, **parameters)
            
            return [self._format_mentor(record) for record in result]

    def _format_mentor(self, record):
        mentor = record["m"]
        company = record["c"]
        
        return {
            "name": mentor["name"],
            "role": mentor.get("role", ""),
            "company": company["name"],
            "bookings": mentor.get("bookings", "0"),
            "services": mentor.get("services", "").split(',') if mentor.get("services") else []
        }

    def get_mentor_companies(self):
        with self._driver.session() as session:
            query = """
            MATCH (c:Company)<-[:WORKS_FOR]-(m:Mentor)
            RETURN DISTINCT c.name AS company
            """
            result = session.run(query)
            return [record["company"] for record in result]

    def get_mentor_services(self):
        with self._driver.session() as session:
            query = """
            MATCH (m:Mentor)
            WHERE m.services IS NOT NULL
            UNWIND split(m.services, ',') AS service
            RETURN DISTINCT trim(service) AS service
            """
            result = session.run(query)
            return [record["service"] for record in result]
    
    # User authentication methods
    def create_user(self, username, password_hash):
        with self._driver.session() as session:
            # Check if user already exists
            check_query = """
            MATCH (u:User {username: $username})
            RETURN u
            """
            result = session.run(check_query, username=username)
            if result.single():
                return False  # User already exists
            
            # Create new user
            create_query = """
            CREATE (u:User {username: $username, password: $password, created_at: datetime()})
            RETURN u
            """
            session.run(create_query, username=username, password=password_hash)
            return True  # User created
    
    def get_user(self, username):
        with self._driver.session() as session:
            query = """
            MATCH (u:User {username: $username})
            RETURN u
            """
            result = session.run(query, username=username)
            record = result.single()
            if record:
                user = record["u"]
                return {
                    "username": user["username"],
                    "password": user["password"]
                }
            return None
