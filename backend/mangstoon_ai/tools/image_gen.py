def generate_panel(image_prompt: str, panel_number: int) -> dict:
    """Generate a single webtoon panel image using Gemini 3.1 Flash Image.

    Args:
        image_prompt: Detailed prompt for the panel image in Korean webtoon style.
        panel_number: Panel position (1-8) in the webtoon sequence.

    Returns:
        dict with 'image_url' and 'panel_number'.
    """
    return {
        "status": "generate_panel called",
        "image_prompt": image_prompt,
        "panel_number": panel_number,
    }
