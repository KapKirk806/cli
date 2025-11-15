"""
Base classes for all agents in the system.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    id: str
    name: str
    description: str
    personality: str
    system_prompt: str
    model: str = "gemini-1.5-pro"
    temperature: float = 0.7
    knowledge_base_path: Optional[Path] = None
    mcp_servers: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)

    @classmethod
    def from_file(cls, config_path: Path) -> 'AgentConfig':
        """Load agent configuration from JSON file."""
        with open(config_path, 'r') as f:
            data = json.load(f)

        if 'knowledge_base_path' in data and data['knowledge_base_path']:
            data['knowledge_base_path'] = Path(data['knowledge_base_path'])

        return cls(**data)

    def to_file(self, config_path: Path):
        """Save agent configuration to JSON file."""
        data = self.__dict__.copy()
        if data.get('knowledge_base_path'):
            data['knowledge_base_path'] = str(data['knowledge_base_path'])

        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)


class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(self, config: AgentConfig):
        """Initialize agent with configuration.

        Args:
            config: Agent configuration object
        """
        self.config = config
        self.knowledge_base_path = config.knowledge_base_path or Path(f"data/{config.id}")
        self.knowledge_base_path.mkdir(parents=True, exist_ok=True)

    @property
    def id(self) -> str:
        """Get agent ID."""
        return self.config.id

    @property
    def name(self) -> str:
        """Get agent name."""
        return self.config.name

    @property
    def description(self) -> str:
        """Get agent description."""
        return self.config.description

    @abstractmethod
    def run(self, ui: Any):
        """
        Run the agent's main functionality.

        Args:
            ui: UI object for user interaction
        """
        pass

    def get_system_prompt(self) -> str:
        """
        Get the full system prompt including personality.

        Returns:
            Complete system prompt for the agent
        """
        return f"{self.config.personality}\n\n{self.config.system_prompt}"

    def save_to_knowledge_base(self, filename: str, content: str):
        """
        Save content to the agent's knowledge base.

        Args:
            filename: Name of the file
            content: Content to save
        """
        filepath = self.knowledge_base_path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    def load_from_knowledge_base(self, filename: str) -> Optional[str]:
        """
        Load content from the agent's knowledge base.

        Args:
            filename: Name of the file

        Returns:
            File content if exists, None otherwise
        """
        filepath = self.knowledge_base_path / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        return None


class AgentRegistry:
    """Registry for managing multiple agents."""

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent):
        """
        Register an agent.

        Args:
            agent: Agent instance to register
        """
        self._agents[agent.id] = agent

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get an agent by ID.

        Args:
            agent_id: ID of the agent

        Returns:
            Agent instance or None if not found
        """
        return self._agents.get(agent_id)

    def list_agents(self) -> List[Dict[str, str]]:
        """
        List all registered agents.

        Returns:
            List of agent info dictionaries
        """
        return [
            {
                'id': agent.id,
                'name': agent.name,
                'description': agent.description
            }
            for agent in self._agents.values()
        ]

    def unregister(self, agent_id: str):
        """
        Unregister an agent.

        Args:
            agent_id: ID of the agent to remove
        """
        if agent_id in self._agents:
            del self._agents[agent_id]
