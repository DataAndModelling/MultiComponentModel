import random
import math
from collections import defaultdict

from logger import get_logger

logger = get_logger()



class Part_attributes:
    """
    this is the part number Class
    """

    master_list = []  # Class-level attribute to track all parts created

    def __init__(self, name, failure_hours=float('inf'), life_limit=float('inf'), depot_limit=float('inf'),
                 depot_repair=float('inf'), depot_overhaul=float('inf'), shape_factor=1, depot_tat=1, cost=1000,
                 placeholder=False):
        self.name = name
        self.failure_hours = failure_hours
        self.shape_factor = shape_factor
        self.life_limit = life_limit
        self.depot_limit = depot_limit
        self.depot_repair = depot_repair
        self.depot_overhaul = depot_overhaul
        self.depot_tat = depot_tat
        self.placeholder = placeholder
        self.cost = cost
        # placeholders are for imaginary containers for subparts, if I ever decide to use it

        # Add the current instance to the master list whenever a new part is created
        Part_attributes.master_list.append(self)

    def __repr__(self):
        return (f"PartBlueprint(Name: {self.name}, Failure Hours: {self.failure_hours}, "
                f"Life Limit: {self.life_limit}, Depot Limit: {self.depot_limit}, "
                f"Depot Repair: {self.depot_repair}, Depot Overhaul: {self.depot_overhaul}, "
                f"Shape Factor: {self.shape_factor}, Depot TAT: {self.depot_tat}, "
                f"Cost: {self.cost}, Placeholder: {self.placeholder})")

    @classmethod
    def remove_part(cls, part):
        """Removes a specific part from the master list."""
        if part in cls.master_list:
            cls.master_list.remove(part)
            logger.info(f"Removed {part.name} from master list.")
        else:
            logger.info(f"{part.name} not found in master list.")

    @classmethod
    def reset_master_list(cls):
        """Removes all instances and resets the master list to an empty list."""
        # Explicitly delete instances
        for part in cls.master_list:
            del part  # Deletes the instance itself, which triggers __del__ if defined
        cls.master_list.clear()  # Clear the master list itself
        logger.info("Master list has been reset and all parts have been removed.")

    def __del__(self):
        """Optional: Define custom deletion behavior when an instance is deleted."""
        logger.info(f"Part {self.name} is being deleted.")



class Part_physical:
    # this class stores the serial number information
    master_list = []
    # Class-level list to store all created parts
    master_dict = {}
    # Class-level counter to generate unique serial numbers
    serial_counter = 1

    def __init__(self, blueprint: Part_attributes, operating_hours= 0, location=None):
        """
        Initialize the Part instance, associating it with a PartBlueprint and setting its location.
        """
        self.blueprint = blueprint
        self.serial_number = Part_physical.serial_counter
        self.location = location
        self.operating_hours = 0
        if self.blueprint.failure_hours != float('inf'):
            self.failure_hours = self.weibull_inverse_cdf(self.blueprint.shape_factor,self.blueprint.failure_hours)
        else:
            self.failure_hours = self.blueprint.failure_hours
        self.life_limit = self.blueprint.life_limit
        self.depot_limit = self.blueprint.depot_limit
        self.serviceable = self.operating_hours < self.failure_hours
        self.depot_tat = 0
        self.cost = self.blueprint.cost


        # Register this part in the global list of created parts
        Part_physical.master_dict[Part_physical.serial_counter] = self
        Part_physical.master_list.append(self)

        # Increment the serial number counter for the next part
        Part_physical.serial_counter += 1

    def __repr__(self):
        return (f"Part(Serial: {self.serial_number}, Name: {self.blueprint.name}, "
                f"Location: {self.location}, Operating Hours: {self.operating_hours}, "
                f"Failure Hours: {self.blueprint.failure_hours}, actual failure time :{self.failure_hours}, Serviceable: {self.serviceable})")

    @staticmethod
    def weibull_inverse_cdf(shape_factor, scale_factor):
        """
        Generate a value from the inverse CDF of the Weibull distribution.

        Parameters:
        shape_factor (beta): The shape parameter (β)
        scale_factor (lambda): The scale parameter (λ)
        u (float): A uniform random variable between 0 and 1.

        Returns:
        float: A value sampled from the Weibull distribution.
        """
        u = random.random()
        fail_time = scale_factor * (-math.log(1 - u))**(1 / shape_factor)
        return fail_time

    @classmethod
    def all_parts(cls):
        """Method to return all parts created and their locations."""
        return "\n".join(f"Serial Number: {part.serial_number}, {part.blueprint.name}, Location: {part.location}, "
                         f"Operating Hours: {part.operating_hours}, Failure Hours: {part.failure_hours}, "
                         f"Serviceable: {part.serviceable}"
                         for part in cls.master_list)

    def reset_operating_hours(self):
        """Method to reset operating hours to zero."""
        self.operating_hours = 0
        # Update serviceable status after reset
        if self.blueprint.failure_hours != float('inf'):
            self.failure_hours = self.weibull_inverse_cdf(self.blueprint.shape_factor,self.blueprint.failure_hours)
            #print("hello we are here")
        else:
            self.failure_hours = self.blueprint.failure_hours
        self.serviceable = self.operating_hours < self.failure_hours
        print(f"Operating hours for part {self.serial_number} ({self.blueprint.name}) have been reset to 0.")

    def has_failed(self):
        """Check if the part has failed based on operating hours."""
        if self.operating_hours >= self.failure_hours:
            return True
        else:
            return False

    def reach_life(self):
        """Check if the part has failed based on operating hours."""
        if self.operating_hours >= self.life_limit:
            return True
        else:
            return False

    def needs_depot(self):
        """Check if the part has failed based on operating hours."""
        if self.operating_hours >= self.depot_limit:
            return True
        else:
            return False

    def update_operating_hours(self, hours):
        """Update the operating hours and check if the part is still serviceable."""
        self.operating_hours += hours
        # Update serviceable status
        if self.reach_life() == True:
            self.serviceable = False
            self.location = 'Transit_Graveyard'
        elif self.needs_depot() == True:
            self.serviceable = False
            self.location = 'Transit_Depot_OH'
            self.depot_tat = self.blueprint.depot_tat
        elif self.has_failed() == True:
            self.serviceable = False
            self.location = 'Transit_Depot_UER'
            self.depot_tat = self.blueprint.depot_tat
        else:
            self.serviceable = True

        #self.blueprint.serviceable = self.serviceable
        logger.info(
            f"Operating hours for part {self.serial_number} ({self.blueprint.name}) updated to {self.operating_hours}. "
            f"Serviceable: {self.serviceable}")

    def update_depot_days(self, hours):
        """Update the operating hours and check if the part is still serviceable."""
        self.depot_tat -= hours
        # Update serviceable status
        if self.depot_tat <= 0:
            self.serviceable = True
            self.location = 'Transit_Warehouse'
            # update failure time
            self.failure_hours += self.weibull_inverse_cdf(self.blueprint.shape_factor,self.blueprint.failure_hours)


    @classmethod
    def remove_part(cls, serial_number):
        """Removes a specific part from the master list based on serial number."""
        if serial_number in cls.master_dict:
            part = cls.master_dict.pop(serial_number)  # Remove the part from the master list and store the reference
            logger.info(f"Removed Serial Number {serial_number} from master list ")
            if part in cls.master_list:
                del part

        else:
            logger.info(f"Part with Serial Number {serial_number} not found in master list.")

    @classmethod
    def reset_master_list(cls):
        """Removes all instances and resets the master list to an empty list."""
        Part_physical.master_dict.clear()  # Clear the master list itself
        for parts in Part_physical.master_list:
            del parts
        cls.master_list.clear()  # Finally clear the list itself
        logger.info("Master list has been reset")

    def __del__(self):
        """Optional: Define custom deletion behavior when an instance is deleted."""
        pass

    @classmethod
    def assign_parts_to_location(cls, current_location, future_location):
        """
        Iterate over all parts in the master list and if their location matches the current_location,
        assign them to the future_location.
        """
        for part in cls.master_list:
            if part.location == current_location:
                part.location = future_location
                logger.info(f"Part {part.serial_number} ({part.blueprint.name}) moved from {current_location} to {future_location}.")
            else:
                logger.info(f"Part {part.serial_number} ({part.blueprint.name}) is not located at {current_location}, no change.")


    @classmethod
    def group_parts_by_blueprint(cls):
        """
        Groups parts by their blueprint, and counts the total and serviceable parts.
        Returns a dictionary where each key is the blueprint name, and the value is
        a dictionary containing:
        - 'serviceable_count': The count of serviceable parts for that blueprint.
        - 'total_count': The total count of parts for that blueprint.
        """
        blueprint_stats = defaultdict(
            lambda: {'serviceable_count': 0, 'total_count': 0, "Life_Ex": 0, "Overhaul": 0, "Failed": 0})

        for part in cls.master_list:
            blueprint_name = part.blueprint.name  # Get the name of the blueprint
            blueprint_stats[blueprint_name]['total_count'] += 1  # Increment total count

            if part.serviceable == True:
                blueprint_stats[blueprint_name]['serviceable_count'] += 1  # Increment serviceable count
            if part.location == "Transit_Graveyard":
                blueprint_stats[blueprint_name]["Life_Ex"] += 1
                # send to the Graveyard
                part.location = "Graveyard"
            elif part.location == 'Transit_Depot_OH':
                blueprint_stats[blueprint_name]['Overhaul'] += 1
                # send to the Depot
                part.location = "Depot"
            if part.location == 'Transit_Depot_UER':
                blueprint_stats[blueprint_name]['Failed'] += 1
                # send to the Depot
                part.location = "Depot"

        return dict(blueprint_stats)

    @classmethod
    def parts_grouped_depot_warehouse(cls):
        """
        Groups parts by their blueprint, and counts the total and serviceable parts.
        Returns a dictionary where each key is the blueprint name, and the value is
        a dictionary containing:
        - 'serviceable_count': The count of serviceable parts for that blueprint.
        - 'total_count': The total count of parts for that blueprint.
        """
        blueprint_stats = defaultdict(
            lambda: {'total_count': 0, "Under_Repair": 0, "Finished_Repair": 0})

        for part in cls.master_list:
            blueprint_name = part.blueprint.name  # Get the name of the blueprint
            blueprint_stats[blueprint_name]['total_count'] += 1  # Increment total count

            if part.location == "Transit_Warehouse":
                blueprint_stats[blueprint_name]["Finished_Repair"] += 1
                # send to the Warehouse
                part.location = "Warehouse"
            elif part.location == 'Depot':
                blueprint_stats[blueprint_name]['Under_Repair'] += 1
                # we're done. no need to do anything else

        return dict(blueprint_stats)
    @classmethod
    def parts_grouped_summary(cls):
        """
        Groups parts by their blueprint, and counts the total and serviceable parts.
        Returns a dictionary where each key is the blueprint name, and the value is
        a dictionary containing:
        - 'serviceable_count': The count of serviceable parts for that blueprint.
        - 'total_count': The total count of parts for that blueprint.
        """
        blueprint_stats = defaultdict(
            lambda: {'total_count': 0, "In_Use": 0, "Depot": 0,"Warehouse":0, "Graveyard":0})

        for part in cls.master_list:
            blueprint_name = part.blueprint.name  # Get the name of the blueprint
            blueprint_stats[blueprint_name]['total_count'] += 1  # Increment total count

            if part.location == "Car":
                blueprint_stats[blueprint_name]["In_Use"] += 1
            elif part.location == 'Depot':
                blueprint_stats[blueprint_name]['Depot'] += 1
            elif part.location == 'Warehouse':
                blueprint_stats[blueprint_name]['Warehouse'] += 1
            elif part.location == 'Graveyard':
                blueprint_stats[blueprint_name]['Graveyard'] += 1
                # we're done. no need to do anything else

        return dict(blueprint_stats)
class Blueprint:
    def __init__(self, place, part_type):
        """
        Initialize the Blueprint with a place (where the part is located)
        and a part_type (the type of part that can fill this node).
        """
        self.place = place
        self.part_type = part_type
        self.children = []

    def add_child(self, place, part_type):
        # Add a child node with a specific place and part_type
        new_node = Blueprint(place, part_type)
        self.children.append(new_node)
        return new_node

    def __repr__(self, level=0):
        # Recursive function to represent the blueprint structure
        result = "\t" * level + f"Place: {self.place}, Part Type: {self.part_type}\n"
        for child in self.children:
            result += child.__repr__(level + 1)
        return result

    def get_part_quantities(self):
        """
        Iterate over all children, store the parts and their quantities in a dictionary.
        """
        part_quantities = {}

        # Helper function to traverse recursively and count parts
        def traverse(node):
            # Count the current node's part
            if node.part_type in part_quantities:
                part_quantities[node.part_type] += 1
            else:
                part_quantities[node.part_type] = 1

            # Recursively traverse children
            for child in node.children:
                traverse(child)

        # Start the traversal from the current node
        traverse(self)

        return part_quantities


class Car:
    # Class-level list to store all created parts
    created_cars = []
    # Class-level counter to generate unique serial numbers
    serial_counter = 1

    def __init__(self, blueprint):
        self.blueprint = blueprint
        self.parts = {}
        self.serviceable = False

        # Register this car in the global list of created cars
        Car.created_cars.append(self)

        # Increment the serial number counter for the next car
        Car.serial_counter += 1

    def fill_parts(self):
        """
        Fills the car with parts based on its blueprint.
        This method should be called after the car has been created.
        """
        self._fill_parts(self.blueprint)
    def _fill_parts(self, node):
        """
        Recursively fill in the parts based on the Blueprint.
        For each node in the blueprint, get the corresponding part from the master list.
        """
        # Check if the car node already has a part assigned
        if node.place in self.parts:
            #print(f"Car already has a part at {node.place}. Skipping.")
            pass
        else:

            for part in Part_physical.master_list:
                # Check if part matches the blueprint and its location is None
                if part.blueprint.name == node.part_type and part.location == "Warehouse" and part.serviceable == True:
                    # Assign the part to the current location
                    self.parts[node.place] = {
                        'part_type': node.part_type,
                        'part': part
                    }
                    # Set the part's location to "Car"
                    part.location = "Car"
                    logger.info(f"Assigned part {part.blueprint.name} to place {node.place}.")
                    break  # Exit after assigning the part for this location

        # Recursively fill in children (sub-parts)
        for child in node.children:
            self._fill_parts(child)

    def check_serviceability(self):
        """
        Recursively check if all parts required by the car's blueprint are filled.
        If all parts are assigned to their respective places, the car is serviceable.
        """
        # Start by checking the serviceability of the root node (the main car blueprint)
        is_serviceable = self._check_serviceability_recursive(self.blueprint)

        # Update the car's serviceable status based on the result
        self.serviceable = is_serviceable
        return self.serviceable

    def _check_serviceability_recursive(self, node):
        """
        Helper function to recursively check serviceability by going through each node's place.
        """
        # Check if a part has been assigned to the current node's place
        if node.place not in self.parts:
            logger.info(f"Missing part at {node.place}. Car is not serviceable.")
            return False  # If the part is not assigned, the car is not serviceable

        # Check if the part assigned at the current node is serviceable
        part = self.parts[node.place]['part']
        if not part.serviceable:  # If the part itself is unserviceable
            logger.info(f"Part {part.blueprint.name} at {node.place} is unserviceable.")
            return False  # If the part is unserviceable, the car is not serviceable

        # Recursively check each child node
        for child in node.children:
            if not self._check_serviceability_recursive(child):
                return False  # If any child is not serviceable, return False

        # If all checks pass, the node is serviceable
        return True

    def remove_unserviceable_parts(self):
        """
        Remove all unserviceable parts from the car and set their location to None.
        """
        for place, part_info in list(self.parts.items()):
            part = part_info['part']
            if not part.serviceable:  # Check if the part is not serviceable
                # Remove the part from the car's parts
                del self.parts[place]
                # Reset the part's location to None
                #part.location = "Just_Broken"
                #print(f"Removed unserviceable part {part.blueprint.name} from place {place}. Location reset to None.")

    def do_run(self, amount):
        """
        If the car is serviceable, increment the operating hours of each part by the given amount.
        """
        if not self.serviceable:
            #print("The car is not serviceable. Cannot run.")
            pass
            return

        for place, part_info in self.parts.items():
            part = part_info['part']
            part.update_operating_hours(amount)
            # i transfered this to part.
            #part.operating_hours += amount
            #print(f"Part {part_info['part'].blueprint.name} at {place} now has {part.operating_hours} operating hours.")
            #if part.has_failed() == True:
            #    part.serviceable = False


    def __repr__(self):
        """
        Return a string representation of the car's parts.
        """
        result = []
        for place, part_info in self.parts.items():
            result.append(
                f"Place: {place}, Part Type: {part_info['part_type']}, Part: {part_info['part'].blueprint.name}, "
                f"Serial: {part_info['part'].serial_number}, Operating Hours: {part_info['part'].operating_hours}, "
                f"Failure Hours: {part_info['part'].blueprint.failure_hours}, Serviceable: {part_info['part'].serviceable}, "
                f"Location: {part_info['part'].location}")
        return "\n".join(result)

    @classmethod
    def count_serviceable_cars(cls):
        # Count how many cars in created_cars are serviceable
        serviceable_cars = sum(1 for car in cls.created_cars if car.check_serviceability())
        return serviceable_cars

    @classmethod
    def reset_all_cars(cls):
        """
        Deletes all car instances and resets the created_cars list.
        """
        # Reset all car instances by clearing the list
        cls.created_cars.clear()

        # Optionally, reset the serial number counter
        cls.serial_counter = 1

        logger.info("All car instances have been deleted and the master list has been reset.")
