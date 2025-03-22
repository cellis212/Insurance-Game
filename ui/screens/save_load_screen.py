# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.

import pygame
import os
from typing import List, Optional, Dict, Any, Tuple
from ui.components.colors import Colors
from ui.components.button import Button
from utils import save_game_state, load_game_state

class SaveLoadScreen:
    """Screen for saving and loading game states."""
    
    def __init__(self, screen_rect: pygame.Rect, title_font: pygame.font.Font, main_font: pygame.font.Font):
        self.rect = screen_rect
        self.title_font = title_font
        self.main_font = main_font
        
        # Create save/load sections
        self.save_section = pygame.Rect(
            screen_rect.left + 20,
            screen_rect.top + 70,
            screen_rect.width // 2 - 30,
            screen_rect.height - 100
        )
        
        self.load_section = pygame.Rect(
            screen_rect.centerx + 10,
            screen_rect.top + 70,
            screen_rect.width // 2 - 30,
            screen_rect.height - 100
        )
        
        # Create buttons
        self.close_button = Button(
            pygame.Rect(screen_rect.right - 100, screen_rect.top + 20, 80, 30),
            "Close",
            main_font,
            color=Colors.GRAY
        )
        
        self.save_button = Button(
            pygame.Rect(self.save_section.centerx - 60, self.save_section.bottom - 50, 120, 40),
            "Save Game",
            main_font,
            color=Colors.GREEN
        )
        
        # Input fields
        self.save_name = "save_game"
        self.input_active = False
        self.input_rect = pygame.Rect(
            self.save_section.left + 20,
            self.save_section.top + 80,
            self.save_section.width - 40,
            40
        )
        
        # Save slots - will be populated in render
        self.save_slots: List[Dict[str, Any]] = []
        
        self.message = ""
        self.message_color = Colors.BLACK
        self.message_timer = 0
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle events related to save/load screen."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check close button
            if self.close_button.handle_event(event):
                return "close"
            
            # Check save button
            if self.save_button.handle_event(event):
                return f"save:{self.save_name}"
            
            # Check input field activation
            if self.input_rect.collidepoint(event.pos):
                self.input_active = True
            else:
                self.input_active = False
            
            # Check save slots for loading
            for slot in self.save_slots:
                if slot["button"].handle_event(event):
                    return f"load:{slot['filename']}"
        
        # Handle text input for save name
        elif event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_BACKSPACE:
                self.save_name = self.save_name[:-1]
            elif event.key == pygame.K_RETURN:
                self.input_active = False
            else:
                # Only allow valid filename characters
                if event.unicode.isalnum() or event.unicode in "._-":
                    self.save_name += event.unicode
        
        return None
    
    def render(self, screen: pygame.Surface) -> None:
        """Render the save/load screen."""
        # Draw background
        pygame.draw.rect(screen, Colors.WHITE, self.rect)
        
        # Draw title
        title = self.title_font.render("Save / Load Game", True, Colors.BLACK)
        screen.blit(title, (self.rect.centerx - title.get_width()//2, self.rect.top + 20))
        
        # Draw close button
        self.close_button.draw(screen)
        
        # Draw save section
        pygame.draw.rect(screen, Colors.LIGHT_GRAY, self.save_section, 2)
        save_title = self.title_font.render("Save Game", True, Colors.BLUE)
        screen.blit(save_title, (self.save_section.centerx - save_title.get_width()//2, self.save_section.top + 10))
        
        # Draw input field
        active_color = Colors.BLUE if self.input_active else Colors.GRAY
        pygame.draw.rect(screen, active_color, self.input_rect, 2)
        
        # Draw input field label
        label = self.main_font.render("Save Name:", True, Colors.BLACK)
        screen.blit(label, (self.input_rect.left, self.input_rect.top - 30))
        
        # Draw save name
        text_surface = self.main_font.render(self.save_name, True, Colors.BLACK)
        screen.blit(text_surface, (self.input_rect.left + 10, self.input_rect.top + 10))
        
        # Draw save button
        self.save_button.draw(screen)
        
        # Draw load section
        pygame.draw.rect(screen, Colors.LIGHT_GRAY, self.load_section, 2)
        load_title = self.title_font.render("Load Game", True, Colors.BLUE)
        screen.blit(load_title, (self.load_section.centerx - load_title.get_width()//2, self.load_section.top + 10))
        
        # List save files
        self._refresh_save_slots()
        if not self.save_slots:
            no_saves = self.main_font.render("No saved games found", True, Colors.GRAY)
            screen.blit(no_saves, (self.load_section.centerx - no_saves.get_width()//2, self.load_section.centery))
        else:
            # Draw save slots
            for i, slot in enumerate(self.save_slots):
                slot["button"].draw(screen)
                
                # Draw save info
                save_date = self.main_font.render(slot["date"], True, Colors.BLACK)
                screen.blit(save_date, (slot["button"].rect.right + 10, slot["button"].rect.top + 5))
        
        # Draw message if any
        if self.message and self.message_timer > 0:
            message_surface = self.main_font.render(self.message, True, self.message_color)
            screen.blit(message_surface, (self.rect.centerx - message_surface.get_width()//2, self.rect.bottom - 30))
            self.message_timer -= 1
    
    def _refresh_save_slots(self) -> None:
        """Refresh the list of available save files."""
        self.save_slots = []
        save_dir = "saves"
        
        if not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)
            return
        
        # Get all .json files in saves directory
        save_files = [f for f in os.listdir(save_dir) if f.endswith('.json')]
        save_files.sort(key=lambda x: os.path.getmtime(os.path.join(save_dir, x)), reverse=True)
        
        # Create buttons for each save file
        for i, filename in enumerate(save_files):
            if i >= 5:  # Limit to 5 save slots
                break
                
            # Get file modification time
            file_path = os.path.join(save_dir, filename)
            mod_time = os.path.getmtime(file_path)
            
            # Format date
            import datetime
            date_str = datetime.datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
            
            # Create button
            button_rect = pygame.Rect(
                self.load_section.left + 20,
                self.load_section.top + 80 + i * 50,
                150,
                40
            )
            
            # Create display name (strip .json)
            display_name = filename.replace('.json', '')
            
            self.save_slots.append({
                "filename": filename,
                "date": date_str,
                "button": Button(button_rect, display_name, self.main_font)
            })
    
    def show_message(self, message: str, color: Tuple[int, int, int] = Colors.BLACK) -> None:
        """Show a temporary message on the screen."""
        self.message = message
        self.message_color = color
        self.message_timer = 120  # frames 