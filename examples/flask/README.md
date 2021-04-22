# Run samples
* Have access granted to your github.com id.
* Install the hypertrace python agent:
```
pip install git+https://github.com/rcbj/hypertrace-pythonagent.git@main#egg=hypertrace
```
* Enter your github.com username and password when prompted.
* Add the following to your app's entrypoint python file:
```
from hypertrace.agent import Agent
# Run: ```./test.sh```

# Instrument Code
* Add the following to your app's entrypoint python file:
```
from hypertrace.agent import Agent

#
# Code snippet here represents the current initialization logic
#
logger.info('Initializing agent.')
agent = Agent()
agent.registerFlaskApp(app)
agent.registerMySQL()
agent.registerPostgreSQL()
agent.registerRequests()
agent.registerAioHttp()
agent.registerGrpcServer()
#
# End initialization logic for Python Agent
#
```
