#!/usr/bin/env python3
"""
Test edge cases and error handling that weren't tested in initial test suite.
"""

import sys
from pathlib import Path

print("=" * 60)
print("EDGE CASE & ERROR HANDLING TESTS")
print("=" * 60)
print()

tests_passed = 0
tests_failed = 0

def test(name, func):
    global tests_passed, tests_failed
    try:
        func()
        print(f"✓ {name}")
        tests_passed += 1
    except Exception as e:
        print(f"✗ {name}: {e}")
        tests_failed += 1

# Test 1: Empty/Invalid Inputs
print("Testing Input Validation...")
print("-" * 60)

from agents.youtube_agent import YouTubeAgent

def test_empty_filename():
    agent = YouTubeAgent()
    result = agent._sanitize_filename("")
    assert result == "", "Empty filename should return empty"

def test_very_long_filename():
    agent = YouTubeAgent()
    long_name = "x" * 200
    result = agent._sanitize_filename(long_name)
    assert len(result) <= 100, "Should truncate to 100 chars"

def test_special_chars():
    agent = YouTubeAgent()
    result = agent._sanitize_filename("Test<>:\"/\\|?*File")
    assert '<' not in result and '>' not in result
    assert '/' not in result and '\\' not in result

test("Empty filename sanitization", test_empty_filename)
test("Very long filename truncation", test_very_long_filename)
test("Special characters removal", test_special_chars)
print()

# Test 2: API Key Handling
print("Testing API Key Handling...")
print("-" * 60)

def test_missing_api_keys():
    import os
    # Temporarily remove keys
    old_gemini = os.environ.pop('GEMINI_API_KEY', None)
    old_youtube = os.environ.pop('YOUTUBE_API_KEY', None)

    from utils.ui import UI
    agent = YouTubeAgent()
    ui = UI()

    # Should return False when keys missing
    result = agent._check_api_keys(ui)
    assert result == False, "Should return False for missing keys"

    # Restore
    if old_gemini:
        os.environ['GEMINI_API_KEY'] = old_gemini
    if old_youtube:
        os.environ['YOUTUBE_API_KEY'] = old_youtube

test("Missing API keys handled gracefully", test_missing_api_keys)
print()

# Test 3: File Operations
print("Testing File Operations...")
print("-" * 60)

def test_save_empty_content():
    agent = YouTubeAgent()
    agent.save_to_knowledge_base("empty.txt", "")
    content = agent.load_from_knowledge_base("empty.txt")
    assert content == "", "Should save and load empty content"
    (agent.knowledge_base_path / "empty.txt").unlink()

def test_unicode_content():
    agent = YouTubeAgent()
    unicode_text = "Hello 世界 🌍 Привет"
    agent.save_to_knowledge_base("unicode.txt", unicode_text)
    content = agent.load_from_knowledge_base("unicode.txt")
    assert content == unicode_text, "Should handle unicode"
    (agent.knowledge_base_path / "unicode.txt").unlink()

test("Save empty content", test_save_empty_content)
test("Unicode content handling", test_unicode_content)
print()

# Test 4: Registry Edge Cases
print("Testing Registry Edge Cases...")
print("-" * 60)

from agents.base import AgentRegistry

def test_register_duplicate():
    registry = AgentRegistry()
    agent = YouTubeAgent()

    registry.register(agent)
    # Register again - should overwrite
    registry.register(agent)

    agents = registry.list_agents()
    assert len(agents) == 1, "Duplicate registration should overwrite"

def test_unregister_nonexistent():
    registry = AgentRegistry()
    # Should not crash
    registry.unregister("nonexistent")
    assert True

test("Duplicate agent registration", test_register_duplicate)
test("Unregister non-existent agent", test_unregister_nonexistent)
print()

# Test 5: Configuration Edge Cases
print("Testing Configuration Edge Cases...")
print("-" * 60)

from agents.base import AgentConfig

def test_config_defaults():
    config = AgentConfig(
        id="test",
        name="Test",
        description="Test",
        personality="Test",
        system_prompt="Test"
    )
    # Check defaults
    assert config.model == "gemini-1.5-pro"
    assert config.temperature == 0.7
    assert config.mcp_servers == []
    assert config.tools == []

def test_config_custom_values():
    config = AgentConfig(
        id="test",
        name="Test",
        description="Test",
        personality="Test",
        system_prompt="Test",
        model="gemini-1.5-flash",
        temperature=0.5,
        mcp_servers=["server1"],
        tools=["tool1"]
    )
    assert config.model == "gemini-1.5-flash"
    assert config.temperature == 0.5
    assert len(config.mcp_servers) == 1
    assert len(config.tools) == 1

test("Config default values", test_config_defaults)
test("Config custom values", test_config_custom_values)
print()

# Test 6: Path Handling
print("Testing Path Handling...")
print("-" * 60)

def test_knowledge_base_path_creation():
    agent = YouTubeAgent()
    # Path should exist
    assert agent.knowledge_base_path.exists()
    assert agent.knowledge_base_path.is_dir()

def test_nested_path_creation():
    from agents.base import BaseAgent, AgentConfig

    config = AgentConfig(
        id="test_nested",
        name="Test",
        description="Test",
        personality="Test",
        system_prompt="Test",
        knowledge_base_path=Path("data/nested/deep/path")
    )

    class TestAgent(BaseAgent):
        def run(self, ui):
            pass

    agent = TestAgent(config)
    assert agent.knowledge_base_path.exists()

    # Cleanup
    import shutil
    shutil.rmtree(Path("data/nested"), ignore_errors=True)

test("Knowledge base path creation", test_knowledge_base_path_creation)
test("Nested path creation", test_nested_path_creation)
print()

# Summary
print("=" * 60)
print("EDGE CASE TEST SUMMARY")
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
