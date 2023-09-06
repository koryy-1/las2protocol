from docx import Document
from docx.shared import Inches
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH


def make_docx(output_filename, params, MEM_FILES, picture_size) -> bool:
    (MF_RSD, MF_RLD, MF_RLD_ON_RSD, MF_MT) = MEM_FILES

    (
        serial_number, 
        date, 
        instrument_name, 
        records, 
        conclusion, 
        T_min, 
        T_max,
        ADCS,
        ADCL,
    ) = params

    document = Document()

    # styles
    style = document.styles['Normal']
    style.font.size = Pt(12)

    p_header = document.add_paragraph()
    p_header.add_run('Протокол').bold = True
    p_header_fmt = p_header.paragraph_format
    p_header_fmt.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_header2 = document.add_paragraph('температурных испытаний прибора')
    p_header2_fmt = p_header2.paragraph_format
    p_header2_fmt.alignment = WD_ALIGN_PARAGRAPH.CENTER


    document.add_paragraph(f'Прибор:                               №: {serial_number}', style='List Number')
    document.add_paragraph(f'Канал:                                   {instrument_name}', style='List Number')
    document.add_paragraph(f'Дата испытаний:                 {date}', style='List Number')
    document.add_paragraph(f'Пороги: RSD - {ADCS} мВ, RLD - {ADCL} мВ. ', style='List Number')

    document.add_paragraph('RSD', style='List Number')
    document.add_picture(MF_RSD, width=Inches(picture_size))

    document.add_paragraph('RLD', style='List Number')
    document.add_picture(MF_RLD, width=Inches(picture_size))

    document.add_paragraph('RLD/RSD', style='List Number')
    document.add_picture(MF_RLD_ON_RSD, width=Inches(picture_size))

    document.add_paragraph('TEMPER', style='List Number')
    document.add_picture(MF_MT, width=Inches(picture_size))

    document.add_paragraph('Результаты при нагреве', style='List Number')


    table = document.add_table(rows=1, cols=5)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'п/п'
    hdr_cells[1].text = 'Формула'
    hdr_cells[2].text = 'RSD'
    hdr_cells[3].text = 'RLD'
    hdr_cells[4].text = 'RLD/RSD'
    # print(records)
    for num, formula, RSD, RLD, RLD_ON_RSD in records:
        row_cells = table.add_row().cells
        row_cells[0].text = str(num)
        row_cells[1].text = formula
        row_cells[2].text = str(RSD)
        row_cells[3].text = str(RLD)
        row_cells[4].text = str(RLD_ON_RSD)

    table.style = 'Table Grid'
    
    document.add_paragraph()

    conc_p = document.add_paragraph(style='List Number')
    conc_p.add_run('Выводы').bold = True
    document.add_paragraph(
        f'Температурный уход сигналов RSD,  RLD  и  RLD/RSD  в диапазоне температур от {T_min} до {T_max} градусов {conclusion} 5%.'
    )

    document.add_paragraph()

    document.add_paragraph(
        'Начальник КО-1                                                                    А.Н. Петров'
    )
    document.add_paragraph(
        'Составил:                                                                               А.Б. Овчаренко'
    )

    try:
        document.save(f'{output_filename}.docx')
        return True
    except:
        return False
