from langchain_core.tools import tool
from chat.registries.tool_registries import TOOLRegistry
from rdflib.query import Result
from chat.tools.tool_utils import is_safe_readonly_sql
from api_utils.utils import RefrenceRegistry
from chat.utils.utility import hash_query
from pydantic import BaseModel
from typing import TypedDict, Dict, Optional


class DBCache(TypedDict):
    schema: str
    queries: Dict[str, str]


class CacheType(BaseModel):
    db_cache: Optional[DBCache]


# -----------------------------
# 1. SPARQL QUERY TOOL
# -----------------------------
@TOOLRegistry.register
@tool
def run_sparql_query_on_ontology(query: str) -> str:
    """
    Executes a SPARQL query on the globally registered RDF graph.
    """
    try:
        g = RefrenceRegistry.get("g")
        if not g:
            return "Ontology graph is not parsed; exiting with error."

        result: Result = g.query(query)

        if result.type == "ASK":
            return str(result.askAnswer)

        if result.type != "SELECT":
            return "The supported result type is SELECT"

        # Optimized string joining
        rows = ["(" + ", ".join(str(item) for item in row) + ")" for row in result]
        return "\n".join(rows)

    except Exception as e:
        return f"SPARQL Error: {e}"


# -----------------------------
# 2. EXPLORE DATABASE TOOL
# -----------------------------
@TOOLRegistry.register
@tool
def explore_db() -> str:
    """
    Explore ClickHouse databases, tables and schema using caching.
    """
    try:
        cache = RefrenceRegistry.get("cache")
        clickhouse = RefrenceRegistry.get("db")

        if not cache or not clickhouse:
            return "Cache or Database connection is not working."

        db_cache: Optional[DBCache] = cache.get("db_cache")

        # return cached schema
        if db_cache and db_cache.get("schema"):
            return db_cache["schema"]

        schema = clickhouse.extract_clickhouse_schema()
        text = f"Database name is JARVIS_DB and it has the following tables{schema}"

        # update DB cache properly
        cache.set(
            "db_cache",
            {
                **(db_cache or {}),
                "schema": text,
                "queries": (db_cache.get("queries") if db_cache else {}),
            },
            ttl=10_800,
        )
        return text

    except Exception as e:
        return f"ExploreDB Error: {e}"


# -----------------------------
# 3. SQL EXECUTION TOOL
# -----------------------------
@TOOLRegistry.register
@tool
def execute_sql_command(query: str) -> str:
    """
    Executes a READ-ONLY SQL query on ClickHouse with result caching.
    """
    try:
        clickhouse = RefrenceRegistry.get("db")
        cache = RefrenceRegistry.get("cache")

        if not clickhouse or not cache:
            return "Database or Cache is not connected."

        if not is_safe_readonly_sql(query):
            return "Client has only readonly access."

        if not clickhouse.client:
            return "Database client is not connected."

        db_cache: Optional[DBCache] = cache.get("db_cache") or {
            "schema": "",
            "queries": {}
        }

        query_hash = hash_query(query)

        if not db_cache.get('queries'):
            db_cache['queries']={}
            
        # return cached result if exists
        if query_hash in db_cache["queries"]:
            return db_cache["queries"][query_hash]

        # execute query
        rows = clickhouse.client.query(query).result_rows
        result = "\n".join(str(r) for r in rows)

        # update query cache block
        db_cache["queries"][query_hash] = result

        # write back to cache with TTL
        cache.set("db_cache", db_cache, ttl=10_800)

        return result

    except Exception as e:
        return f"SQL Error: {e}"

