"""Conversation state shared across model providers."""

from dataclasses import dataclass, field
from typing import Literal
from uuid import uuid4


MessageRole = Literal["system", "user", "assistant", "tool"]


@dataclass(frozen=True, slots=True)
class Message:
    """A provider-neutral conversation message."""

    role: MessageRole
    content: str


@dataclass(slots=True)
class AgentSession:
    """Track a conversation independently of an LLM provider."""

    provider: str
    id: str = field(default_factory=lambda: str(uuid4()))
    messages: list[Message] = field(default_factory=list)

    def add_message(self, role: MessageRole, content: str) -> Message:
        """Append and return a message."""
        message = Message(role=role, content=content)
        self.messages.append(message)
        return message
