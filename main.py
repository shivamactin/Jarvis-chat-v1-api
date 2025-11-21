from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from chat.clickhouse.connect import CLICKHOUSE
from chat.cache.redis_cache import KVCache
from api_utils.utils import RefrenceRegistry
import os 
from rdflib.graph import Graph
from pathlib import Path
from chat.dynamic_graph import Agent
from api.v1.v1_router import router
from database.database import Base , engine
from database import models

@asynccontextmanager
async def lifespan(app:FastAPI):
    #database connections
    app.state.db = CLICKHOUSE()
    app.state.db.connect(
        host=os.environ['CLICKHOUSE_HOST'],
        port=os.environ['CLICKHOUSE_PORT'],
        username=os.environ['CLICKHOUSE_USER'],
        password=os.environ['CLICKHOUSE_PASS']
    )

    RefrenceRegistry.set("db",app.state.db)

    # Cache conection
    app.state.cache_db = KVCache()
    RefrenceRegistry.set('cache',app.state.cache_db)

    #ontology loader
    app.state.g = Graph()
    files = [str(f.resolve()) for f in Path(os.path.join(os.path.dirname(__file__),"chat","ontologies")).glob("*.rdf")]
    for file in files:
        app.state.g.parse(file,format='xml')
    
    RefrenceRegistry.set('g',app.state.g)

    #initialize agent
    app.state.agent = Agent(prompt_yaml=os.path.join(os.path.dirname(__file__),"prompts.yml")).build_graph()
    RefrenceRegistry.set('agent',app.state.agent)

    #sentiment log db
    Base.metadata.create_all(bind=engine)
    conn = engine.raw_connection()
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.close()

    
    yield
    print("Exiting app......")


app = FastAPI(title="Jarvis Chat Api",version='0.1',lifespan=lifespan)
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app,host='0.0.0.0',port=8001)