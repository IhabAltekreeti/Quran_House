class IntegrityError(Exception):
    """Quranic content/metadata could not be validated. Generation must stop."""


class MediaError(Exception):
    """Audio/video asset is missing, unsafe, or invalid."""


class RenderError(Exception):
    """Rendering failed or cannot be done faithfully (e.g. missing glyphs/shaping)."""
