import json
import os
import pygame
from constants import *

class HighscoreManager:
    def __init__(self):
        self.highscores = []
        self.load_highscores()
        
    def load_highscores(self):
        try:
            if os.path.exists(HIGHSCORE_FILE):
                with open(HIGHSCORE_FILE, 'r') as f:
                    self.highscores = json.load(f)
            else:
                # Standard-Highscores erstellen
                self.highscores = [{"name": "AAA", "score": 1000 - i * 100} for i in range(HIGHSCORE_MAX_ENTRIES)]
                self.save_highscores()
        except Exception as e:
            print(f"Fehler beim Laden der Highscores: {e}")
            self.highscores = [{"name": "AAA", "score": 1000 - i * 100} for i in range(HIGHSCORE_MAX_ENTRIES)]
    
    def save_highscores(self):
        try:
            with open(HIGHSCORE_FILE, 'w') as f:
                json.dump(self.highscores, f)
        except Exception as e:
            print(f"Fehler beim Speichern der Highscores: {e}")
    
    def is_highscore(self, score):
        """Prüft, ob der Score ein neuer Highscore ist"""
        if len(self.highscores) < HIGHSCORE_MAX_ENTRIES:
            return True
        return score > self.highscores[-1]["score"]
    
    def add_highscore(self, name, score):
        """Fügt einen neuen Highscore hinzu und sortiert die Liste"""
        # Name validieren
        name = name.upper()[:HIGHSCORE_NAME_LENGTH]
        # Nur erlaubte Zeichen
        name = ''.join(c for c in name if c in HIGHSCORE_ALLOWED_CHARS)
        # Mit Leerzeichen auffüllen, falls zu kurz
        name = name.ljust(HIGHSCORE_NAME_LENGTH, 'A')
        
        self.highscores.append({"name": name, "score": score})
        # Nach Punkten sortieren (absteigend)
        self.highscores.sort(key=lambda x: x["score"], reverse=True)
        # Auf maximale Anzahl begrenzen
        self.highscores = self.highscores[:HIGHSCORE_MAX_ENTRIES]
        self.save_highscores()
        
        # Position in der Liste zurückgeben
        for i, entry in enumerate(self.highscores):
            if entry["name"] == name and entry["score"] == score:
                return i
        return -1

class HighscoreInput:
    def __init__(self, score):
        self.score = score
        self.name = ["A", "A", "A"]  # Default-Name
        self.current_pos = 0
        self.done = False
        self.font = pygame.font.Font(None, 64)
        
    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.done = True
                    return ''.join(self.name)
                    
                elif event.key == pygame.K_BACKSPACE:
                    # Zurück zum vorherigen Buchstaben
                    self.current_pos = max(0, self.current_pos - 1)
                    
                elif event.key == pygame.K_RIGHT:
                    # Zum nächsten Buchstaben
                    self.current_pos = min(HIGHSCORE_NAME_LENGTH - 1, self.current_pos + 1)
                    
                elif event.key == pygame.K_LEFT:
                    # Zum vorherigen Buchstaben
                    self.current_pos = max(0, self.current_pos - 1)
                    
                elif event.key == pygame.K_UP:
                    # Buchstabe erhöhen
                    current_char = self.name[self.current_pos]
                    idx = HIGHSCORE_ALLOWED_CHARS.find(current_char)
                    idx = (idx + 1) % len(HIGHSCORE_ALLOWED_CHARS)
                    self.name[self.current_pos] = HIGHSCORE_ALLOWED_CHARS[idx]
                    
                elif event.key == pygame.K_DOWN:
                    # Buchstabe verringern
                    current_char = self.name[self.current_pos]
                    idx = HIGHSCORE_ALLOWED_CHARS.find(current_char)
                    idx = (idx - 1) % len(HIGHSCORE_ALLOWED_CHARS)
                    self.name[self.current_pos] = HIGHSCORE_ALLOWED_CHARS[idx]
        
        return None
    
    def draw(self, screen):
        # Hintergrund
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Halbtransparenter Hintergrund
        screen.blit(overlay, (0, 0))
        
        # Titel
        title_text = self.font.render("NEUER HIGHSCORE!", True, "white")
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 
                                SCREEN_HEIGHT // 3 - title_text.get_height()))
                                
        # Score anzeigen
        score_text = self.font.render(f"Score: {self.score}", True, "white")
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 
                                SCREEN_HEIGHT // 3))
        
        # Name eingeben
        for i in range(HIGHSCORE_NAME_LENGTH):
            color = "yellow" if i == self.current_pos else "white"
            char_text = self.font.render(self.name[i], True, color)
            
            # Position für jeden Buchstaben
            x = SCREEN_WIDTH // 2 - (HIGHSCORE_NAME_LENGTH * 40) // 2 + i * 40
            y = SCREEN_HEIGHT // 2
            
            # Rahmen für den aktuellen Buchstaben
            if i == self.current_pos:
                pygame.draw.rect(screen, "yellow", 
                               (x - 5, y - 5, 
                                char_text.get_width() + 10, 
                                char_text.get_height() + 10), 2)
            
            screen.blit(char_text, (x, y))
        
        # Anweisungen
        hint_font = pygame.font.Font(None, 30)
        hint1 = hint_font.render("Pfeiltasten: Buchstaben ändern", True, "white")
        hint2 = hint_font.render("Enter: Bestätigen", True, "white")
        
        screen.blit(hint1, (SCREEN_WIDTH // 2 - hint1.get_width() // 2, 
                          SCREEN_HEIGHT * 2 // 3))
        screen.blit(hint2, (SCREEN_WIDTH // 2 - hint2.get_width() // 2, 
                          SCREEN_HEIGHT * 2 // 3 + 30))

class HighscoreDisplay:
    def __init__(self, highscore_manager):
        self.highscore_manager = highscore_manager
        self.font_title = pygame.font.Font(None, 64)
        self.font_entry = pygame.font.Font(None, 36)
        
    def draw(self, screen):
        # Hintergrund
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Halbtransparenter Hintergrund
        screen.blit(overlay, (0, 0))
        
        # Titel
        title_text = self.font_title.render("HIGHSCORES", True, "white")
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
        
        # Einträge
        for i, entry in enumerate(self.highscore_manager.highscores):
            color = "gold" if i == 0 else "silver" if i == 1 else "#CD7F32" if i == 2 else "white"
            rank_text = self.font_entry.render(f"{i+1}.", True, color)
            name_text = self.font_entry.render(f"{entry['name']}", True, color)
            score_text = self.font_entry.render(f"{entry['score']}", True, color)
            
            x_rank = SCREEN_WIDTH // 4
            x_name = SCREEN_WIDTH // 2 - 50
            x_score = SCREEN_WIDTH * 3 // 4
            y = 150 + i * 40
            
            screen.blit(rank_text, (x_rank, y))
            screen.blit(name_text, (x_name, y))
            screen.blit(score_text, (x_score, y))
        
        # Hinweis zum Zurückkehren
        hint_text = self.font_entry.render("Drücke LEERTASTE zum Fortfahren", True, "white")
        screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, 
                             SCREEN_HEIGHT - 100))