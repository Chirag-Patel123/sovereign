from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    """Abstract base class for tools executable by Person 1's Agent loop."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name matching PRD contract: search | calculate | write_file"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Clear description of tool capabilities for planning."""
        pass

    @abstractmethod
    def run(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool and return a JSON-serializable dictionary."""
        pass
