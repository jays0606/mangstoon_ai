def edit_panel(panel_number: int, edit_instruction: str) -> dict:
    """Edit a specific panel based on user's chat instruction.

    Args:
        panel_number: Which panel to edit (1-8).
        edit_instruction: What to change (e.g., "change background to Han River").

    Returns:
        dict with updated 'image_url' and 'panel_number'.
    """
    return {
        "status": "edit_panel called",
        "panel_number": panel_number,
        "edit_instruction": edit_instruction,
    }
