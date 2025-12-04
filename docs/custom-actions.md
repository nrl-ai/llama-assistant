# Custom Actions Feature

## Overview
The Custom Actions feature allows you to create, edit, hide, and reorder action buttons in the Llama Assistant interface. Actions are quick shortcuts that prepend a specific prompt to your input text.

## Accessing Actions Management
1. Open Settings (via system tray icon)
2. Look for the "Actions Settings" section
3. Click "Manage Actions" button

## Features

### 1. Create Custom Actions
- Click "Add Action" after filling in the form
- **ID**: Unique identifier (no spaces, e.g., `translate_spanish`)
- **Label**: Button text shown in the UI (e.g., `Translate to Spanish`)
- **Prompt**: Instruction sent to the AI before your input (e.g., `Please translate the following text to Spanish:`)
- **Visible**: Toggle to show/hide the action button

**How it works**: When you click an action button, the prompt is combined with your input text and sent to the AI. For example:
- Your input: "Hello, how are you?"
- Action prompt: "Please translate the following text to Spanish:"
- Sent to AI: "Please translate the following text to Spanish:\n\nHello, how are you?"

### 2. Edit Actions
- Select an action from the list
- Modify any field (ID, Label, Prompt, Visibility)
- Click "Update Action" to save changes

### 3. Reset Default Actions
- Select a default action (Summarize, Rephrase, Fix Grammar, Brainstorm, Write Email)
- Click "Reset to Default" to restore original prompt and settings
- Custom actions cannot be reset (use Remove instead)

### 4. Hide/Show Actions
- Select an action
- Uncheck "Visible" checkbox
- Click "Update Action"
- Hidden actions won't appear in the UI but remain in your configuration

### 5. Reorder Actions
- Drag and drop actions in the list to reorder them
- The order in the list determines the button order in the UI
- Changes are saved when you click "Close"

### 6. Remove Actions
- Select an action
- Click "Remove Action"
- Confirmation will be shown
- Default actions can be removed but can be re-added manually

## Configuration File
Actions are stored in: `~/llama_assistant/actions.json`

Example structure:
```json
{
  "actions": [
    {
      "id": "summarize",
      "label": "Summarize",
      "prompt": "Please provide a concise summary of the following text:",
      "visible": true,
      "order": 0
    },
    {
      "id": "translate_spanish",
      "label": "Translate to Spanish",
      "prompt": "Please translate the following text to Spanish:",
      "visible": true,
      "order": 5,
      "custom": true
    }
  ]
}
```

## Tips
- Use descriptive IDs for easy identification
- Keep labels short for better UI appearance
- Write clear, specific prompts that instruct the AI what to do
- Start prompts with "Please" for better AI responses
- End prompts with a colon or clear instruction (e.g., "Please translate the following text to Spanish:")
- Test your custom prompts to ensure they work as expected
- Hidden actions can be quickly re-enabled without recreating them
- Reorder frequently used actions to the front for quick access

## Example Prompts
- **Translate**: "Please translate the following text to [language]:"
- **Explain**: "Please explain the following concept in simple terms:"
- **Code Review**: "Please review the following code and suggest improvements:"
- **Make Formal**: "Please rewrite the following text in a more formal tone:"
- **Simplify**: "Please simplify the following text for a general audience:"
