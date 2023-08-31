from docx import Document
from docx.shared import Inches


def make_docx(output_filename, params, MEM_FILES, picture_size):
    (MF_RSD, MF_RLD, MF_RLD_ON_RSD, MF_MT) = MEM_FILES

    (serial_number, date, instrument_name) = params

    document = Document()

    document.add_heading('Протокол температурных испытаний прибора', 1)


    document.add_paragraph(f'Прибор                  {serial_number}', style='List Number')
    document.add_paragraph(f'Канал                 {instrument_name}', style='List Number')
    document.add_paragraph(f'Дата испытаний          {date}', style='List Number')
    document.add_paragraph('Пороги                    (ADCS   ADCL?)', style='List Number')

    document.add_paragraph('RSD', style='List Number')
    document.add_picture(MF_RSD, width=Inches(picture_size))

    document.add_paragraph('RLD', style='List Number')
    document.add_picture(MF_RLD, width=Inches(picture_size))

    document.add_paragraph('RLD/RSD', style='List Number')
    document.add_picture(MF_RLD_ON_RSD, width=Inches(picture_size))

    document.add_paragraph('TEMPER', style='List Number')
    document.add_picture(MF_MT, width=Inches(picture_size))

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

    # table.style = ''

    document.add_paragraph('Выводы', style='List Number')
    document.add_paragraph(
        'Температурный уход сигналов RSD,  RLD  и  RLD/RSD  в диапазоне температур от 64 до 130 градусов не превышает 5%.'
    )

    document.add_paragraph()

    document.add_paragraph(
        'Начальник КО-1                               А.Н. Петров'
    )
    document.add_paragraph(
        'Составил:                                    А.Б. Овчаренко'
    )

    try:
        document.save(f'{output_filename}.docx')
        print("docx successfully saved")
    except:
        print("ERROR: failed to save, please close document <NAME>")
