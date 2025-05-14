[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/asktheapi-asktheapi-team-builder-badge.png)](https://mseep.ai/app/asktheapi-asktheapi-team-builder)

# AskTheApi Team Builder

[![PyPI version](https://badge.fury.io/py/asktheapi-team-builder.svg)](https://badge.fury.io/py/asktheapi-team-builder)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/asktheapi-team-builder.svg)](https://pypi.org/project/asktheapi-team-builder/)

A high-level Python library for building and managing networks of autonomous agents that collaborate to solve complex tasks. It's designed to work seamlessly with APIs defined using the OpenAPI standard. The library provides a clean, type-safe interface for creating, configuring, and running teams of agents, making it easy to orchestrate multi-agent workflows with minimal boilerplate.

## Features

- 🚀 Effortless Agent Network Creation: Quickly build agent networks with custom tools and capabilities based on OpenAPI specifications.

- 🤝 Team-Based Collaboration: Easily define agent teams with automatic coordination handled by a built-in planning agent.

- 📡 Streaming Interactions: Stream agent communication in real-time for more dynamic and responsive workflows.

- 🔧 Built-in HTTP Client: Simplify tool implementation with an integrated HTTP client ready to call external APIs.

- ✨ Type Safety with Pydantic: Leverage Pydantic models for robust data validation and clear type definitions.

- 🎯 Clean and Intuitive API: Designed for developers—minimal boilerplate, maximum clarity.

## Installation

```bash
pip install asktheapi-team-builder
```

## Quick Start

Here's how to use the package:



# 1. Create agents from OpenAPI spec
```python
from asktheapi_team_builder import TeamBuilder, Agent, Tool, Message, APISpecHandler
from typing import List
async def create_agents_from_spec():
    # Initialize handlers
    api_spec_handler = APISpecHandler()
    
    # Download and parse OpenAPI spec
    spec_content = await api_spec_handler.download_url_spec("https://api.example.com/openapi.json")
    
    # Classify endpoints into logical groups
    classification_result = await api_spec_handler.classify_spec(
        spec_content
    )
    
    # Generate agents for each group
    agents = []
    for group_spec in classification_result.specs:
        agent_result = await api_spec_handler.generate_agent_for_group(
            group_spec,
            spec_content
        )
        agents.append(agent_result)
    
    return agents
```

# 2. Build and run a team
```python
async def run_agent_team(agents: List[Agent], query: str):
    # Initialize team builder
    team_builder = TeamBuilder(
        model="gpt-4",
        model_config={"temperature": 0.7}
    )
    
    # Build the team
    team = await team_builder.build_team(agents)
    
    # Create messages
    messages = [
        Message(
            role="user",
            content=query
        )
    ]
    
    # Run the team with streaming
    async for event in team_builder.run_team(team, messages, stream=True):
        if isinstance(event, ChatMessage):
            print(f"{event.source}: {event.content}")
```        
# Example usage
```python
async def main():
    # Create agents from spec
    api_agents = await create_agents_from_spec()
    
    # Combine with manual agents
    all_agents = [weather_agent] + api_agents
    
    # Run the team
    await run_agent_team(
        all_agents,
        "What's the weather like in London and how might it affect local businesses?"
    )
```

## Custom Headers and Configuration

You can configure the team builder with custom headers and model settings:

```python
team_builder = TeamBuilder(
    model="gpt-4",
    model_config={
        "temperature": 0.7,
        "default_headers": {
            "Authorization": "Bearer your-token",
            "Custom-Header": "custom-value"
        }
    }
)

# Run team with extra headers for specific requests
team = await team_builder.build_team(agents)
result = await team_builder.run_team(
    team,
    messages,
    extra_headers={"Request-ID": "123"}
)
```

## MCP (Model Context Protocol) Support

The library includes built-in support for Model Context Protocol, allowing you to expose your agent teams as API endpoints with automatic tool generation from OpenAPI specifications.

```python
from asktheapi_team_builder import MCPService, MCPConfig

# Configure MCP service
mcp_config = MCPConfig(
    transport="sse",  # Server-Sent Events transport
    port=8000,        # Port to run the MCP server
    name="asktheapi_mcp"  # Service name
)

# Initialize MCP service
mcp_service = MCPService(mcp_config)

# Start MCP server with OpenAPI spec
await mcp_service.start_from_spec(
    url_spec="https://api.example.com/openapi.json",
    headers={"Authorization": "Bearer your-token"}
)
```

The MCP service will:
- Automatically download and parse the OpenAPI specification
- Classify endpoints into logical groups
- Generate appropriate tools for each group
- Expose these tools through a Model Control Protocol interface
- Handle real-time streaming of agent interactions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/alexalbala/asktheapi-team-builder.git
cd asktheapi-team-builder

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on top of [Microsoft's AutoGen](https://github.com/microsoft/autogen)
- Inspired by the need for a higher-level interface for agent team management 
