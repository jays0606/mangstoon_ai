"""Single source of truth for all 4 art styles."""

STYLE_PROMPTS: dict[str, str] = {
    "k-webtoon": (
        "Korean webtoon style illustration. Clean digital line art with smooth cel-shading. "
        "Soft gradient coloring with vibrant accents. Large expressive eyes with detailed highlights. "
        "Modern manhwa aesthetic. Single panel illustration. "
        "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
    ),
    "anime": (
        "Japanese anime style illustration. Vibrant colors with clean cel-shading and bold outlines. "
        "Large detailed eyes with colorful iris reflections and highlights. Dynamic hair with flowing strands. "
        "Smooth gradient backgrounds with atmospheric effects. Single panel illustration. "
        "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
    ),
    "comic": (
        "American comic book style illustration. Bold ink outlines with varying line weight. "
        "Rich saturated colors with dramatic cel-shading and strong cast shadows. "
        "Dynamic figure work. Detailed crosshatching in shadow areas. "
        "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
    ),
    "cinematic": (
        "Cinematic Korean manhwa style. Semi-realistic digital painting with detailed "
        "rendering. Dramatic cinematic lighting with volumetric effects. Rich deep color "
        "palette with glowing accent highlights. Detailed background environments. "
        "Painterly brushwork visible in shading. Epic composition. "
        "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
    ),
}

STYLE_CONFIGS: dict[str, dict] = {
    "k-webtoon": {"aspect_ratio": "9:16"},
    "anime": {"aspect_ratio": "3:4"},
    "comic": {"aspect_ratio": "2:3"},
    "cinematic": {"aspect_ratio": "9:16"},
}

STYLE_NAMES: dict[str, str] = {
    "k-webtoon": "Korean Webtoon",
    "anime": "Japanese Anime",
    "comic": "American Comic",
    "cinematic": "Cinematic Manhwa",
}

# Style-specific writer personas for decompose_story
STYLE_WRITERS: dict[str, str] = {
    "k-webtoon": "Korean webtoon writer",
    "anime": "Japanese anime screenwriter",
    "comic": "American comic book writer",
    "cinematic": "cinematic Korean manhwa writer",
}

# Style-specific character design instructions for extract_character
STYLE_CHARACTER_DESIGN: dict[str, str] = {
    "k-webtoon": (
        "Korean webtoon character design. Large expressive eyes with detailed highlights. "
        "Clean digital line art with soft cel-shading. Modern manhwa proportions."
    ),
    "anime": (
        "Japanese anime character design. Large colorful eyes with vibrant iris reflections. "
        "Dynamic flowing hair. Clean cel-shading with bold outlines. Anime proportions."
    ),
    "comic": (
        "American comic book character design. Bold heroic proportions. Strong ink outlines "
        "with dramatic shadow work. Realistic musculature. Western comic aesthetic."
    ),
    "cinematic": (
        "Cinematic manhwa character design. Semi-realistic proportions with detailed rendering. "
        "Painterly shading. Dramatic lighting on face. Manhwa beauty standards."
    ),
}


def get_style_prompt(style_id: str) -> str:
    """Get the style prompt for a given style ID, defaulting to k-webtoon."""
    return STYLE_PROMPTS.get(style_id, STYLE_PROMPTS["k-webtoon"])


def get_style_config(style_id: str) -> dict:
    """Get the style config (aspect_ratio etc.) for a given style ID."""
    return STYLE_CONFIGS.get(style_id, STYLE_CONFIGS["k-webtoon"])


def get_style_writer(style_id: str) -> str:
    """Get the writer persona for a given style ID."""
    return STYLE_WRITERS.get(style_id, STYLE_WRITERS["k-webtoon"])


def get_character_design(style_id: str) -> str:
    """Get character design instruction for a given style ID."""
    return STYLE_CHARACTER_DESIGN.get(style_id, STYLE_CHARACTER_DESIGN["k-webtoon"])
