#!/usr/bin/env python3
"""
Multi-Agent CLI System
A terminal-based CLI for running various specialized AI agents with different tasks.
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.base import AgentRegistry
from agents.youtube_agent import YouTubeAgent
from utils.ui import UI, Color


def main():
    """Main entry point for the Multi-Agent CLI."""
    ui = UI()

    # Display banner
    ui.clear_screen()
    ui.print_banner()

    # Initialize agent registry
    registry = AgentRegistry()

    # Register available agents
    registry.register(YouTubeAgent())
    # Future agents will be registered here:
    # registry.register(WebScraperAgent())
    # registry.register(UIBuilderAgent())

    while True:
        try:
            # Display main menu
            ui.print_header("MAIN MENU")
            agents = registry.list_agents()

            print("\nAvailable Agents:")
            for idx, agent_info in enumerate(agents, 1):
                print(f"  {Color.CYAN}{idx}.{Color.RESET} {agent_info['name']}")
                print(f"     {Color.GRAY}{agent_info['description']}{Color.RESET}")
                print()

            print(f"  {Color.CYAN}0.{Color.RESET} Exit")
            print()

            # Get user choice
            choice = ui.get_input("Select an agent (number)")

            if choice == "0":
                ui.print_success("Goodbye!")
                break

            try:
                agent_idx = int(choice) - 1
                if 0 <= agent_idx < len(agents):
                    agent_id = agents[agent_idx]['id']
                    agent = registry.get_agent(agent_id)

                    # Run the selected agent
                    ui.clear_screen()
                    agent.run(ui)

                    # Wait for user before returning to menu
                    ui.get_input("\nPress Enter to return to main menu")
                    ui.clear_screen()
                else:
                    ui.print_error("Invalid selection. Please try again.")
                    ui.pause(1)
            except ValueError:
                ui.print_error("Please enter a valid number.")
                ui.pause(1)

        except KeyboardInterrupt:
            print("\n")
            ui.print_warning("Operation cancelled by user.")
            confirm = ui.get_input("Return to main menu? (y/n)", default="y")
            if confirm.lower() != 'y':
                ui.print_success("Goodbye!")
                break
            ui.clear_screen()
        except Exception as e:
            ui.print_error(f"An unexpected error occurred: {e}")
            ui.pause(2)


if __name__ == "__main__":
    main()
