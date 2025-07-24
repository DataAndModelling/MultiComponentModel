import copy
import math

from logger import get_logger
from classes import Part_physical, Part_attributes, Car
from reader import load_part_attributes, load_blueprints
from mathstuff import gamma_approx, weibull_mean
from runners import do_one_run, do_first_allocation, get_new_service
from plotter import plot_partnumber_all, plot_partnumber_values, plot_budget_serv, plot_serv

logger = get_logger()


# load the data from the worksheet
part_objects = load_part_attributes()
car_blueprint = load_blueprints()

# set mission profile here
hours_per_day = 5
days = 1000
fleet_size = 5

# this get the average number of parts needed on an ongoing basis
# first get the ratio of parts needed in one instance
part_quantities = car_blueprint.get_part_quantities()
# now we need to work out what the MTBF should be
# can be amended if there is also scheduled heavy maintenance - just reduce the MTBF
parts_needed = {}

for key, value in part_quantities.items():
    for parts in Part_attributes.master_list:
        if key == parts.name and parts.depot_tat is not None:
            mtbf = weibull_mean(parts.shape_factor, parts.failure_hours)
            zero_stoppages = value * fleet_size / mtbf * parts.depot_tat
            parts_needed[key] = [zero_stoppages, zero_stoppages * parts.cost]

# scale as per lowest common denominator
# this serves as the first estimate for allocating repairables budget
non_zero_parts = {key: value.copy() for key, value in parts_needed.items() if value[0] != 0}
lowest_part = min(non_zero_parts, key=lambda x: non_zero_parts[x][0])
lowest_value = non_zero_parts[lowest_part][0]

for key, value in non_zero_parts.items():
    # Append the result of value[1] / lowest_value rounded up
    rounded_value = math.ceil(value[0] / lowest_value)  # Example of using length of the string
    value.append(rounded_value)




# lets do 1 run and see what the serviceability and parts look like

budget = 1000
logger.warning(f"Running Budget {budget}")
temp_spares_allocated, budget = do_first_allocation(budget, part_quantities, non_zero_parts, fleet_size)
spares_allocated = copy.deepcopy(temp_spares_allocated)
highest_servicability = 0

service_current, car_serviceable, car_breakage, serv_tracker, depot_tracker, warehouse_tracker, graveyard_tracker = do_one_run(
    spares_allocated, days, fleet_size, hours_per_day, car_blueprint)
logger.warning(f"Current Serv {service_current}")

plot_serv(car_serviceable,car_breakage)

for x2 in range(10):

    if service_current > highest_servicability:
        highest_servicability = service_current
        spares_allocated = copy.deepcopy(temp_spares_allocated)
        temp_spares_allocated, budget = get_new_service(days, fleet_size, part_quantities, spares_allocated,
                                                        serv_tracker, warehouse_tracker, budget)
        Car.reset_all_cars()
        Part_physical.reset_master_list()
        service_current, car_serviceable, car_breakage, serv_tracker, depot_tracker, warehouse_tracker, graveyard_tracker = do_one_run(
            spares_allocated, days, fleet_size, hours_per_day, car_blueprint)
    else:
        logger.info("no more improvements")
        break

logger.warning(f"Current Serv {service_current}")

plot_serv(car_serviceable,car_breakage)
# initial guesses are ready for implementation
budget_list = []
service_list = []
allocation_list = []
# for budget in range(5000,7000,100):
for budget in range(1000, 1200, 100):
    logger.warning(f"Running Budget {budget}")
    # budget = 7000
    budget_list.append(budget)

    temp_spares_allocated, budget = do_first_allocation(budget, part_quantities, non_zero_parts, fleet_size)
    spares_allocated = copy.deepcopy(temp_spares_allocated)

    highest_servicability = 0

    service_current, car_serviceable, car_breakage, serv_tracker, depot_tracker, warehouse_tracker, graveyard_tracker = do_one_run(
        spares_allocated, days, fleet_size, hours_per_day, car_blueprint)

    logger.info(service_current)

    for x2 in range(10):

        if service_current > highest_servicability:
            highest_servicability = service_current
            spares_allocated = copy.deepcopy(temp_spares_allocated)
            temp_spares_allocated, budget = get_new_service(days, fleet_size, part_quantities, spares_allocated,
                                                            serv_tracker, warehouse_tracker, budget)
            Car.reset_all_cars()
            Part_physical.reset_master_list()
            service_current, car_serviceable, car_breakage, serv_tracker, depot_tracker, warehouse_tracker, graveyard_tracker = do_one_run(
                spares_allocated, days, fleet_size, hours_per_day, car_blueprint)
        else:
            logger.info("no more improvements")
            break
    print(highest_servicability)

    for key, value in spares_allocated.items():
        print(key,value)
    service_list.append(highest_servicability)
    allocation_list.append(spares_allocated)

    Car.reset_all_cars()
    Part_physical.reset_master_list()

plot_budget_serv(budget_list, service_list)
