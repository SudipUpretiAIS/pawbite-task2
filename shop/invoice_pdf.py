from io import BytesIO
from decimal import Decimal
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def build_invoice_pdf(user, orders, invoice_number):
    out = BytesIO()
    styles = getSampleStyleSheet()
    story = [Paragraph('PawBite Invoice ' + escape(str(invoice_number)), styles['Title']),
             Paragraph('Customer: ' + escape(user.username), styles['Normal']),
             Paragraph(escape(user.email), styles['Normal']), Spacer(1, 18)]
    rows = [['Product', 'Qty', 'Line total']]
    total = Decimal('0')
    for order in orders:
        line = Decimal(str(order.price))
        total += line
        rows.append([Paragraph(escape(order.product.name), styles['Normal']), str(order.quantity), f'{line:.2f}'])
    rows.append(['Total for ordered products', '', f'{total:.2f}'])
    t = Table(rows, colWidths=[330, 50, 110], repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                           ('GRID', (0, 0), (-1, -1), .5, colors.lightgrey),
                           ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                           ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
    story.append(t)
    story.append(Spacer(1, 12))
    story.append(Paragraph('Assessment demonstration. No online payment was processed.', styles['Normal']))
    SimpleDocTemplate(out).build(story)
    return out.getvalue()
