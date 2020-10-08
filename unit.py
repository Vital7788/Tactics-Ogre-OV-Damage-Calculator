from itertools import zip_longest
import math
import equipment

class Unit(equipment.Base):

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
        assert len(equip) == 5 and all([e is None or isinstance(e, equipment.Weapon) for e in equip[:2]]) and \
                all([e is None or isinstance(e, equipment.Armor) for e in equip[2:]]) and \
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
        return self.equipment[0].bonusses["elem_type"] if isinstance(self.equipment[0], equipment.Weapon) else "none"

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
                + (weapon.bonusses["racial_type"] == other.race) * weapon.bonusses["racial_bonus"]

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
        return sum([equip.dmg_resists.get(dmg_type, 0) + equip.elem_resists.get(elem, 0) + equip.racial_resists.get(other.race, 0) for equip in self.equipment if isinstance(equip, equipment.Armor)]) / 100

    def calc_extra_damage(self):
        return 1.2 * self.equipment[0].stats["atk"] + self.stats["atk"] \
                + (self.equipment[4].stats["atk"] if self.equipment[4] is not None else 0)

    def calc_defense(self, spell=False):
        return sum([equip.stats["def"] for equip in self.equipment[2:] if equip is not None]) \
                + ((0.9 + (0.1*spell)) * self.equipment[1].stats["def"] if isinstance(self.equipment[1], equipment.Shield) else 0) \
                + self.stats["def"]

    def attack(self, other):
        assert isinstance(self.equipment[0], equipment.Weapon), "no weapon equipped"
        return max(1, math.floor(max(self.calc_offense(other) - other.calc_toughness(self), 0) \
                * min(max(1 + self.calc_damage_bonus(other) - other.calc_resistance(self), 0), 2.5) 
                + self.calc_extra_damage() - other.calc_defense()))

    #direction = 0 for front, 1 for side and 2 for back
    def attack_accuracy(self, other, direction):
        return math.floor(min(100, max(25, 30 + 10 * self.skills["w_rank"]
                + self.stats["dex"] + 1.2 * self.stats["agi"]
                + 0.8 * self.gear_stat_total("dex") + self.gear_stat_total("agi")
                - other.stats["dex"] - 1.2 * other.stats["avd"]
                - 0.6 * other.gear_stat_total("dex") - other.gear_stat_total("avd")
                - 10 * (other.skills["w_type"] == self.skills["w_type"]) * other.skills["w_rank"]) \
                + direction * 15))

    def cast(self, other, spell_power, element, dmg_type="none"):
        return max(1, math.floor(max(self.calc_power(other, element) - other.calc_resilience(element), 0) \
                * min(max(1 + self.calc_m_damage_bonus(other, element) - other.calc_resistance(self, False, dmg_type, element), 0), 2.5) 
                + spell_power - other.calc_defense(True)))

    def spell_accuracy(self, other):
        return math.floor(min(100, max(0, 1.2 * self.stats["mind"] + 1.2 * self.stats["int"]
                + self.gear_stat_total("mind") + 0.8 * self.gear_stat_total("int")
                - 0.8 * other.stats["agi"] - 1.2 * other.stats["avd"]
                - 0.5 * other.gear_stat_total("agi") - other.gear_stat_total("avd"))))

