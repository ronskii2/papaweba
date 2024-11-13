from pydantic import BaseModel, UUID4, validator
from typing import Optional, List
from datetime import datetime

VALID_ASPECT_RATIOS = ["1:1", "16:9", "9:16", "4:5", "5:4", "3:2", "2:3"]


VALID_STYLES = {
    "БЕЗ_СТИЛЯ": "",  # Пустой стиль для генерации без фильтров
    "РЕАЛИЗМ": "Cinematic photography, shot on Sony Venice cinema camera, Cooke anamorphic lenses, shallow depth of field, film grain, cinematic lighting, color grading, wide aspect ratio, detailed shadows and highlights",
    "ПЕПЕ": "Pepe the Frog meme art style, MS Paint aesthetics, crude drawings, green frog character, humorous expressions, comic sans text, viral internet meme format, surreal backgrounds",
    "МУЛЬТИК": "3D animated film still, Pixar style, cute stylized characters, expressive facial animations, rich textures, vivid colors, cinematic composition, realistic shading and lighting, renderman rendering",
    "ГРАВЮРА": "Scientific illustration in the style of vintage anatomical etchings, detailed line engravings, monochromatic color scheme, stippled textures, labeled diagrams, educational visuals",
    "АРТ": "Vibrant creative art style, bold color palette, surreal shapes and patterns, abstract elements, painterly textures, dreamy atmosphere, psychedelic vibes, imaginative composition, artistic interpretation",
    "МИНИМАЛИЗМ": "Abstract minimalist landscape, seamless horizon line, blurred boundaries, neutral hues, empty sky, lack of details",
    "ФЛЭТ": "The cat is walking on the roof. Flat vector illustration style for web design, simplified shapes, stylized icons, limited color palette, clean linework, scalable graphics, modern aesthetic, digital art for websites and apps.",
    "КИБЕРПАНК": "Cyberpunk futuristic concept art, neon cybercity environments, advanced technologies, holographic displays, sleek robotic designs, dark dystopian atmospheres, gritty sci-fi aesthetics"
}

class ImageBase(BaseModel):
    prompt: str
    aspect_ratio: str = "1:1"
    style: Optional[str] = None

    @validator('aspect_ratio')
    def validate_aspect_ratio(cls, v):
        if v not in VALID_ASPECT_RATIOS:
            raise ValueError(f"Invalid aspect ratio. Must be one of: {', '.join(VALID_ASPECT_RATIOS)}")
        return v

    @validator('style')
    def validate_style(cls, v):
        if v is not None and v not in VALID_STYLES:
            raise ValueError(f"Invalid style. Must be one of: {', '.join(VALID_STYLES.keys())}")
        return v

class ImageCreate(ImageBase):
    pass

class ImageInDB(ImageBase):
    id: UUID4
    user_id: UUID4
    translated_prompt: str
    image_url: str
    created_at: datetime

    class Config:
        from_attributes = True

class ImageGalleryResponse(BaseModel):
    images: List[ImageInDB]
    total: int
    page: int
    pages: int

    class Config:
        from_attributes = True
