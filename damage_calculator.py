from equipment import Weapon
from equipment import Armor
from equipment import Shield
from unit import Unit

#approximate damage bonusses for spells: projectile, aoe: 0, summons: 15, apocrypha: 40

def test():
    """
    >>> spear = Weapon(name="Guisarme", scaling="str", stats=[106] + [0] * 9)
    >>> spear.bonusses["dmg_type"] = "slash"
    >>> spear.bonusses["dmg_bonus"] = 11
    >>> spear.bonusses["elem_type"] = "divine"
    >>> spear.bonusses["elem_bonus"] = 15
    >>> spear.bonusses["racial_type"] = "faerie"
    >>> spear.bonusses["racial_bonus"] = 7
    >>> spear.stats["avd"] = 15
    >>> spear.stats["agi"] = 20

    >>> bolon = Weapon(name="Bolon", scaling="dex", stats=[82] + [0] * 9)
    >>> bolon.bonusses["dmg_type"] = "crush"
    >>> bolon.bonusses["dmg_bonus"] = 4
    >>> bolon.stats["mind"] = 15

    >>> vest = Armor(name="Plated Vest", stats=[0, 33] + [0] * 8, dmg_resists=[21, 15, 21])
    >>> vest.stats["avd"] = 20

    >>> leggings = Armor(name="Scale Leggings", stats=[0, 19] + [0] * 8, dmg_resists=[11, 8, 11])
    >>> leggings.stats["avd"] = 24

    >>> jewelry = Armor(name="test_jewel", is_jewelry=True)
    >>> jewelry.elem_resists["divine"] = 10
    >>> jewelry.racial_resists["human"] = 5

    >>> shield = Shield(name="shield")
    >>> shield.bonusses["dmg_type"] = "crush"
    >>> shield.bonusses["dmg_bonus"] = 5
    >>> shield.stats["def"] = 10

    >>> unit1 = Unit(name="Denam", race="human", stats=[17, 11, 97, 71, 90, 91, 89, 75, 77, 81], equipment=[spear, None, vest, leggings, jewelry], skills=[False, "spear", 6, "divine", 4, "faerie", 3])
    >>> unit2 = Unit(name="Izabella", race="faerie", stats=[11, 5, 75, 60, 100, 94, 101, 97, 96, 96], equipment=[bolon, None, vest, leggings, jewelry], skills=[False, "instrument", 6, "divine", 5, "human", 2])

    >>> unit1.calc_offense(unit2)
    205.3
    >>> unit2.calc_toughness(unit1)
    133.5
    >>> unit1.calc_damage_bonus(unit2)
    0.43
    >>> unit2.calc_resistance(unit1)
    0.38
    >>> unit1.calc_extra_damage()
    144.2
    >>> unit2.calc_defense()
    57
    >>> unit1.attack(unit2)
    162

    >>> unit1.attack_accuracy(unit2, 0)
    44

    >>> unit2.calc_power(unit1, "divine")
    222.4
    >>> unit1.calc_resilience("divine")
    154.6
    >>> unit2.calc_m_damage_bonus(unit1, "divine")
    0.15
    >>> unit1.calc_resistance(unit2, False, "none", "divine")
    0.1
    >>> unit1.calc_defense(True)
    63
    >>> unit2.cast(unit1, 50, "divine")
    58

    >>> unit2.spell_accuracy(unit1)
    0
    """
    pass

test()

if __name__ == "__main__":
    import doctest
    doctest.testmod()

