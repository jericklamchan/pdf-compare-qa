from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

OUT = Path("data")
OUT.mkdir(exist_ok=True)
styles = getSampleStyleSheet()


def build(path, pages):
    doc = SimpleDocTemplate(str(path), pagesize=A4)
    story = []
    for i, page in enumerate(pages):
        for kind, text in page:
            style = styles["Heading1"] if kind == "h" else styles["BodyText"]
            story.append(Paragraph(text, style))
            story.append(Spacer(1, 8))
        if i < len(pages) - 1:
            story.append(PageBreak())
    doc.build(story)


spec = [
    [("h", "Structural Design Brief - Requirements"),
     ("p", "Project: Fictional Warehouse Extension. Project start date: 15 March 2026."),
     ("p", "1. Standards. The design shall conform to AS 3600:2018 Concrete structures."),
     ("p", "2. Materials. Characteristic concrete compressive strength f'c shall be 40 MPa. "
           "Reinforcement yield strength shall be 500 MPa. Cover to reinforcement shall be 40 mm.")],
    [("p", "3. Geometry and loads. The maximum beam span shall not exceed 8.0 m. "
           "All loads shall be stated in kN or kPa."),
     ("p", "4. Design life. The design life shall be 50 years."),
     ("p", "5. Required sections. The submission shall include a Site Geotechnical Summary "
           "and a Design Verification Sign-off."),
     ("p", "6. Dates. The project start date shall be stated consistently across the submission.")],
]

submission = [
    [("h", "Beam Design Report"),
     ("p", "Project: Fictional Warehouse Extension. Project start date: 15 March 2026."),
     ("p", "1. Introduction. This report presents the design of the first-floor transfer beam.")],
    [("p", "2. Design basis. The design has been carried out in accordance with "
           "AS 4100:2020 Steel structures."),
     ("p", "3. Materials. Concrete characteristic compressive strength f'c is 32 MPa. "
           "Reinforcement yield strength is 500 MPa. Cover to reinforcement is 40 mm.")],
    [("p", "4. Geometry and loads. The beam span is 9.2 m. The imposed floor load is 3.0 psf. "
           "The design life is 50 years."),
     ("p", "5. Programme. Construction is scheduled to follow a project start date of 12 April 2026.")],
    [("p", "6. Conclusion. The beam is adequate for the stated loads.")],
]

build(OUT / "spec.pdf", spec)
build(OUT / "submission.pdf", submission)
print("wrote data/spec.pdf and data/submission.pdf")