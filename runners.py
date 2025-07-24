import math

from logger import get_logger
from classes import Part_physical, Part_attributes, Car
logger = get_logger()


def do_first_allocation(budget,part_quantities,non_zero_parts,fleet_size):
    # now allocate the spares
    # first build the cars
    spares_allocated = {}
    for key, value in part_quantities.items():
        for parts in Part_attributes.master_list:
            if key == parts.name:
                spares_allocated[parts] = 0

    # for the fleet, it comes fully equipped
    for x1 in range(fleet_size):
        for key, value in spares_allocated.items():
            spares_allocated[key] += part_quantities[key.name]


    # second assign spare cash
    while budget > 0:
        break_outer = False
        for key, value in spares_allocated.items():
            if key.name in non_zero_parts:
                spares_allocated[key] += non_zero_parts[key.name][-1]
                budget -= key.cost * non_zero_parts[key.name][-1]
                print(key.name,budget)
                if budget < 0:
                    spares_allocated[key] -= non_zero_parts[key.name][-1]
                    budget += key.cost * non_zero_parts[key.name][-1]
                    print("reversing")
                    print(key.name, budget)
                    break_outer = True
                    break
        if break_outer == True:
            break
    return spares_allocated, budget


def do_one_run(spares_allocated,days,fleet_size,hours_per_day,car_blueprint):
    for key, value in spares_allocated.items():
        for x1 in range(value):
            Part_physical(key)

    Part_physical.assign_parts_to_location(None, "Warehouse")

    for x1 in range(fleet_size):
        car = Car(car_blueprint)
        car.fill_parts()

    serv_tracker = {}
    depot_tracker = {}
    warehouse_tracker = {}
    graveyard_tracker = {}
    breakage_tracker = {}
    overhaul_tracker = {}
    life_ex_tracker = {}
    depot_done = {}
    depot_at = {}
    perf_tracker = {}
    for part_number in Part_attributes.master_list:
        serv_tracker[part_number.name] = []
        depot_tracker[part_number.name] = []
        warehouse_tracker[part_number.name] = []
        graveyard_tracker[part_number.name] = []
        breakage_tracker[part_number.name] = []
        overhaul_tracker[part_number.name] = []
        life_ex_tracker[part_number.name] = []
        depot_done[part_number.name] = []
        depot_at[part_number.name] = []
        perf_tracker[part_number.name] = []

    wheels_list = []
    car_breakage = []
    car_serviceable = []


    for x1 in range(days):
        day_breakage = 0

        # fix the parts
        for part_number in Part_physical.master_list:
            if part_number.location == 'Depot':
                part_number.update_depot_days(1)

        # run the machines
        for x2 in range(hours_per_day):
            for car_object in Car.created_cars:
                car_object.do_run(1)
                car_object.check_serviceability()
                car_object.remove_unserviceable_parts()

        for car_object in Car.created_cars:
            if car_object.serviceable == False:
                day_breakage += 1
            # print("something broke",day_breakage)

            # from warehouse to car
            car_object.fill_parts()
            car_object.check_serviceability()

        car_serviceable.append(Car.count_serviceable_cars())
        # you cannot move parts out of transition

        # shift from car to depot
        temp_dict = Part_physical.group_parts_by_blueprint()
        for part_number in Part_attributes.master_list:
            breakage_tracker[part_number.name].append(temp_dict[part_number.name]["Failed"])
            overhaul_tracker[part_number.name].append(temp_dict[part_number.name]["Overhaul"])
            life_ex_tracker[part_number.name].append(temp_dict[part_number.name]["Life_Ex"])
            # wheels_list.append(Part.group_parts_by_blueprint()["Wheel"]["serviceable_count"])
        car_breakage.append(day_breakage)

        # from depot to warehouse
        temp_dict2 = Part_physical.parts_grouped_depot_warehouse()
        for part_number in Part_attributes.master_list:
            depot_at[part_number.name].append(temp_dict2[part_number.name]["Under_Repair"])
            depot_done[part_number.name].append(temp_dict2[part_number.name]["Finished_Repair"])

        temp_dict3 = Part_physical.parts_grouped_summary()
        for part_number in Part_attributes.master_list:
            serv_tracker[part_number.name].append(temp_dict3[part_number.name]["In_Use"])
            depot_tracker[part_number.name].append(temp_dict3[part_number.name]["Depot"])
            warehouse_tracker[part_number.name].append(temp_dict3[part_number.name]["Warehouse"])
            graveyard_tracker[part_number.name].append(temp_dict3[part_number.name]["Graveyard"])



    service_current = (sum(car_serviceable) / fleet_size / days) * 100

    return service_current, car_serviceable,car_breakage, serv_tracker, depot_tracker, warehouse_tracker,graveyard_tracker


def get_new_service(days,fleet_size,part_quantities,spares_allocated,serv_tracker,warehouse_tracker,budget):

    perf_tracker = {}
    for part_number in Part_attributes.master_list:
        if part_number.depot_tat != 0 and part_number.depot_tat != None:
            perf_tracker[part_number.name] = []

    for key, value in perf_tracker.items():
        min_value = part_quantities[key] * fleet_size
        temp_min = float('inf')

        for x1 in range(days):

            if (serv_tracker[key][x1] + warehouse_tracker[key][x1]) - min_value < temp_min:
                temp_min = (serv_tracker[key][x1] + warehouse_tracker[key][x1]) - min_value

        perf_tracker[key] = temp_min / part_quantities[key]

    max_key, max_value = max(perf_tracker.items(), key=lambda item: item[1])
    min_key, min_value = min(perf_tracker.items(), key=lambda item: item[1])

    for key, value in spares_allocated.items():
        if key.name == max_key:
            decr_cost = key.cost
        elif key.name == min_key:
            incr_cost = key.cost

    cost_to_change = max(decr_cost,incr_cost)
    logger.info(f"cost to change {cost_to_change}")
    can_change = True
    for key, value in spares_allocated.items():
        if key.name == max_key:
            spares_to_de = math.ceil(cost_to_change / key.cost)
            if spares_to_de >= spares_allocated[key]:
                # cant do this!
                can_change = False
            else:
                spares_allocated[key] -= spares_to_de
                budget += key.cost * spares_to_de
                logger.info(f"de {key.name}, {spares_to_de}, {budget}")
                break

    if can_change == True:
        for key, value in spares_allocated.items():
            if key.name == min_key:
                spares_to_incr = max(0, cost_to_change // key.cost)
                spares_allocated[key] += spares_to_incr
                budget -= key.cost * spares_to_incr
                logger.info(f"de {key.name}, {spares_to_de}, {budget}")
                break
    else:
        logger.info("cant do any changes!")

    # Filter out parts with cost of 0 and sort the remaining ones by cost (cheapest first)
    valid_spares = [(key, value) for key, value in spares_allocated.items() if key.cost > 0]
    sorted_spares = sorted(valid_spares, key=lambda x: x[0].cost)  # Sort by cost (cheapest first)

    # Find the minimum cost of valid parts
    min_valid_cost = min(key.cost for key, _ in sorted_spares) if sorted_spares else float('inf')

    if budget > min_valid_cost:
        logger.info(f"Remaining budget: {budget}, redistributing spare budget to parts.")

        for key, value in sorted_spares:
            if budget >= key.cost:  # Check if the budget is sufficient for the part
                max_spares_to_add = budget // key.cost  # Max we can add based on the remaining budget
                spares_allocated[key] += max_spares_to_add
                budget -= key.cost * max_spares_to_add
                logger.info(f"Allocated {max_spares_to_add} of {key.name}. Remaining budget: {budget}")

            if budget <= min_valid_cost:  # If we run out of budget, break the loop
                logger.info("Out of budget. Stopping allocation.")
                break


    return spares_allocated, budget
