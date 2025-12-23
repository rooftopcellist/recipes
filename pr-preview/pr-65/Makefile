.PHONY: help setup-automation run-automation standardize-image

help:
	@echo "Available targets:"
	@echo "  setup-automation   - Set up the recipe automation environment"
	@echo "  run-automation     - Run the recipe automation script"
	@echo "  standardize-image  - Standardize a local image (IMAGE=path/to/image.jpg)"

# Recipe automation targets
setup-automation:
	@echo "Setting up recipe automation environment..."
	cd recipe_automation && python3 -m venv venv
	cd recipe_automation && . venv/bin/activate && pip install -r requirements.txt
	@echo "Setup complete. Make sure to set GITHUB_TOKEN environment variable."

run-automation:
	@echo "Running recipe automation..."
	cd recipe_automation && . venv/bin/activate && python main.py

# Image standardization target
# Usage: make standardize-image IMAGE=path/to/image.jpg [OUTPUT=path/to/output.jpg] [MAX_WIDTH=1024] [MAX_HEIGHT=768] [FORMAT=JPEG] [QUALITY=95]
standardize-image:
ifndef IMAGE
	$(error IMAGE is required. Usage: make standardize-image IMAGE=path/to/image.jpg)
endif
	@cd recipe_automation && . venv/bin/activate && python image_utils.py "$(abspath $(IMAGE))" \
		$(if $(OUTPUT),-o "$(abspath $(OUTPUT))") \
		$(if $(MAX_WIDTH),--max-width $(MAX_WIDTH)) \
		$(if $(MAX_HEIGHT),--max-height $(MAX_HEIGHT)) \
		$(if $(FORMAT),--format $(FORMAT)) \
		$(if $(QUALITY),--quality $(QUALITY))
