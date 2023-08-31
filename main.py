import os
import lasio

from docx_creator import make_docx

from plot_creator import create

if __name__ == "__main__":
    # fulPath = r"C:/Users/Андрей/Desktop/Ilya/19399001 2023-07-27 09-46-50 ГГКП.rt.las"
    # print(fulPath)
    # cwd = os.getcwd()

    filename = "19399001 2023-07-27 09-46-50 ГГКП.rt.las"
    las = lasio.read(f"C:/Users/Андрей/Desktop/Ilya/{filename}")
    Keys=las.keys()
    print(Keys)
    print(os.getcwd())

    RSD_data = dict(x=las["RSD"],y=las["MT"])
    create(RSD_data, "RSD_1", "RSD")

    RLD_data = dict(x=las["RLD"],y=las["MT"])
    create(RLD_data, "RLD_1", "RLD")

    RLD_on_RSD_data = dict(x=las["RLD"],y=las["MT"])
    create(RLD_on_RSD_data, "RLD/RSD", "RLD_on_RSD")

    temp_data = dict(x=las["TIME"],y=las["MT"])
    create(temp_data, "TEMPER", "TEMPER")

    make_docx()

    # las.to_excel('output.xlsx')