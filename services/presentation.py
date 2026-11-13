from io import BytesIO
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

def make_presentation(paper_name: str, outline: str) -> bytes:
    prs = Presentation()
    prs.core_properties.title = f"Presentation: {paper_name}"
    slides = []
    current_title, bullets = None, []
    def flush():
        if current_title:
            slides.append((current_title, bullets.copy()))
    for line in outline.splitlines():
        line = line.strip()
        if line.startswith("## Slide") or line.startswith("### Slide"):
            flush(); current_title = line.split(":", 1)[-1].strip() or line; bullets = []
        elif line.startswith(("-", "*", "•")):
            bullets.append(line.lstrip("-*• "))
        elif line and current_title and not line.startswith("#"):
            bullets.append(line)
    flush()
    if not slides:
        slides = [(paper_name, [line.strip(" -*•") for line in outline.splitlines() if line.strip()][:8])]
    for title, items in slides:
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = title[:100]
        slide.shapes.title.text_frame.paragraphs[0].font.color.rgb = RGBColor(26, 75, 115)
        body = slide.placeholders[1].text_frame
        body.clear()
        for idx, item in enumerate(items[:7]):
            p = body.paragraphs[0] if idx == 0 else body.add_paragraph()
            p.text = item[:350]; p.level = 0; p.font.size = Pt(20)
    output = BytesIO(); prs.save(output); return output.getvalue()
