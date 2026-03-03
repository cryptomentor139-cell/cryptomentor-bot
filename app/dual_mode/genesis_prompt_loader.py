"""
Genesis Prompt Loader for Dual-Mode System

This module handles loading and caching of the Genesis Prompt that is injected
into all AI agents as their base knowledge for trading operations.
"""

import os
import hashlib
from datetime import datetime
from typing import Optional
from pathlib import Path


class GenesisPromptLoader:
    """
    Manages loading and caching of the Genesis Prompt for AI agents.
    
    The Genesis Prompt is loaded from AUTOMATON_GENESIS_PROMPT.md and cached
    in memory for performance. It can be reloaded without restart.
    """
    
    def __init__(self, prompt_file_path: str = "AUTOMATON_GENESIS_PROMPT.md"):
        """
        Initialize the Genesis Prompt Loader.
        
        Args:
            prompt_file_path: Path to the Genesis Prompt markdown file
        """
        self.prompt_file_path = prompt_file_path
        self._cached_prompt: Optional[str] = None
        self._prompt_version: Optional[str] = None
        self._last_loaded: Optional[datetime] = None
    
    def load_prompt(self) -> str:
        """
        Load the Genesis Prompt from file and cache it in memory.
        
        Returns:
            The Genesis Prompt content as a string
            
        Raises:
            FileNotFoundError: If the prompt file doesn't exist
            IOError: If there's an error reading the file
        """
        try:
            # Resolve the full path
            file_path = Path(self.prompt_file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(
                    f"Genesis Prompt file not found: {self.prompt_file_path}"
                )
            
            # Read the prompt content
            with open(file_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
            
            # Cache the prompt
            self._cached_prompt = prompt_content
            self._last_loaded = datetime.now()
            
            # Generate version hash from content
            self._prompt_version = self._generate_version_hash(prompt_content)
            
            return prompt_content
            
        except FileNotFoundError:
            raise
        except Exception as e:
            raise IOError(f"Error loading Genesis Prompt: {str(e)}")
    
    def reload_prompt(self) -> str:
        """
        Reload the Genesis Prompt from file, updating the cache.
        
        This allows updating the prompt without restarting the application.
        New agents created after reload will use the updated prompt.
        
        Returns:
            The updated Genesis Prompt content
            
        Raises:
            FileNotFoundError: If the prompt file doesn't exist
            IOError: If there's an error reading the file
        """
        return self.load_prompt()
    
    def get_current_prompt(self) -> str:
        """
        Get the current cached Genesis Prompt.
        
        If the prompt hasn't been loaded yet, it will be loaded automatically.
        
        Returns:
            The current Genesis Prompt content
        """
        if self._cached_prompt is None:
            return self.load_prompt()
        
        return self._cached_prompt
    
    def get_prompt_version(self) -> str:
        """
        Get the version hash of the current Genesis Prompt.
        
        The version is a hash of the prompt content, useful for tracking
        which version of the prompt is being used by agents.
        
        Returns:
            Version hash string (first 8 characters of SHA256)
        """
        if self._prompt_version is None:
            # Load prompt if not already loaded
            self.get_current_prompt()
        
        return self._prompt_version or "unknown"
    
    def get_last_loaded_time(self) -> Optional[datetime]:
        """
        Get the timestamp when the prompt was last loaded.
        
        Returns:
            Datetime of last load, or None if never loaded
        """
        return self._last_loaded
    
    def is_loaded(self) -> bool:
        """
        Check if the Genesis Prompt has been loaded.
        
        Returns:
            True if prompt is cached, False otherwise
        """
        return self._cached_prompt is not None
    
    def _generate_version_hash(self, content: str) -> str:
        """
        Generate a version hash from the prompt content.
        
        Args:
            content: The prompt content to hash
            
        Returns:
            First 8 characters of SHA256 hash
        """
        hash_obj = hashlib.sha256(content.encode('utf-8'))
        return hash_obj.hexdigest()[:8]


# Global singleton instance
_loader_instance: Optional[GenesisPromptLoader] = None


def get_genesis_prompt_loader() -> GenesisPromptLoader:
    """
    Get the global Genesis Prompt Loader instance.
    
    Returns:
        The singleton GenesisPromptLoader instance
    """
    global _loader_instance
    
    if _loader_instance is None:
        _loader_instance = GenesisPromptLoader()
    
    return _loader_instance
