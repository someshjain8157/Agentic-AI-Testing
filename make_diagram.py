from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

width, height = 1600, 900
img = Image.new('RGB', (width, height), 'white')
draw = ImageDraw.Draw(img)

# Background panel
draw.rounded_rectangle((80, 80, 1520, 780), radius=28, fill='#f8fafc', outline='#dbeafe', width=3)

# Title
try:
    font_title = ImageFont.truetype('arial.ttf', 34)
except OSError:
    font_title = ImageFont.load_default()
draw.text((120, 115), 'Agentic AI Testing Framework Workflow', fill='#1e3a8a', font=font_title)

# Boxes
boxes = [
    ('User / Prompt', 120, 220, 280, 320, '#dbeafe', '#1d4ed8'),
    ('Orchestrator', 360, 220, 520, 320, '#dcfce7', '#16a34a'),
    ('DeepEval Agent', 600, 220, 780, 320, '#fef3c7', '#d97706'),
    ('RAGAS Agent', 820, 220, 1000, 320, '#fef3c7', '#d97706'),
    ('PyRIT Agent', 1040, 220, 1220, 320, '#fef3c7', '#d97706'),
    ('Langfuse / Braintrust / Guardrails', 1240, 220, 1480, 320, '#fef3c7', '#d97706'),
    ('Playwright Agent', 680, 420, 920, 520, '#ede9fe', '#7c3aed'),
    ('Results / Reports', 600, 620, 1000, 720, '#fee2e2', '#dc2626'),
]

for title, x1, y1, x2, y2, fill, border in boxes:
    draw.rounded_rectangle((x1, y1, x2, y2), radius=18, fill=fill, outline=border, width=3)
    try:
        font = ImageFont.truetype('arial.ttf', 24)
    except OSError:
        font = ImageFont.load_default()
    text_w, text_h = draw.textbbox((0, 0), title)[2:4]
    draw.text((x1 + (x2 - x1 - text_w) // 2, y1 + (y2 - y1 - text_h) // 2), title, fill=border, font=font)

# Arrows
arrow_color = '#475569'
for x1, y1, x2, y2 in [
    (280, 270, 360, 270),
    (520, 270, 600, 270),
    (780, 270, 820, 270),
    (1000, 270, 1040, 270),
    (1220, 270, 1240, 270),
    (800, 320, 800, 420),
    (800, 520, 800, 620),
]:
    draw.line((x1, y1, x2, y2), fill=arrow_color, width=4)
    draw.polygon([(x2, y2), (x2 - 12, y2 - 10), (x2 - 12, y2 + 10)], fill=arrow_color)

# Labels
try:
    font_small = ImageFont.truetype('arial.ttf', 18)
except OSError:
    font_small = ImageFont.load_default()
draw.text((300, 235), 'input', fill='#64748b', font=font_small)
draw.text((560, 235), 'coordination', fill='#64748b', font=font_small)
draw.text((760, 385), 'browser flow', fill='#64748b', font=font_small)
draw.text((745, 575), 'reports / artifacts', fill='#64748b', font=font_small)

out_path = Path('agentic_testing_workflow.png')
img.save(out_path)
print(out_path.resolve())
