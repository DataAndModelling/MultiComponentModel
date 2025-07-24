
from classes import  Part_physical, Part_attributes, Blueprint, Car

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
car_scheduled = []
days = 100

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
        #print("something broke",day_breakage)

    # from warehouse to car
        car_object.fill_parts()
        car_object.check_serviceability()

    # you cannot move parts out of transition

    # shift from car to depot
    temp_dict = Part_physical.group_parts_by_blueprint()
    for part_number in Part_attributes.master_list:


        breakage_tracker[part_number.name].append(temp_dict[part_number.name]["Failed"])
        overhaul_tracker[part_number.name].append(temp_dict[part_number.name]["Overhaul"])
        life_ex_tracker[part_number.name].append(temp_dict[part_number.name]["Life_Ex"])
        #wheels_list.append(Part.group_parts_by_blueprint()["Wheel"]["serviceable_count"])
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



# Plotting the list
plt.plot(car_breakage)

# Adding labels and title
plt.xlabel('Index')
plt.ylabel('Value')
plt.title('Plot of a List')

# Show the plot
plt.show(block=True)

#list_of_dicts = [breakage_tracker,overhaul_tracker,life_ex_tracker]
list_of_dicts = [serv_tracker,depot_tracker,warehouse_tracker,graveyard_tracker]
plot_partnumber_values(list_of_dicts, 'Wheel')
plot_partnumber_values(list_of_dicts, 'Engine')
plot_partnumber_all(depot_done)
plot_partnumber_all(life_ex_tracker)


perf_tracker = {}
for part_number in Part_attributes.master_list:
    if part_number.depot_tat != 0 and part_number.depot_tat != None:
        perf_tracker[part_number.name] = []

for key,value in perf_tracker.items():
    min_value = part_quantities[key]*fleet_size
    temp_min = float('inf')

    for x1 in range(days):

        if (serv_tracker[key][x1] + warehouse_tracker[key][x1]) - min_value< temp_min:
            temp_min = (serv_tracker[key][x1] + warehouse_tracker[key][x1]) - min_value

    perf_tracker[key] = temp_min / part_quantities[key]

max_key, max_value = max(perf_tracker.items(), key=lambda item: item[1])
min_key, min_value = min(perf_tracker.items(), key=lambda item: item[1])
# do analysis
# get current service status
service_current = (1 - sum(car_breakage) / fleet_size / days) * 100
print(service_current)
# get highest cases of unserviceability
# get highest value of serviceability
# change spares allocated

for key, value in spares_allocated.items():
    if key.name == max_key:
        print("match, decremening")
        spares_allocated[key] -= 1
        budget += key.cost
        break

for key, value in spares_allocated.items():
    if key.name == min_key:
        print("match, decremening")
        spares_to_incr = max(0,budget // key.cost)
        spares_allocated[key]  += spares_to_incr
        budget -= key.cost * spares_to_incr
        break



Car.reset_all_cars()
Part_physical.reset_master_list()
