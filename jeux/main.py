import random
import time

class Entity:
    def __init__(self, name, hp, damage):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.damage = damage

    def is_alive(self):
        return self.hp > 0

    def attack(self, target):
        dmg = random.randint(self.damage[0], self.damage[1])
        target.take_damage(dmg)
        return dmg

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp < 0:
            self.hp = 0

class Player(Entity):
    def __init__(self, name, hardcore=False):
        # Hardcore: Moins de PV, pas de regen automatique (exemple)
        hp = 50 if hardcore else 100
        damage = (5, 10)
        super().__init__(name, hp, damage)
        self.hardcore = hardcore
        self.potions = 1 if hardcore else 3

    def heal(self):
        if self.potions > 0:
            heal_amount = 20
            self.hp = min(self.hp + heal_amount, self.max_hp)
            self.potions -= 1
            return heal_amount
        return 0

class Enemy(Entity):
    def __init__(self, name, difficulty_multiplier=1.0):
        base_hp = random.randint(20, 40)
        base_min_dmg = 2
        base_max_dmg = 6
        
        hp = int(base_hp * difficulty_multiplier)
        min_dmg = int(base_min_dmg * difficulty_multiplier)
        max_dmg = int(base_max_dmg * difficulty_multiplier)
        
        super().__init__(name, hp, (min_dmg, max_dmg))

class Game:
    def __init__(self):
        self.player = None
        self.level = 1
        self.is_hardcore = False

    def start(self):
        print("=== BIENVENUE DANS LE DONJON ===")
        print("Je n'ai trouvé aucun fichier existant, j'ai donc créé ce petit RPG pour vous.")
        
        choice = input("Voulez-vous activer le mode HARDCORE ? (oui/non): ").lower()
        if choice in ['oui', 'o', 'yes', 'y']:
            self.is_hardcore = True
            print("\n!!! MODE HARDCORE ACTIVÉ !!!")
            print("- PV réduits")
            print("- Ennemis plus puissants")
            print("- Moins de potions")
        else:
            print("\nMode Normal activé.")

        name = input("\nEntrez le nom de votre héros: ")
        self.player = Player(name, self.is_hardcore)
        
        self.game_loop()

    def game_loop(self):
        while self.player.is_alive():
            print(f"\n--- Niveau {self.level} ---")
            
            # Difficulty scales with level
            # In hardcore, difficulty scales faster
            diff_mult = 1.0 + (self.level * 0.1)
            if self.is_hardcore:
                diff_mult *= 1.5

            enemy_name = random.choice(["Gobelin", "Squelette", "Orc", "Slime"])
            enemy = Enemy(enemy_name, diff_mult)
            
            print(f"Un {enemy.name} sauvage apparaît ! (PV: {enemy.hp})")
            
            while enemy.is_alive() and self.player.is_alive():
                print(f"\n{self.player.name}: {self.player.hp}/{self.player.max_hp} PV | Potions: {self.player.potions}")
                print(f"{enemy.name}: {enemy.hp} PV")
                
                action = input("Action (a: attaquer, h: soigner): ").lower()
                
                if action == 'a':
                    dmg = self.player.attack(enemy)
                    print(f"Vous infligez {dmg} dégâts au {enemy.name}.")
                elif action == 'h':
                    healed = self.player.heal()
                    if healed > 0:
                        print(f"Vous vous soignez de {healed} PV.")
                    else:
                        print("Plus de potions !")
                        continue # Perte de tour ou on laisse l'ennemi attaquer ? Disons on laisse attaquer pour punir.
                else:
                    print("Action invalide, vous hésitez et perdez votre tour !")

                if enemy.is_alive():
                    enemy_dmg = enemy.attack(self.player)
                    print(f"Le {enemy.name} vous inflige {enemy_dmg} dégâts !")

            if self.player.is_alive():
                print(f"\nVous avez vaincu le {enemy.name} !")
                self.level += 1
                # Chance to find potion
                if random.random() < 0.3:
                    print("Vous avez trouvé une potion !")
                    self.player.potions += 1
                
                input("Appuyez sur Entrée pour continuer...")
            else:
                print("\n=== GAME OVER ===")
                print(f"Vous êtes mort au niveau {self.level}.")
                if self.is_hardcore:
                    print("En mode Hardcore, la mort est définitive. Adieu.")

if __name__ == "__main__":
    game = Game()
    game.start()
