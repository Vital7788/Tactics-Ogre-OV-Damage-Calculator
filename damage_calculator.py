from itertools import zip_longest

#approximate damage bonusses for spells: projectile, aoe: 0, summons: 15, apocrypha: 40
base_stats = ["atk", "def", "str", "vit", "dex", "agil", "avd", "int", "mind", "res"]
elements = ["air", "earth", "lightning", "water", "fire", "ice", "divine", "dark"]
dmg_types = ["crush", "slash", "pierce"]
races = ["human", "reptile", "divine", "umbra", "faerie", "phantom", "beast", "dragon", "golem"]

class Unit:

    skills = ["dual_wield", "w_type", "w_rank", "aug_elem", "aug_rank", "racial_race", "racial_rank"]

    #stats consist of class atk and def as seen on the class list on the party screen and
    #stats of the unit without any gear, which is the same as a units base stats + class stats
    def __init__(self, name, race="human", stats=[0]*10, equipment=[None]*5, skills=[False] + ["none", 0] * 3):

        assert len(stats) == 10 and len(equipment) == 5 and len(skills) == 7, "invalid stats"

        self.name = name
        self.race = race

        self.stats = {base_stats[i]:stats[i] for i in range(10)}
        self.skills = {Unit.skills[i]:skills[i] for i in range(7)}

        self.equipment = equipment
        #self.status
    
    def equip(self, *equipment):
        self.equipment = equipment

    def equip_slot(self, slot, equipment):
        assert slot > 0 and slot <= 5, "wrong slot"
        self.equipment[slot-1] = equipment

    def __str__(self):
        return self.name

    def gear_stat_total(self, stat):
        return sum([equip.stats[stat] for equip in self.equipment if equip is not None])

    def get_weapon_elem(self):
        return self.equipment[0].bonusses["elem_type"] if isinstance(self.equipment[0], Weapon) else "none"

    def calc_offense(self, other):
        scale_str = self.equipment[0].scaling == "str" 
        return (0.7 + 0.2 * scale_str) * (self.stats["str"]) \
                + (0.5 + 0.2 * scale_str) * (self.gear_stat_total("str")) \
                + (1.1 - 0.4 * scale_str) * self.stats["dex"] \
                + (0.9 - 0.4 * scale_str) * (self.gear_stat_total("dex")) \
                + 4 * self.skills["w_rank"] \
                + (self.equipment[0].bonusses["elem_type"] == self.skills["aug_elem"]) * self.skills["aug_rank"] * 4 \
                + (self.skills["racial_race"] == other.race) * self.skills["racial_rank"] * 5

    def calc_toughness(self, other):
        return 0.7 * self.stats["str"] + 1.1 * self.stats["vit"] \
                + 0.5 * self.gear_stat_total("str") + 0.9 * self.gear_stat_total("vit") \
                + (other.skills["w_type"] == self.skills["w_type"]) * self.skills["w_rank"] * 3 \
                + (other.get_weapon_elem() == self.skills["aug_elem"]) * self.skills["aug_rank"] * 3


    def calc_damage_bonus(self, other):
        weapon = self.equipment[0]
        bonus = weapon.bonusses["dmg_bonus"] + weapon.bonusses["elem_bonus"] \
                + (weapon.bonusses["race_type"] == other.race) * weapon.bonusses["race_bonus"]

        if self.equipment[4] is not None:
            jewelry = self.equipment[4]
            bonus += jewelry.dmg_resists.get(weapon.bonusses["dmg_type"], 0) + jewelry.elem_resists.get(weapon.bonusses["elem_type"], 0) + jewelry.racial_resists.get(weapon.bonusses["race_type"], 0)

        return bonus / 100

    def calc_resistance(self, other):
        dmg_type = other.equipment[0].bonusses["dmg_type"]
        elem = other.equipment[0].bonusses["elem_type"]
        return sum([equip.dmg_resists.get(dmg_type, 0) + equip.elem_resists.get(elem, 0) + equip.racial_resists.get(other.race, 0) for equip in self.equipment if isinstance(equip, Armor)]) / 100

    def calc_extra_damage(self):
        return 1.2 * self.equipment[0].stats["atk"] + self.stats["atk"] \
                + (self.equipment[4].stats["atk"] if self.equipment[4] is not None else 0)

    def calc_defense(self):
        return sum([equip.stats["def"] for equip in self.equipment[2:] if equip is not None]) \
                + (0.9 * self.equipment[1].stats["def"] if isinstance(self.equipment[1], Armor) else 0) \
                + self.stats["def"]

    def attack(self, other):
        assert isinstance(self.equipment[0], Weapon), "no weapon equipped"
        #print(self.calc_offense(other), other.calc_toughness(self), self.calc_damage_bonus(other), other.calc_resistance(self), self.calc_extra_damage(), other.calc_defense())
        return round(max(self.calc_offense(other) - other.calc_toughness(self), 0) * min(max(1 + self.calc_damage_bonus(other) - other.calc_resistance(self), 0), 2.5) + self.calc_extra_damage() - other.calc_defense())

class Weapon:

    weapon_bonus = ["dmg_type", "dmg_bonus", "elem_type", "elem_bonus", "race_type", "race_bonus"]

    def __init__(self, name, scaling="str", stats=[0]*10, bonusses=["crush", 0, "none", 0, "none", 0]):

        assert len(stats) == 10 and len(bonusses) == 6, "invalid stats"

        self.name = name

        self.scaling = scaling
        self.stats = {base_stats[i]:stats[i] for i in range(10)}
        self.bonusses = {Weapon.weapon_bonus[i]:bonusses[i] for i in range(6)}

    def set_dmg_bonus(self, dmg_type, percent):
        assert dmg_type in dmg_types, "invalid type"
        self.bonusses["dmg_type"] = dmg_type
        self.bonusses["dmg_bonus"] = percent

    def set_elem_bonus(self, elem_type, percent):
        assert elem_type == "none" or elem_type in elements, "invalid type"
        self.bonusses["elem_type"] = elem_type
        self.bonusses["elem_bonus"] = percent

    def set_race_bonus(self, race_type, percent):
        assert race_type == "none" or race_type in races, "invalid type"
        self.bonusses["race_type"] = race_type
        self.bonusses["race_bonus"] = percent

    def __str__(self):
        string = ''
        data = zip_longest(self.stats, self.stats.values(), self.bonusses, self.bonusses.values(), fillvalue = '')
        for row in data:
            string += '\n' + "{:>5} {:>3} {:>15} {:>10}".format(*row)
        return self.name + string

class Armor:

    def __init__(self, name, stats=[0]*10, dmg_resists=[0]*3, elem_resists=[0]*8, racial_resists=[0]*9, is_jewelry=False):

        assert len(stats) == 10 and len(dmg_resists) == 3 and \
               len(elem_resists) == 8 and len(racial_resists) == 9, "invalid stats"

        self.name = name

        self.stats = {base_stats[i]:stats[i] for i in range(10)}
        self.dmg_resists = {dmg_types[i]:dmg_resists[i] for i in range(3)}
        self.elem_resists = {elements[i]:elem_resists[i] for i in range(8)}
        self.racial_resists = {races[i]:racial_resists[i] for i in range(9)}
        self.is_jewelry = is_jewelry

    def set_dmg_resists(self, resists):
        assert len(resists) == 3, "invalid amount of arguments"
        self.dmg_resists = {dmg_types[i]:resists[i] for i in range(3)}

    def set_elem_resists(self, resists):
        assert len(resists) == 8, "invalid amount of arguments"
        self.elem_resists = {elements[i]:resists[i] for i in range(8)}

    def set_racial_resists(self, resists):
        assert len(resists) == 9, "invalid amount of arguments"
        self.racial_resists = {races[i]:resists[i] for i in range(9)}

    def __str__(self):
        string = ''
        data = zip_longest(self.stats, self.stats.values(), self.dmg_resists, self.dmg_resists.values(), self.elem_resists, self.elem_resists.values(), self.racial_resists, self.racial_resists.values(), fillvalue = '')
        for row in data:
            string += '\n' + "{:>5} {:>3} {:>15} {:>3} {:>15} {:>3} {:>15} {:>3}".format(*row)
        return self.name + string

def set_stat(target, stat, value):
    assert stat in base_stats and isinstance(value, int), "invalid stat"
    target.stats[stat] = value

def set_stats(target, stats):
    assert len(stats) == 10, "invalid stats"
    target.stats = stats


spear = Weapon("Guisarme", "str", [106] + [0] * 9)
spear.set_dmg_bonus("slash", 11)
#spear.set_elem_bonus("divine", 0)
#spear.set_race_bonus("faerie", 20)
set_stat(spear, "avd", 15)

bolon = Weapon("Bolon", "dex", [82] + [0] * 9)
bolon.set_dmg_bonus("crush", 4)
set_stat(bolon, "mind", 15)

vest = Armor("Plated Vest", [0, 33] + [0] * 8, [21, 15, 21], [0] * 8)
set_stat(vest, "avd", 20)

leggings = Armor("Scale Leggings", [0, 19] + [0] * 8, [11, 8, 11], [0] * 8)
set_stat(leggings, "avd", 24)

jewelry = Armor("test_jewel", is_jewelry=True)

shield = Armor("shield")
set_stat(shield, "def", 10)

unit1 = Unit("Denam", "human", [17, 11, 97, 71, 90, 91, 89, 75, 77, 81], [spear, None, vest, leggings, jewelry], [False, "spear", 6, "none", 0, "none", 0])
unit2 = Unit("Izabella", "faerie", [11, 5, 75, 60, 100, 94, 101, 97, 96, 96], [bolon, None, vest, leggings, None], [False, "instrument", 6, "none", 0, "none", 0])
print(unit1.attack(unit2))
