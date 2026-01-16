#!/usr/bin/env python3
"""
Context Manager - Auto-compact and summary for long conversations
Inspired by OpenCode's auto-compact feature
"""

import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sharingan.context")

@dataclass
class ContextItem:
    role: str  # system, user, assistant, tool
    content: str
    timestamp: str
    tokens: int = 0
    metadata: Dict = field(default_factory=dict)

@dataclass
class ContextSummary:
    """Summary of conversation context"""
    summary: str
    key_topics: List[str]
    actions_taken: List[str]
    files_mentioned: List[str]
    decisions: List[str]
    created_at: str
    original_messages_count: int

class ContextManager:
    """
    Manages conversation context with auto-compact/summary for long sessions
    """
    
    def __init__(self, max_tokens: int = 100000, compact_threshold: float = 0.9):
        self.base_dir = Path(__file__).parent / "data"
        self.base_dir.mkdir(exist_ok=True)
        self.context_file = self.base_dir / "conversation_context.json"
        self.max_tokens = max_tokens
        self.compact_threshold = compact_threshold
        self.messages: List[ContextItem] = []
        self.summary: Optional[ContextSummary] = None
        self.session_start = datetime.now().isoformat()
        self.stats = {
            "total_messages": 0,
            "total_compacts": 0,
            "tokens_saved": 0
        }
        self._load_context()
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)"""
        return len(text) // 4
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> int:
        """Add a message to context and return current token count"""
        item = ContextItem(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            tokens=self.estimate_tokens(content),
            metadata=metadata or {}
        )
        self.messages.append(item)
        self.stats["total_messages"] += 1
        
        total_tokens = self.get_token_count()
        
        if total_tokens > self.max_tokens * self.compact_threshold:
            self._auto_compact()
        
        self.save_context()
        return total_tokens
    
    def _load_context(self) -> None:
        """Load context from disk at startup"""
        if self.context_file.exists():
            try:
                with open(self.context_file, 'r') as f:
                    data = json.load(f)
                
                self.messages = [
                    ContextItem(**msg) for msg in data.get("messages", [])
                ]
                
                if data.get("summary") and data["summary"].get("summary"):
                    self.summary = ContextSummary(**data["summary"])
                
                self.session_start = data.get("session_start", self.session_start)
                self.stats = data.get("stats", self.stats)
                
                logger.info(f"Loaded {len(self.messages)} messages from previous session")
            except Exception as e:
                logger.warning(f"Failed to load context: {e}")
    
    def save_context(self) -> None:
        """Save context to disk"""
        try:
            with open(self.context_file, 'w') as f:
                json.dump(self.export(), f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save context: {e}")
    
    def get_token_count(self) -> int:
        """Get total token count"""
        return sum(m.tokens for m in self.messages)
    
    def get_context(self) -> List[Dict]:
        """Get context for LLM"""
        return [
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp,
                **m.metadata
            }
            for m in self.messages
        ]
    
    def should_compact(self) -> bool:
        """Check if context should be compacted"""
        return self.get_token_count() > (self.max_tokens * self.compact_threshold)
    
    def _auto_compact(self):
        """Automatically summarize old messages"""
        logger.info("Auto-compacting context...")
        
        self.stats["total_compacts"] += 1
        
        if not self.messages:
            return
        
        recent_messages = self.messages[-50:]
        older_messages = self.messages[:-50]
        
        summary_text = self._generate_summary(older_messages)
        
        self.summary = ContextSummary(
            summary=summary_text,
            key_topics=self._extract_topics(recent_messages),
            actions_taken=self._extract_actions(recent_messages),
            files_mentioned=self._extract_files(recent_messages),
            decisions=self._extract_decisions(recent_messages),
            created_at=datetime.now().isoformat(),
            original_messages_count=len(older_messages)
        )
        
        self.stats["tokens_saved"] += sum(m.tokens for m in older_messages)
        
        self.messages = recent_messages
        
        logger.info(f"Context compacted: {len(older_messages)} messages summarized")
    
    def _generate_summary(self, messages: List[ContextItem]) -> str:
        """Generate summary of old messages"""
        if not messages:
            return "No previous context."
        
        topics = self._extract_topics(messages)
        actions = self._extract_actions(messages)
        
        summary_parts = [
            "Previous session summary:",
            f"- Discussed topics: {', '.join(topics[:5])}",
            f"- Actions taken: {', '.join(actions[:5])}",
            f"- {len(messages)} messages from earlier"
        ]
        
        return "\n".join(summary_parts)
    
    def _extract_topics(self, messages: List[ContextItem]) -> List[str]:
        """Extract key topics from messages"""
        topics = []
        keywords = [
            "security", "scan", "network", "vulnerability", "exploit",
            "code", "function", "class", "api", "database",
            "web", "server", "linux", "windows", "docker"
        ]
        
        for msg in messages:
            content_lower = msg.content.lower()
            for kw in keywords:
                if kw in content_lower and kw not in topics:
                    topics.append(kw)
        
        return topics
    
    def _extract_actions(self, messages: List[ContextItem]) -> List[str]:
        """Extract actions taken from messages"""
        actions = []
        action_patterns = [
            "executed", "ran", "created", "modified", "deleted",
            "scanned", "analyzed", "tested", "deployed", "installed"
        ]
        
        for msg in messages:
            if msg.role == "assistant" or msg.role == "tool":
                content_lower = msg.content.lower()
                for pattern in action_patterns:
                    if pattern in content_lower:
                        actions.append(msg.content[:100])
                        break
        
        return actions[-10:]
    
    def _extract_files(self, messages: List[ContextItem]) -> List[str]:
        """Extract file paths mentioned in messages"""
        files = []
        for msg in messages:
            content = msg.content
            for word in content.split():
                if "/" in word and "." in word:
                    if word not in files and not word.startswith("http"):
                        files.append(word)
        return files[-10:]
    
    def _extract_decisions(self, messages: List[ContextItem]) -> List[str]:
        """Extract decisions made during conversation"""
        decisions = []
        for msg in messages:
            if "decision" in msg.content.lower() or "chose" in msg.content.lower():
                decisions.append(msg.content[:100])
        return decisions[-5:]
    
    def get_summary_prompt(self) -> str:
        """Get summary for continuing conversation"""
        if not self.summary:
            return ""
        
        return f"""
=== PREVIOUS SESSION SUMMARY ===

{self.summary.summary}

**Key Topics:** {', '.join(self.summary.key_topics)}
**Actions Taken:** {', '.join(self.summary.actions_taken[:5])}
**Files Referenced:** {', '.join(self.summary.files_mentioned[:5])}

**Instructions:** Continue from where we left off. The above summarizes what was discussed and done before this point.
"""
    
    def create_continuation_context(self) -> List[Dict]:
        """Create context for continuing a conversation"""
        context = []
        
        if self.summary:
            context.append({
                "role": "system",
                "content": self.get_summary_prompt(),
                "timestamp": self.summary.created_at
            })
        
        context.extend(self.get_context())
        
        return context
    
    def get_stats(self) -> Dict:
        """Get context manager statistics"""
        return {
            **self.stats,
            "current_tokens": self.get_token_count(),
            "max_tokens": self.max_tokens,
            "messages_count": len(self.messages),
            "has_summary": self.summary is not None
        }
    
    def clear(self):
        """Clear all context"""
        self.messages = []
        self.summary = None
        self.session_start = datetime.now().isoformat()
    
    def export(self) -> Dict:
        """Export context for saving"""
        return {
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                    "timestamp": m.timestamp,
                    "tokens": m.tokens,
                    "metadata": m.metadata
                }
                for m in self.messages
            ],
            "summary": {
                "summary": self.summary.summary if self.summary else None,
                "key_topics": self.summary.key_topics if self.summary else [],
                "actions_taken": self.summary.actions_taken if self.summary else [],
                "files_mentioned": self.summary.files_mentioned if self.summary else [],
                "decisions": self.summary.decisions if self.summary else [],
                "created_at": self.summary.created_at if self.summary else None,
                "original_messages_count": self.summary.original_messages_count if self.summary else 0
            } if self.summary else None,
            "session_start": self.session_start,
            "stats": self.stats
        }


def get_context_manager(max_tokens: int = 100000) -> ContextManager:
    """Get context manager singleton"""
    return ContextManager(max_tokens)


if __name__ == "__main__":
    print("=== CONTEXT MANAGER TEST ===\n")
    
    ctx = ContextManager(max_tokens=500)
    
    print("1. Adding messages:")
    for i in range(10):
        msg = f"Message {i+1} - " + "x" * 100
        tokens = ctx.add_message("user", msg)
        print(f"   Message {i+1}: {tokens} tokens")
    
    print(f"\n   Total tokens: {ctx.get_token_count()}")
    print(f"   Should compact: {ctx.should_compact()}")
    
    print("\n2. Adding more messages (trigger compact):")
    for i in range(100):
        ctx.add_message("user", f"Additional message {i+1}")
    
    print(f"   Total tokens after: {ctx.get_token_count()}")
    print(f"   Compact triggered: {ctx.stats['total_compacts']}")
    print(f"   Tokens saved: {ctx.stats['tokens_saved']}")
    print(f"   Has summary: {ctx.summary is not None}")
    
    print("\n3. Summary preview:")
    if ctx.summary:
        print(f"   Topics: {ctx.summary.key_topics[:5]}")
        print(f"   Actions: {len(ctx.summary.actions_taken)}")
        print(f"   Files: {ctx.summary.files_mentioned[:3]}")
    
    print("\n4. Stats:")
    print(json.dumps(ctx.get_stats(), indent=2))
    
    print("\n✓ Context manager operational!")
