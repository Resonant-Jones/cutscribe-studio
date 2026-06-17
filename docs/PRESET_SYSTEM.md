# Preset System

Caption presets are stored as JSON files in the `presets/` directory. They define styling and lightweight scoring hints.

## Preset goals

- Make caption styling reusable.
- Keep presets inspectable and portable.
- Support active-word captions later without changing the storage model.
- Allow heuristic scoring to choose the best preset for a specific video.

## Example shape

```json
{
  "id": "classic-bold",
  "name": "Classic Bold",
  "description": "High-contrast creator captions for general use.",
  "style": {
    "font_family": "Arial",
    "font_size": 64,
    "primary_color": "#FFFFFF",
    "outline_color": "#000000",
    "highlight_color": "#FFD54A",
    "stroke_width": 4,
    "shadow": 2,
    "position": "bottom_center",
    "uppercase": false,
    "max_words_on_screen": 5
  },
  "scoring_hints": {
    "prefers_dark_background": 0.6,
    "prefers_bright_background": 0.2,
    "clutter_tolerance": 0.8
  }
}
```

## Scoring hints

The scaffold supports these hints:

- `prefers_dark_background`: higher means the preset tends to read best on darker video.
- `prefers_bright_background`: higher means the preset tends to read best on brighter video.
- `clutter_tolerance`: higher means the preset can survive busy bottom-thirds.

These are intentionally simple. They are scaffolding for a future scoring system, not a final aesthetic oracle in a velvet cape.
