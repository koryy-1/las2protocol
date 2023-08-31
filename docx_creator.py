from docx import Document
from docx.shared import Inches


def make_docx():
    document = Document()

    document.add_heading('Протокол температурных испытаний прибора', 2)


    document.add_paragraph('Прибор', style='List Number')
    document.add_paragraph('Канал', style='List Number')
    document.add_paragraph('Дата испытаний', style='List Number')
    document.add_paragraph('Пороги', style='List Number')

    document.add_paragraph('RSD', style='List Number')
    document.add_picture('RSD.png', width=Inches(7))

    document.add_paragraph('RLD', style='List Number')
    document.add_picture('RLD.png', width=Inches(7))

    document.add_paragraph('RLD/RSD', style='List Number')
    document.add_picture('RLD_on_RSD.png', width=Inches(7))

    document.add_paragraph('TEMPER', style='List Number')
    document.add_picture('TEMPER.png', width=Inches(7))

    document.add_paragraph('Результаты', style='List Number')

    records = (
        (3, '101', 'Spam'),
        (7, '422', 'Eggs'),
        (4, '631', 'Spam, spam, eggs, and spam')
    )

    table = document.add_table(rows=1, cols=3)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Qty'
    hdr_cells[1].text = 'Id'
    hdr_cells[2].text = 'Desc'
    for qty, id, desc in records:
        row_cells = table.add_row().cells
        row_cells[0].text = str(qty)
        row_cells[1].text = id
        row_cells[2].text = desc

    table.style = 'LightShading-Accent1'

    document.add_paragraph('Выводы', style='List Number')
    document.add_paragraph(
        'Температурный уход сигналов RSD,  RLD  и  RLD/RSD  в диапазоне температур от 64 до 130 градусов не превышает 5%.'
    )

    document.add_paragraph(
        'Начальник КО-1                               А.Н. Петров'
    )
    document.add_paragraph(
        'Составил:                                    А.Б. Овчаренко'
    )

    try:
        document.save('serial_number_date.docx')
        print("docx successfully saved")
    except:
        print("ERROR: failed to save, please close document <NAME>")
