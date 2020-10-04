from itertools import zip_longest

#approximate damage bonusses for spells: projectile, aoe: 0, summons: 15, apocrypha: 40

class Base:

    base_stats = ["atk", "def", "str", "vit", "dex", "agil", "avd", "int", "mind", "res"]
    elements = ["air", "earth", "lightning", "water", "fire", "ice", "divine", "dark"]
    dmg_types = ["crush", "slash", "pierce"]
    races = ["human", "reptile", "divine", "umbra", "faerie", "phantom", "beast", "dragon", "golem"]

    def __init__(self, name, stats=None, **kwargs):
        self.name = name
        self.stats = stats
        super().__init__(**kwargs)

    @property
    def stats(self):
        return self._stats

    @stats.setter
    def stats(self, s):
        s = [0] * len(self.base_stats) if s is None else s
        assert len(s) == len(self.base_stats), "invalid stats"
        self._stats = dict(zip(self.base_stats, s))


class Unit(Base):

    skill_categories = ["dual_wield", "w_type", "w_rank", "aug_elem", "aug_rank", "racial_race", "racial_rank"]

    #stats consist of class atk and def as seen on the class list on the party screen and
    #stats of the unit without any gear, which is the same as a units base stats + class stats
    def __init__(self, race="human", equipment=None, skills=None, **kwargs):
        self.race = race
        self.skills = skills
        self.equipment = equipment
        #self.status
        super().__init__(**kwargs)

    @property
    def equipment(self):
        return self._equipment

    @equipment.setter
    def equipment(self, equip):
        equip = [0] * 5 if equip is None else equip
        assert len(equip) == 5 and all([e is None or isinstance(e, Weapon) for e in equip[:2]]) and \
                all([e is None or isinstance(e, Armor) for e in equip[2:]]) and \
                (equip[4] is None or equip[4].is_jewelry), "invalid equipment"
        self._equipment = equip

    @property
    def skills(self):
        return self._skills

    @skills.setter
    def skills(self, s):
        s = [0]*len(self.skill_categories) if s is None else s
        assert len(s) == len(self.skill_categories), "invalid skills"
        self._skills = dict(zip(self.skill_categories, s))
    
    def __str__(self):
        string = ''
        data = zip_longest(self.stats, self.stats.values(), [e.name if e is not None else "None" for e in self.equipment], self.skills, self.skills.values(), fillvalue = '')
        for row in data:
            string += '\n' + "{:>5} {:<5} {:<15} {:>15} {:<10}".format(*row)
        return '{}({}) {}'.format(self.name, self.race, string)

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

    def calc_power(self, other, element):
        return self.stats["int"] + self.gear_stat_total("int") \
                + 0.9 * self.stats["mind"] + 0.6 * self.gear_stat_total("mind") \
                + (element == self.skills["aug_elem"]) * self.skills["aug_rank"] * 4 \
                + (self.skills["racial_race"] == other.race) * self.skills["racial_rank"] * 5


    def calc_toughness(self, other):
        return 0.7 * self.stats["str"] + 1.1 * self.stats["vit"] \
                + 0.5 * self.gear_stat_total("str") + 0.9 * self.gear_stat_total("vit") \
                + (other.skills["w_type"] == self.skills["w_type"]) * self.skills["w_rank"] * 3 \
                + (other.get_weapon_elem() == self.skills["aug_elem"]) * self.skills["aug_rank"] * 3

    def calc_resilience(self, element):
        return 0.8 * self.stats["mind"] + 0.6 * self.gear_stat_total("mind") \
                + self.stats["res"] + self.gear_stat_total("res") \
                + (element == self.skills["aug_elem"]) * self.skills["aug_rank"] * 3

    def calc_damage_bonus(self, other):
        weapon = self.equipment[0]
        bonus = weapon.bonusses["dmg_bonus"] + weapon.bonusses["elem_bonus"] \
                + (weapon.bonusses["race_type"] == other.race) * weapon.bonusses["race_bonus"]

        if self.equipment[4] is not None:
            jewelry = self.equipment[4]
            bonus += jewelry.dmg_resists.get(weapon.bonusses["dmg_type"], 0) + jewelry.elem_resists.get(weapon.bonusses["elem_type"], 0) + jewelry.racial_resists.get(other.race, 0)

        return bonus / 100

    def calc_m_damage_bonus(self, other, element):
        return (0 if self.equipment[4] is None else self.equipment[4].elem_resists[element] + self.equipment[4].racial_resists[other.race]) / 100

    def calc_resistance(self, other, weapon=True, dmg_type="none", elem="none"):
        if weapon:
            dmg_type = other.equipment[0].bonusses["dmg_type"]
            elem = other.equipment[0].bonusses["elem_type"]
        return sum([equip.dmg_resists.get(dmg_type, 0) + equip.elem_resists.get(elem, 0) + equip.racial_resists.get(other.race, 0) for equip in self.equipment if isinstance(equip, Armor)]) / 100

    def calc_extra_damage(self):
        return 1.2 * self.equipment[0].stats["atk"] + self.stats["atk"] \
                + (self.equipment[4].stats["atk"] if self.equipment[4] is not None else 0)

    def calc_defense(self, spell=False):
        return sum([equip.stats["def"] for equip in self.equipment[2:] if equip is not None]) \
                + ((0.9 + (0.1*spell)) * self.equipment[1].stats["def"] if isinstance(self.equipment[1], Shield) else 0) \
                + self.stats["def"]

    def attack(self, other):
        assert isinstance(self.equipment[0], Weapon), "no weapon equipped"
        #print(self.calc_offense(other), other.calc_toughness(self), self.calc_damage_bonus(other), other.calc_resistance(self), self.calc_extra_damage(), other.calc_defense())
        return round(max(self.calc_offense(other) - other.calc_toughness(self), 0) * min(max(1 + self.calc_damage_bonus(other) - other.calc_resistance(self), 0), 2.5) + self.calc_extra_damage() - other.calc_defense())

    def cast(self, other, spell_power, element, dmg_type="none"):
        print(self.calc_power(other, element), other.calc_resilience(element), self.calc_m_damage_bonus(other, element), other.calc_resistance(self, False, dmg_type, element), spell_power, other.calc_defense(True))
        return round(max(self.calc_power(other, element) - other.calc_resilience(element), 0) * min(max(1 + self.calc_m_damage_bonus(other, element) - other.calc_resistance(self, False, dmg_type, element), 0), 2.5) + spell_power - other.calc_defense(True))

class Weapon(Base):

    weapon_bonus = ["dmg_type", "dmg_bonus", "elem_type", "elem_bonus", "race_type", "race_bonus"]

    def __init__(self, scaling="str", bonusses=None, **kwargs):
        assert scaling == "str" or scaling == "dex", "invalid scaling"
        self.scaling = scaling
        self.bonusses = bonusses
        super().__init__(**kwargs)

    @property
    def bonusses(self):
        return self._bonusses

    @bonusses.setter
    def bonusses(self, bonus):
        bonus = ["crush", 0, "none", 0, "none", 0] if bonus is None else bonus
        assert len(bonus) == len(self.weapon_bonus) and bonus[0] in self.dmg_types, "invalid bonusses"
        self._bonusses = dict(zip(self.weapon_bonus, bonus))

    def __str__(self):
        string = ''
        data = zip_longest(self.stats, self.stats.values(), self.bonusses, self.bonusses.values(), fillvalue = '')
        for row in data:
            string += '\n' + "{:>5} {:<3} {:>12}  {:<5}".format(*row)
        return self.name + string

class Armor(Base):

    def __init__(self, dmg_resists=None, elem_resists=None, racial_resists=None, is_jewelry=False, **kwargs):
        self.dmg_resists = dmg_resists
        self.elem_resists = elem_resists
        self.racial_resists = racial_resists
        self.is_jewelry = is_jewelry
        super().__init__(**kwargs)

    @property
    def dmg_resists(self):
        return self._dmg_resists

    @dmg_resists.setter
    def dmg_resists(self, resists):
        resists = [0] * len(self.dmg_types) if resists is None else resists
        assert len(resists) == len(self.dmg_types), "invalid amount of resistances"
        self._dmg_resists = dict(zip(self.dmg_types, resists))

    @property
    def elem_resists(self):
        return self._elem_resists

    @elem_resists.setter
    def elem_resists(self, resists):
        resists = [0] * len(self.elements) if resists is None else resists
        assert len(resists) == len(self.elements), "invalid amount of resistances"
        self._elem_resists = dict(zip(self.elements, resists))

    @property
    def racial_resists(self):
        return self._racial_resists

    @racial_resists.setter
    def racial_resists(self, resists):
        resists = [0] * len(self.races) if resists is None else resists
        assert len(resists) == len(self.races), "invalid amount of resistances"
        self._racial_resists = dict(zip(self.races, resists))

    def __str__(self):
        string = ''
        data = zip_longest(self.stats, self.stats.values(), self.dmg_resists, self.dmg_resists.values(), self.elem_resists, self.elem_resists.values(), self.racial_resists, self.racial_resists.values(), fillvalue = '')
        for row in data:
            string += '\n' + "{:>5} {:<3} {:>10} {:<3} {:>12} {:<3} {:>10} {:<3}".format(*row)
        return self.name + string

class Shield(Weapon, Armor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __str__(self):
        string = ''
        data = zip_longest(self.stats, self.stats.values(), self.bonusses, self.bonusses.values(), self.dmg_resists, self.dmg_resists.values(), self.elem_resists, self.elem_resists.values(), self.racial_resists, self.racial_resists.values(), fillvalue = '')
        for row in data:
            string += '\n' + "{:>5} {:<3} {:>12}  {:<7} {:>8} {:<3} {:>12} {:<3} {:>10} {:<3}".format(*row)
        return self.name + string

spear = Weapon(name="Guisarme", scaling="str", stats=[106] + [0] * 9)
spear.bonusses["dmg_type"] = "slash"
spear.bonusses["dmg_bonus"] = 11
spear.stats["avd"] = 15

bolon = Weapon(name="Bolon", scaling="dex", stats=[82] + [0] * 9)
bolon.bonusses["dmg_type"] = "crush"
bolon.bonusses["dmg_bonus"] = 4
bolon.stats["mind"] = 15

vest = Armor(name="Plated Vest", stats=[0, 33] + [0] * 8, dmg_resists=[21, 15, 21])
vest.stats["avd"] = 20

leggings = Armor(name="Scale Leggings", stats=[0, 19] + [0] * 8, dmg_resists=[11, 8, 11])
leggings.stats["avd"] = 24

jewelry = Armor(name="test_jewel", is_jewelry=True)

shield = Shield(name="shield")
shield.bonusses["dmg_type"] = "crush"
shield.bonusses["dmg_bonus"] = 5
shield.stats["def"] = 10

unit1 = Unit(name="Denam", race="human", stats=[17, 11, 97, 71, 90, 91, 89, 75, 77, 81], equipment=[spear, None, vest, leggings, jewelry], skills=[False, "spear", 6, "none", 0, "none", 0])
unit2 = Unit(name="Izabella", race="faerie", stats=[11, 5, 75, 60, 100, 94, 101, 97, 96, 96], equipment=[bolon, None, vest, leggings, None], skills=[False, "instrument", 6, "none", 0, "none", 0])
print(unit1.cast(unit2, 40, "divine"))
