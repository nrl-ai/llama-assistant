#!/usr/bin/env python3
"""
Test script to demonstrate the custom actions feature.
This script shows how to programmatically manage actions.
"""

import sys

sys.path.insert(0, ".")

from llama_assistant import config


def print_actions():
    """Print all current actions"""
    print("\n=== Current Actions ===")
    sorted_actions = sorted(config.actions, key=lambda x: x.get("order", 999))
    for action in sorted_actions:
        visibility = "✓" if action.get("visible", True) else "✗"
        custom = " [CUSTOM]" if action.get("custom", False) else ""
        print(f"{action['order']}. {visibility} {action['label']} ({action['id']}){custom}")
        print(f"   Prompt: {action['prompt']}")
    print()


def add_custom_action():
    """Add a custom action example"""
    new_action = {
        "id": "translate_spanish",
        "label": "Translate to Spanish",
        "prompt": "Translate the following text to Spanish:",
        "visible": True,
        "order": len(config.actions),
        "custom": True,
    }

    # Check if already exists
    if any(a["id"] == new_action["id"] for a in config.actions):
        print(f"Action '{new_action['id']}' already exists!")
        return False

    config.actions.append(new_action)
    config.save_actions()
    print(f"✓ Added custom action: {new_action['label']}")
    return True


def hide_action(action_id):
    """Hide an action by ID"""
    for action in config.actions:
        if action["id"] == action_id:
            action["visible"] = False
            config.save_actions()
            print(f"✓ Hidden action: {action['label']}")
            return True
    print(f"✗ Action '{action_id}' not found!")
    return False


def show_action(action_id):
    """Show an action by ID"""
    for action in config.actions:
        if action["id"] == action_id:
            action["visible"] = True
            config.save_actions()
            print(f"✓ Shown action: {action['label']}")
            return True
    print(f"✗ Action '{action_id}' not found!")
    return False


def main():
    print("=== Llama Assistant - Custom Actions Test ===")
    print(f"Actions file: {config.actions_file}")

    # Show current actions
    print_actions()

    # Add a custom action
    print("\n--- Adding Custom Action ---")
    add_custom_action()
    print_actions()

    # Hide an action
    print("\n--- Hiding 'brainstorm' Action ---")
    hide_action("brainstorm")
    print_actions()

    # Show it again
    print("\n--- Showing 'brainstorm' Action ---")
    show_action("brainstorm")
    print_actions()

    print("✓ Test completed successfully!")
    print("\nNote: Changes are saved to ~/llama_assistant/actions.json")
    print("You can manage actions via Settings > Manage Actions in the UI")


if __name__ == "__main__":
    main()
