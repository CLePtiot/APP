import streamlit as st
import random
import time

# --- Classes (Adaptées pour Streamlit) ---

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

# --- Initialisation du jeu ---

def init_game(hardcore=False, name="Héros"):
    st.session_state.player = Player(name, hardcore)
    st.session_state.level = 1
    st.session_state.is_hardcore = hardcore
    st.session_state.game_log = ["Bienvenue dans le donjon !"]
    st.session_state.game_over = False
    spawn_enemy()

def spawn_enemy():
    diff_mult = 1.0 + (st.session_state.level * 0.1)
    if st.session_state.is_hardcore:
        diff_mult *= 1.5
    
    enemy_name = random.choice(["Gobelin", "Squelette", "Orc", "Slime"])
    st.session_state.enemy = Enemy(enemy_name, diff_mult)
    add_log(f"Un {enemy_name} sauvage apparaît ! (PV: {st.session_state.enemy.hp})")

def add_log(message):
    st.session_state.game_log.insert(0, message) # Ajoute au début

# --- Logique de tour ---

def player_attack():
    player = st.session_state.player
    enemy = st.session_state.enemy
    
    # Tour du joueur
    dmg = player.attack(enemy)
    add_log(f"⚔️ Vous attaquez le {enemy.name} pour {dmg} dégâts.")
    
    check_combat_status()

def player_heal():
    player = st.session_state.player
    
    healed = player.heal()
    if healed > 0:
        add_log(f"💖 Vous vous soignez de {healed} PV.")
        enemy_turn() # L'ennemi attaque quand même ? Disons oui pour le challenge
    else:
        add_log("⚠️ Vous n'avez plus de potions !")

def enemy_turn():
    player = st.session_state.player
    enemy = st.session_state.enemy
    
    if enemy.is_alive():
        dmg = enemy.attack(player)
        add_log(f"👹 Le {enemy.name} vous attaque pour {dmg} dégâts !")
        
        if not player.is_alive():
            st.session_state.game_over = True
            add_log("💀 VOUS ÊTES MORT.")
            if st.session_state.is_hardcore:
                add_log("Mode Hardcore : Game Over définitif.")

def check_combat_status():
    enemy = st.session_state.enemy
    
    if not enemy.is_alive():
        add_log(f"🎉 Vous avez vaincu le {enemy.name} !")
        st.session_state.level += 1
        
        # Loot potion
        if random.random() < 0.3:
            st.session_state.player.potions += 1
            add_log("🧪 Vous avez trouvé une potion !")
            
        spawn_enemy()
    else:
        enemy_turn()

# --- Interface Utilisateur (UI) ---

st.set_page_config(page_title="RPG Donjon", page_icon="⚔️")

st.title("🏰 RPG Donjon Textuel")

# Menu Principal / Initialisation
if 'player' not in st.session_state:
    st.header("Nouvelle Partie")
    name = st.text_input("Nom de votre héros", "Aventurier")
    hardcore = st.checkbox("Mode HARDCORE (Moins de PV, ennemis plus forts, mort définitive)", value=False)
    
    if st.button("Commencer l'aventure"):
        init_game(hardcore, name)
        st.rerun()

else:
    # État du jeu
    player = st.session_state.player
    enemy = st.session_state.enemy
    
    # Sidebar stats
    with st.sidebar:
        st.header(f"👤 {player.name} (Niveau {st.session_state.level})")
        st.progress(player.hp / player.max_hp)
        st.write(f"PV: {player.hp}/{player.max_hp}")
        st.write(f"Potions: {player.potions} 🧪")
        
        st.divider()
        
        if st.session_state.is_hardcore:
            st.error("MODE HARDCORE ACTIF")
        
        if st.button("Recommencer"):
            del st.session_state.player
            st.rerun()

    # Zone de combat
    if not st.session_state.game_over:
        st.subheader(f"Combat contre : {enemy.name}")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Vos PV", value=player.hp, delta=f"{player.hp - player.max_hp}" if player.hp < player.max_hp else None)
        with col2:
            st.metric(label=f"PV {enemy.name}", value=enemy.hp)
            st.progress(min(1.0, max(0.0, enemy.hp / (enemy.max_hp if hasattr(enemy, 'max_hp') else 40)))) # Estimation max hp pour la barre

        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if st.button("⚔️ ATTAQUER", use_container_width=True):
                player_attack()
                st.rerun()
        with col_act2:
            if st.button("💖 SOIGNER (Potion)", use_container_width=True, disabled=player.potions <= 0):
                player_heal()
                st.rerun()
    else:
        st.error("GAME OVER")
        st.write(f"Vous avez atteint le niveau {st.session_state.level}.")
        if st.button("Nouvelle Partie"):
            del st.session_state.player
            st.rerun()

    # Log du jeu
    st.divider()
    st.subheader("Journal de combat")
    for msg in st.session_state.game_log:
        st.text(msg)
