"""Render the report with ReportLab; optional dependency used only for PDF."""
import html
import re
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

p = Path(__file__).parent
source = (p / 'paper.md').read_text()
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='PaperTitle', fontName='Helvetica-Bold', fontSize=21,
                         leading=25, spaceAfter=18, textColor=colors.HexColor('#173a50')))
styles.add(ParagraphStyle(name='BodyPaper', fontName='Times-Roman', fontSize=10.8,
                         leading=14.5, spaceAfter=8))
styles['Heading2'].fontName = 'Helvetica-Bold'
styles['Heading2'].fontSize = 12
styles['Heading2'].spaceBefore = 14
styles['Heading2'].keepWithNext = True
styles['Heading2'].textColor = colors.HexColor('#173a50')
styles.add(ParagraphStyle(name='CellPaper', fontSize=8, leading=11))

def clean(s):
    s = s.replace('中', 'U+4E2D').replace('😀', 'U+1F600')
    s = s.replace('·', '|').replace('’', "'")
    s = html.escape(s)
    s = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', s)
    return s

story = []
table = []
def flush_table():
    if not table: return
    cells = [[Paragraph(clean(x), styles['CellPaper']) for x in row] for row in table]
    t = Table(cells, colWidths=[99, 60, 64, 70, 78, 72], repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e6eff3')),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),7),
        ('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),0.6,colors.grey),
        ('LINEBELOW',(0,1),(-1,-1),0.25,colors.lightgrey)]))
    story.extend([t,Spacer(1,10)]);table.clear()

for block in source.split('\n\n'):
    if block.startswith('|'):
        for line in block.splitlines():
            row = [c.strip() for c in line.strip('|').split('|')]
            if all(re.fullmatch(r'[:\- ]+', c) for c in row): continue
            table.append(row)
        flush_table(); continue
    if block.startswith('# '):
        story.append(Paragraph(clean(block[2:]), styles['PaperTitle']))
    elif block.startswith('## '):
        story.append(Paragraph(clean(block[3:]), styles['Heading2']))
    else:
        story.append(Paragraph(clean(block).replace('  \n','<br/>').replace('\n',' '), styles['BodyPaper']))

def footer(canvas, doc):
    canvas.setStrokeColor(colors.HexColor('#cad5dc'));canvas.line(52,44,543,44)
    canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#475866'))
    canvas.drawString(52,31,'Sami Halawa Ribas | Bounded Tool Results | Technical report v1.0')
    canvas.drawRightString(543,31,str(doc.page))

doc = SimpleDocTemplate(str(p/'paper.pdf'),pagesize=A4,leftMargin=55,rightMargin=55,
                        topMargin=51,bottomMargin=56,title=source.splitlines()[0][2:],
                        author='Sami Halawa Ribas')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(p/'paper.pdf')
