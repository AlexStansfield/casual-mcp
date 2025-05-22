# Casual MCP

The starter aim of this was to create a package that would:
- [x] allow me to easily add multiple MCP servers.
- [x] handle tool calls from the LLM
- [x] configuration support for multiple models over differnt providers
- [x] Add OpenAI Provider
- [x] include some basic MCP servers
- [x] Include an API for quick testing 

Further aims:
* Support a final response model allowing handling of tools done by another model
* Add a "tuner" to allow you to test multiple LLMs to find the best at handling tools
* Add more MCP Servers


## Todo 

- [ ] Add configurable tool result response formatting (just the result, function name and result, etc)
- [ ] Add support for router and final response models
- [ ] Add Ollama Provider

### Tuner

- [ ] Create inital tuner to test the tool calls made
- [ ] Add Web UI to control test
- [ ] Add AI Final Result Checking 

### MCP Servers

- [x] Weather
- [x] Improved Date and Time
- [ ] Brave Search
- [ ] Movies
- [ ] Music