def decompose_story(user_story: str, character_description: str) -> dict:
    """Break a user's fantasy story into 6-8 webtoon panel descriptions.

    Args:
        user_story: The user's delusion/fantasy scenario in free text.
        character_description: Visual description of the main character.

    Returns:
        dict with 'panels' list, each containing scene, dialogue, and image_prompt.
    """
    return {
        "status": "decompose_story called",
        "user_story": user_story,
        "character_description": character_description,
    }
