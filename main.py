import math
import csv

from tabulate import tabulate

VALUES_FOR_BASE = {2: 2.8, 3: 6.1, 4: 5.3}
VALUES_FOR_GLASS = {2: {"width": 7.1, "height": 11.6}, 3: {"width_gg": 5.7, "width": 7.1, "height": 11.6}, 4: {"width": 7.1, "height": 11.6}}
HEADERS = ["Ambiente", "Riel Superior", "Riel Inferior", "Jamba (x2)", "Pierna", "Gancho", "Zocalo (x2)", "Alto Vidrio", "Ancho Vidrio", "Ancho GG Vidrio"]
HEADERS_ESTIMATES = ["Perfil", "Cantidad"]
ALUMINIUM_SIZE = 600 # This would be the size of the aluminium that is the store the metric is in CM (centimeters)
FILE_NAME = "metrics.csv"

def is_valid_number(value):
    try:
        float(value)
        return True or value.isdigit()
    except ValueError:
        return False

def process_metrics(metrics):
    updated_metrics = []
    for metric in metrics:
        updated_metric = calculate_frame(**metric)
        updated_metric = calculate_window_frame(**updated_metric)
        updated_metric = calculate_glass(**updated_metric)
        updated_metrics.append(updated_metric)

    return updated_metrics


def calculate_frame(**kwargs):
    print(f"[+] Calculando el Marco para {kwargs.get("name")} con Altura {kwargs.get("height")} y Ancho {kwargs.get("width")}")
    rail_sup = kwargs.get("width") - 1.8
    rail_inf = kwargs.get("width") - 1.8
    jamba = kwargs.get("height") - 0.3

    kwargs["rail_sup"] = rail_sup
    kwargs["rail_inf"] = rail_inf
    kwargs["jamba"] = jamba
    
    return kwargs

def calculate_window_frame(**kwargs):
    print(f"[+] Calculando el Marco de Ventana para {kwargs.get("window_num")} hojas")
    leg, hook = kwargs.get("jamba") - 3.4, kwargs.get("jamba") - 3.4
    base = 0
    window_num = kwargs.get("window_num")

    base = (kwargs.get("rail_inf") + VALUES_FOR_BASE.get(window_num)) / window_num

    kwargs["leg"] = leg
    kwargs["hook"] = hook
    kwargs["base"] = base

    return kwargs

def calculate_glass(**kwargs):
    base = kwargs.get("base")
    hook = kwargs.get("hook")
    window_num = kwargs.get("window_num")
    glass_width_gg = base - VALUES_FOR_GLASS.get(window_num).get("width_gg") if window_num == 3 else 0
    glass_width = base - VALUES_FOR_GLASS.get(window_num).get("width")
    glass_height = hook - VALUES_FOR_GLASS.get(window_num).get("height")

    kwargs["glass_width_gg"] = glass_width_gg
    kwargs["glass_width"] = glass_width
    kwargs["glass_height"] = glass_height

    return kwargs
    

def show_metrics(metrics):
    data = []
    for metric in metrics:
        print_data = []
        print_data.append(metric.get("name"))
        print_data.append(metric.get("rail_sup"))
        print_data.append(metric.get("rail_inf"))
        print_data.append(metric.get("jamba"))
        print_data.append(metric.get("leg"))
        print_data.append(metric.get("hook"))
        print_data.append(metric.get("base"))
        print_data.append(metric.get("glass_height"))
        print_data.append(metric.get("glass_width"))
        print_data.append(metric.get("glass_width_gg"))
        data.append(print_data)

    print("------------------------------------------------------------------------------------------------------------")
    print("[+]                                       Medidas para los Cortes                                           ")
    print(tabulate(data, headers=HEADERS, tablefmt="grid"))
    print("------------------------------------------------------------------------------------------------------------")

def show_estimates(totals):
    data = []
    for key, value in totals.items():
        data.append((key, value))

    print("------------------------------------------------------------------------------------------------------------")
    print("[+]                                     Cotizacion Aluminio Line 25                                         ")
    print(tabulate(data, headers=HEADERS_ESTIMATES, tablefmt="grid"))
    print("------------------------------------------------------------------------------------------------------------")

def calculate_estimate(metrics):
    totals = {}
    for metric in metrics:
        window_num = metric.get("window_num")
        totals["rail_sup"] = metric.get("rail_sup") + totals.get("rail_sup", 0)
        totals["rail_inf"] = metric.get("rail_inf") + totals.get("rail_inf", 0)
        totals["jamba"] = (metric.get("jamba") * 2) + totals.get("jamba", 0)
        totals["leg"] = (metric.get("leg") * window_num) + totals.get("leg", 0)
        totals["hook"] = (metric.get("hook") * window_num) + totals.get("hook", 0)
        totals["base"] = (metric.get("base") * (window_num * window_num)) + totals.get("base", 0)
    
    totals["rail_sup_quantity"] = math.ceil(totals.get("rail_sup") / ALUMINIUM_SIZE)
    totals["rail_inf_quantity"] = math.ceil(totals.get("rail_inf") / ALUMINIUM_SIZE)
    totals["jamba_quantity"] = math.ceil(totals.get("jamba") / ALUMINIUM_SIZE)
    totals["leg_quantity"] = math.ceil(totals.get("leg") / ALUMINIUM_SIZE)
    totals["hook_quantity"] = math.ceil(totals.get("hook") / ALUMINIUM_SIZE)
    totals["base_quantity"] = math.ceil(totals.get("base") / ALUMINIUM_SIZE)

    return totals

def enter_data_from_cmd():
    run = True
    result = []
    height, width = 0, 0
    name = ""

    while run:
        metrics = {}    
        height = input("[+] Ingrese la Altura: ")
        if not is_valid_number(height):
            print("[-] Ingrese una Altura valida")
        width = input("[+] Ingrese el Ancho: ")
        if not is_valid_number(width):
            print("[-] Ingrese un Ancho valida")
        window_num = input("[+] Ingresa el numero de ventanas (2, 3, 4): ")
        if not is_valid_number(window_num) and window_num > 4 and window_num < 2:
            print("[-] Ingrese un numero valido de ventanas.")
        name = input("[+] Ingrese nombre del ambiente (opcional): ")
        
        option = input("Quieres agregar mas medidas (si/no): ")
        
        if option.lower() != "si":
            run = False

        metrics["name"] = name
        metrics["height"] = float(height)
        metrics["width"] = float(width)
        metrics["window_num"] = int(window_num)

        result.append(metrics)

    return result

def read_from_csv_file():
    result = []
    with open(FILE_NAME, mode='r') as file:
        csv_file = csv.reader(file)
        for line in list(csv_file)[1:]:
            metrics = {}
            metrics["name"] = line[0]
            metrics["height"] = float(line[1])
            metrics["width"] = float(line[2])
            metrics["window_num"] = int(line[3])

            result.append(metrics)

    return result

if __name__ == "__main__":
    from_file = input("Leer Archivo (Si/No): ")
    if from_file.lower() == 'si':
        metrics = read_from_csv_file()
    else:
        metrics = enter_data_from_cmd()
    updated_metrics = process_metrics(metrics)
    estimates = calculate_estimate(updated_metrics)

    show_metrics(updated_metrics)
    show_estimates(estimates)