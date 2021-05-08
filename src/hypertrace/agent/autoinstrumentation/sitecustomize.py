'''Enable instrumentationon all supported modules.'''
from hypertrace.agent import Agent
agent = Agent()
agent.register_flask_app()
agent.register_grpc_server()
agent.register_grpc_client()
agent.register_mysql()
agent.register_postgresql()
agent.register_requests()
agent.register_aiohttp_client()
