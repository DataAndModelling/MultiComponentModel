import matplotlib.pyplot as plt
from logger import get_logger

logger = get_logger()

def plot_serv(car_serviceable,car_breakage):
    """
    plots the servicable and broken cars
    """
    plt.plot(car_breakage)
    plt.plot(car_serviceable)
    # Adding labels and title
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.title('Plot of a List')

    # Show the plot
    plt.show(block=True)


def plot_partnumber_values(data_list, partnumber):
    """
    Plots the values of a given partnumber from the dictionary.

    :param data_dict: Dictionary where keys are partnumbers and values are lists of numbers.
    :param partnumber: The partnumber whose values need to be plotted.
    """
    for data_dict in data_list:
        if partnumber in data_dict:
            plt.plot(data_dict[partnumber])

        else:
            pass
            #logger.info(f"Partnumber '{partnumber}' not found in the dictionary.")
    plt.title(f"Plot for {partnumber}")
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.grid(True)
    plt.show(block=True)


def plot_partnumber_all(data_dict):
    """
    Plots the values of all partnumbers from the dictionary.

    :param data_dict: Dictionary where keys are partnumbers and values are lists of numbers.
    """
    if not data_dict:
        logger.info("The dictionary is empty.")
        return
    for partnumber, values in data_dict.items():
        plt.plot(values, label=partnumber)  # Plot each partnumber with a label

    plt.title("Plot for All Partnumbers")
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.legend()  # Add a legend to differentiate between partnumbers
    plt.grid(True)
    plt.show(block=True)


def plot_budget_serv(budget_list,service_list):
    plt.figure(figsize=(8, 6))
    plt.plot(budget_list, service_list, marker='o', linestyle='-', color='b', label='Service vs Budget')

    # Add labels and title
    plt.xlabel('Budget List')
    plt.ylabel('Service List')
    plt.title('Budget List vs Service List')

    # Add a legend
    plt.legend()

    # Display the plot
    plt.grid(True)
    plt.show(block = True)