import base64
import io
from typing import Literal

import openai
from PIL import Image
from pydantic import BaseModel, Field


class ClickAbsoluteAction(BaseModel):
    """Click at absolute coordinates."""

    action: Literal["click_absolute"] = "click_absolute"
    x: int = Field(description="The x coordinate, number of pixels from the left edge.")
    y: int = Field(description="The y coordinate, number of pixels from the top edge.")


def create_localization_prompt(component: str) -> str:
    """Creates the localization prompt with JSON schema."""
    return f"""You are a precise UI element locator. Your task is to find the EXACT center coordinates of a specific interactive element on a webpage screenshot.

CRITICAL INSTRUCTIONS:
1. Identify the EXACT interactive element (input field, button, link, etc.) - not its container or label
2. For INPUT FIELDS: Return coordinates at the CENTER of the input box itself (the white/colored rectangle where text is typed)
3. For BUTTONS: Return coordinates at the CENTER of the clickable button area
4. IGNORE labels, placeholders text positions, and surrounding divs
5. Be EXTREMELY PRECISE - even 10-20 pixels off will cause the click to miss the element
6. If you see a form field with a placeholder like "Benutzername *" or "Passwort", click the CENTER of the actual input box, NOT the text

VISUAL IDENTIFICATION TIPS:
- Input fields usually have a border/outline and a light background
- They are rectangular boxes where users can type
- The placeholder text is INSIDE the input field
- Click the geometric center of this rectangular box

TARGET ELEMENT TO LOCALIZE:
{component}

OUTPUT FORMAT:
You must output valid JSON with x,y coordinates: {ClickAbsoluteAction.model_json_schema()}

Remember: Precision is critical. The coordinates must land exactly on the interactive element."""


def resize_image_for_localization(image: Image.Image, target_size: tuple[int, int] = (1000, 500)) -> Image.Image:
    """Resize image for localization preserving aspect ratio with padding."""
    target_width, target_height = target_size
    original_width, original_height = image.size
    
    # Calculate scaling factor to fit within target size while preserving aspect ratio
    scale = min(target_width / original_width, target_height / original_height)
    
    # Calculate new dimensions
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)
    
    # Resize image
    resized = image.resize((new_width, new_height), resample=Image.Resampling.LANCZOS)
    
    # Create new image with target size and paste resized image centered
    result = Image.new('RGB', target_size, (0, 0, 0))
    paste_x = (target_width - new_width) // 2
    paste_y = (target_height - new_height) // 2
    result.paste(resized, (paste_x, paste_y))
    
    return result


def localization_request(image: Image.Image, element_name: str, model: str, temperature: float = 0.0) -> dict:
    """Creates a localization request with structured JSON output."""
    
    # Resize image using simple resize instead of smart_resize
    resized_image = resize_image_for_localization(image)
    
    # Create prompt text
    localization_prompt = create_localization_prompt(element_name)
    
    # Convert image to JPEG saved as base64
    image_bytes = io.BytesIO()
    resized_image.save(image_bytes, format="JPEG", quality=90)
    image_base64 = base64.b64encode(image_bytes.getvalue()).decode("utf-8")
    
    # Create openai request with structured output
    openai_request = {
        "messages": [
            {
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"detail": "auto", "url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                    {"type": "text", "text": localization_prompt},
                ],
                "role": "user",
            },
        ],
        "model": model,
        "temperature": temperature,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "click_absolute_action",
                "schema": ClickAbsoluteAction.model_json_schema(),
                "strict": True
            }
        },
    }
    return openai_request


def parse_localization_response(completion, original_image: Image.Image, resized_image: Image.Image) -> tuple[int, int]:
    """Parses the JSON localization response and scales coordinates back to original image size."""
    
    # Parse JSON response into ClickAbsoluteAction model
    response_content = completion.choices[0].message.content
    click_action = ClickAbsoluteAction.model_validate_json(response_content)
    
    # Get image dimensions
    original_width, original_height = original_image.size
    resized_width, resized_height = resized_image.size
    
    # Calculate the actual content area (without padding)
    scale = min(resized_width / original_width, resized_height / original_height)
    content_width = int(original_width * scale)
    content_height = int(original_height * scale)
    pad_x = (resized_width - content_width) // 2
    pad_y = (resized_height - content_height) // 2
    
    import sys
    sys.stderr.write(f"\n🔍 LOCALIZATION DEBUG:\n")
    sys.stderr.write(f"   Original: {original_width}x{original_height}, Resized: {resized_width}x{resized_height}\n")
    sys.stderr.write(f"   Content area: {content_width}x{content_height}, Padding: ({pad_x}, {pad_y})\n")
    sys.stderr.write(f"   Model coords: x={click_action.x}, y={click_action.y}\n")
    sys.stderr.flush()
    
    # Remove padding offset
    content_x = click_action.x - pad_x
    content_y = click_action.y - pad_y
    
    # Scale back to original size
    original_x = int(content_x / scale)
    original_y = int(content_y / scale)
    
    sys.stderr.write(f"   Scaled coords: x={original_x}, y={original_y}\n\n")
    sys.stderr.flush()
    
    # Ensure coordinates are within bounds
    original_x = max(0, min(original_x, original_width - 1))
    original_y = max(0, min(original_y, original_height - 1))
    
    return (original_x, original_y)


def localize_element(
    image: Image.Image, element_name: str, openai_client: openai.OpenAI, model: str, temperature: float = 0.0
) -> tuple[int, int]:
    """Localizes an element and returns coordinates in the original image dimensions."""
    
    # Create resized image for processing
    resized_image = resize_image_for_localization(image)
    
    # Create the request
    request_data = localization_request(image=image, element_name=element_name, model=model, temperature=temperature)
    
    # Get response from OpenAI
    response = openai_client.chat.completions.create(**request_data)
    
    # Parse response and scale coordinates back to original image
    return parse_localization_response(response, original_image=image, resized_image=resized_image)


def localize_element_structured(
    image: Image.Image, element_name: str, openai_client: openai.OpenAI, model: str, temperature: float = 0.0
) -> ClickAbsoluteAction:
    """Localizes an element and returns the structured ClickAbsoluteAction with original image coordinates."""
    
    coordinates = localize_element(image, element_name, openai_client, model, temperature)
    
    return ClickAbsoluteAction(x=coordinates[0], y=coordinates[1])
