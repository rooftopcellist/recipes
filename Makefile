.PHONY: help setup-automation run-automation

help:
	@echo "Available targets:"
	@echo "  setup-automation  - Set up the recipe automation environment"
	@echo "  run-automation    - Run the recipe automation script"

# Recipe automation targets
setup-automation:
	@echo "Setting up recipe automation environment..."
	cd recipe_automation && python3 -m venv venv
	cd recipe_automation && . venv/bin/activate && pip install -r requirements.txt
	@echo "Setup complete. Make sure to set GITHUB_TOKEN environment variable."

run-automation:
	@echo "Running recipe automation..."
	cd recipe_automation && . venv/bin/activate && python main.py

