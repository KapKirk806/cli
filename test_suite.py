#!/usr/bin/env python3
"""
Comprehensive test suite for Multi-Agent CLI system.
Tests all components without requiring live API calls.
"""

import sys
import os
from pathlib import Path

# Test counter
tests_passed = 0
tests_failed = 0

def test(name, func):
    """Run a test and track results."""
    global tests_passed, tests_failed
    try:
        func()
        print(f"✓ {name}")
        tests_passed += 1
        return True
    except Exception as e:
        print(f"✗ {name}: {e}")
        tests_failed += 1
        return False

print("=" * 60)
print("MULTI-AGENT CLI - TEST SUITE")
print("=" * 60)
print()

# Test 1: Module Imports
print("Testing Module Imports...")
print("-" * 60)

test("Import agents.base", lambda: __import__('agents.base'))
test("Import agents.youtube_agent", lambda: __import__('agents.youtube_agent'))
test("Import utils.ui", lambda: __import__('utils.ui'))
test("Import utils.gemini_file_search", lambda: __import__('utils.gemini_file_search'))
print()

# Test 2: UI Components
print("Testing UI Components...")
print("-" * 60)

from utils.ui import UI, Color

def test_ui_init():
    ui = UI()
    assert ui.width > 0

def test_ui_colors():
    assert hasattr(Color, 'RED')
    assert hasattr(Color, 'GREEN')
    assert hasattr(Color, 'CYAN')

test("UI initialization", test_ui_init)
test("Color definitions", test_ui_colors)
print()

# Test 3: Agent Base Classes
print("Testing Agent Base Classes...")
print("-" * 60)

from agents.base import AgentConfig, BaseAgent, AgentRegistry

def test_agent_config():
    config = AgentConfig(
        id="test",
        name="Test Agent",
        description="Test",
        personality="Friendly",
        system_prompt="Test prompt"
    )
    assert config.id == "test"
    assert config.name == "Test Agent"
    assert config.model == "gemini-1.5-pro"  # default

def test_agent_registry():
    from agents.youtube_agent import YouTubeAgent

    registry = AgentRegistry()
    agent = YouTubeAgent()
    registry.register(agent)

    agents = registry.list_agents()
    assert len(agents) == 1
    assert agents[0]['id'] == 'youtube_analyzer'

    retrieved = registry.get_agent('youtube_analyzer')
    assert retrieved is not None
    assert retrieved.name == agent.name

test("AgentConfig creation", test_agent_config)
test("AgentRegistry operations", test_agent_registry)
print()

# Test 4: YouTube Agent
print("Testing YouTube Agent...")
print("-" * 60)

from agents.youtube_agent import YouTubeAgent

def test_youtube_agent_init():
    agent = YouTubeAgent()
    assert agent.id == 'youtube_analyzer'
    assert agent.name == 'YouTube Channel Analyzer'
    assert agent.knowledge_base_path == Path('data/youtube_analyzer')

def test_youtube_agent_config():
    agent = YouTubeAgent()
    prompt = agent.get_system_prompt()
    assert len(prompt) > 0
    assert 'YouTube' in prompt or 'youtube' in prompt

def test_youtube_sanitize():
    agent = YouTubeAgent()
    # Test filename sanitization
    result = agent._sanitize_filename("Test <Video> Name: 2024")
    assert '<' not in result
    assert '>' not in result
    assert ':' not in result

test("YouTube agent initialization", test_youtube_agent_init)
test("YouTube agent system prompt", test_youtube_agent_config)
test("YouTube filename sanitization", test_youtube_sanitize)
print()

# Test 5: File Search Components
print("Testing File Search Components...")
print("-" * 60)

from utils.gemini_file_search import FileSearchManager

def test_file_search_init():
    # Should work without API key
    manager = FileSearchManager()
    assert manager is not None

test("FileSearchManager initialization", test_file_search_init)
print()

# Test 6: Configuration System
print("Testing Configuration System...")
print("-" * 60)

def test_config_to_dict():
    config = AgentConfig(
        id="test",
        name="Test",
        description="Desc",
        personality="Pers",
        system_prompt="Prompt"
    )
    data = config.__dict__
    assert 'id' in data
    assert 'name' in data
    assert 'model' in data

def test_config_path():
    config = AgentConfig(
        id="test",
        name="Test",
        description="Desc",
        personality="Pers",
        system_prompt="Prompt",
        knowledge_base_path=Path("data/test")
    )
    assert isinstance(config.knowledge_base_path, Path)

test("Config serialization", test_config_to_dict)
test("Config with custom path", test_config_path)
print()

# Test 7: Data Storage
print("Testing Data Storage...")
print("-" * 60)

def test_knowledge_base_creation():
    agent = YouTubeAgent()
    # Knowledge base path should be created
    assert agent.knowledge_base_path.exists()

def test_save_load_data():
    agent = YouTubeAgent()
    test_data = "Test content"
    filename = "test_file.txt"

    # Save
    agent.save_to_knowledge_base(filename, test_data)

    # Load
    loaded = agent.load_from_knowledge_base(filename)
    assert loaded == test_data

    # Cleanup
    (agent.knowledge_base_path / filename).unlink()

test("Knowledge base directory creation", test_knowledge_base_creation)
test("Save and load from knowledge base", test_save_load_data)
print()

# Test 8: Error Handling
print("Testing Error Handling...")
print("-" * 60)

def test_load_nonexistent():
    agent = YouTubeAgent()
    result = agent.load_from_knowledge_base("nonexistent_file.txt")
    assert result is None

def test_registry_get_missing():
    registry = AgentRegistry()
    result = registry.get_agent("nonexistent_agent")
    assert result is None

test("Load non-existent file", test_load_nonexistent)
test("Get non-existent agent", test_registry_get_missing)
print()

# Summary
print("=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print(f"Tests Passed: {tests_passed}")
print(f"Tests Failed: {tests_failed}")
print(f"Total Tests: {tests_passed + tests_failed}")
print()

if tests_failed > 0:
    print(f"❌ {tests_failed} test(s) failed")
    sys.exit(1)
else:
    print(f"✅ All {tests_passed} tests passed!")
    sys.exit(0)
