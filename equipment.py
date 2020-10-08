from itertools import zip_longest

class Base:

    base_stats = ["atk", "def", "str", "vit", "dex", "agi", "avd", "int", "mind", "res"]
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


class Weapon(Base):

    weapon_bonus = ["dmg_type", "dmg_bonus", "elem_type", "elem_bonus", "racial_type", "racial_bonus"]

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
