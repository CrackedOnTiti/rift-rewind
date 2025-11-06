from PIL import Image, ImageDraw, ImageFont
from urllib.request import urlopen
from io import BytesIO
<<<<<<< HEAD
import aiohttp, asyncio

class RewindExportProfil:
    def __init__(self, player_name: str, champion_played: str, games_played: int, kd: float, lvl: int, rank: str, title: str, story: str):
=======
import aiohttp, asyncio, re

class RewindExportProfil:
    def __init__(self, player_name: str, champion_played: str, games_played: int, kd: float, lvl: int, story: str, title: str):
>>>>>>> 2116320 (feat: rewind card generation impl)
        self.name = player_name
        self.champion_played = champion_played
        self.games_played = games_played
        self.kd = kd
        self.lvl = lvl
<<<<<<< HEAD
        self.rank = rank
        self.title = title
        self.story = story
=======
        self.story = story
        self.title = title
>>>>>>> 2116320 (feat: rewind card generation impl)

class RewindCardGeneration:
    def __init__(self, profil: RewindExportProfil):
        self.profil = profil
        self.image = None
<<<<<<< HEAD
        self.draw = None
        self.width = 356
        self.height = 591
        self.fonts = {}
        self.base_url = "https://raw.communitydragon.org/15.22/game/assets/characters"
    
    async def get_champion_splash(self, champion_name: str) -> str:
        champion_lower = champion_name.lower()
        base_path = f"{self.base_url}/{champion_lower}/skins/base"
        
        possible_patterns = [
            f"{champion_lower}_loadscreen.png",
            f"{champion_lower}_loadscreen_0.png",
            f"{champion_lower}_loadscreen_1.png",
            f"{champion_lower}_loadscreen_2.png",
            "loadscreen.png",
            "loadscreen_0.png",
            "loadscreen_1.png",
        ]
        
        async with aiohttp.ClientSession() as session:
            for pattern in possible_patterns:
                try:
                    url = f"{base_path}/{pattern}"
                    async with session.head(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                        if resp.status == 200:
                            return url
                except Exception as e:
                    continue
            
            try:
                async with session.get(base_path, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        content = await resp.text()
                        import re
                        loadscreen_files = re.findall(r'([\w_-]*loadscreen[\w_-]*\.png)', content, re.IGNORECASE)
                        if loadscreen_files:
                            first_file = loadscreen_files[0]
                            return f"{base_path}/{first_file}"
            except:
                pass
        return f"{base_path}/{champion_lower}_loadscreen.png"
    
    def get_rank_image_url(self, rank: str) -> str:
        rank_mapping = {
            "Iron": "https://static.wikia.nocookie.net/leagueoflegends/images/f/fe/Season_2022_-_Iron.png",
            "Bronze": "https://static.wikia.nocookie.net/leagueoflegends/images/e/e9/Season_2022_-_Bronze.png",
            "Silver": "https://static.wikia.nocookie.net/leagueoflegends/images/4/44/Season_2022_-_Silver.png",
            "Gold": "https://static.wikia.nocookie.net/leagueoflegends/images/8/8d/Season_2022_-_Gold.png",
            "Platinum": "https://static.wikia.nocookie.net/leagueoflegends/images/3/3b/Season_2022_-_Platinum.png",
            "Emerald": "https://static.wikia.nocookie.net/leagueoflegends/images/d/d4/Season_2023_-_Emerald.png",
            "Diamond": "https://static.wikia.nocookie.net/leagueoflegends/images/e/ee/Season_2022_-_Diamond.png",
            "Master": "https://static.wikia.nocookie.net/leagueoflegends/images/e/eb/Season_2022_-_Master.png",
            "Grandmaster": "https://static.wikia.nocookie.net/leagueoflegends/images/f/fc/Season_2022_-_Grandmaster.png",
            "Challenger": "https://static.wikia.nocookie.net/leagueoflegends/images/0/02/Season_2022_-_Challenger.png"
        }
        
        for rank_key, url in rank_mapping.items():
            if rank_key.lower() in rank.lower():
                return url
        
        return rank_mapping["Silver"]
    
    def create_base_card(self):
        self.image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 255))
        self.draw = ImageDraw.Draw(self.image)
        return self
    
    def load_fonts(self):
        try:
            self.fonts['title'] = ImageFont.truetype("arial.ttf", 16)
            self.fonts['name'] = ImageFont.truetype("arial.ttf", 24)
            self.fonts['subtitle'] = ImageFont.truetype("arial.ttf", 14)
            self.fonts['story'] = ImageFont.truetype("arial.ttf", 11)
            self.fonts['circle'] = ImageFont.truetype("arial.ttf", 20)
            self.fonts['circle_label'] = ImageFont.truetype("arial.ttf", 10)
            self.fonts['footer'] = ImageFont.truetype("arial.ttf", 9)
        except:
            default_font = ImageFont.load_default()
            self.fonts['title'] = default_font
            self.fonts['name'] = default_font
            self.fonts['subtitle'] = default_font
            self.fonts['story'] = default_font
            self.fonts['circle'] = default_font
            self.fonts['circle_label'] = default_font
            self.fonts['footer'] = default_font
        return self
    
    def draw_golden_border(self):
        """Dessine la bordure dorée style LoL"""
        gold = (218, 165, 32)
        dark_gold = (139, 101, 8)
        
        for i in range(5):
            self.draw.rectangle(
                [i, i, self.width - 1 - i, self.height - 1 - i],
                outline=gold if i % 2 == 0 else dark_gold,
                width=1
            )
        
        corner_size = 15
        for x, y in [(10, 10), (self.width - 10, 10), (10, self.height - 10), (self.width - 10, self.height - 10)]:
            self.draw.rectangle([x - 3, y - 3, x + 3, y + 3], fill=gold)
        
        return self
    
    def draw_circle_stat(self, x: int, y: int, value: str, label: str, is_rank: bool = False):
        gold = (218, 165, 32)
        dark_bg = (20, 20, 30)
        
        radius = 30
        
        self.draw.ellipse([x - radius - 3, y - radius - 3, x + radius + 3, y + radius + 3], 
                         fill=gold, outline=None)
        self.draw.ellipse([x - radius, y - radius, x + radius, y + radius], 
                         fill=dark_bg, outline=None)
        
        if is_rank:
            try:
                rank_url = self.get_rank_image_url(self.profil.rank)
                response = urlopen(rank_url)
                rank_img = Image.open(BytesIO(response.read()))
                rank_size = int(radius * 1.5)
                rank_img = rank_img.resize((rank_size, rank_size), Image.Resampling.LANCZOS)
                rank_img = rank_img.convert('RGBA')
                mask = Image.new('L', (rank_size, rank_size), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.ellipse([0, 0, rank_size, rank_size], fill=255)
                self.image.paste(rank_img, (x - rank_size // 2, y - rank_size // 2), mask)
                self.draw = ImageDraw.Draw(self.image)
            except Exception as e:
                print(f"Erreur chargement image rang: {e}")
                bbox = self.draw.textbbox((0, 0), value, font=self.fonts['circle'])
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
                self.draw.text((x - text_w // 2, y - text_h // 2), value, 
                              fill=gold, font=self.fonts['circle'])
        else:
            bbox = self.draw.textbbox((0, 0), label, font=self.fonts['circle_label'])
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            self.draw.text((x - text_w // 2, y - 12), label, 
                          fill=gold, font=self.fonts['circle_label'])
            bbox = self.draw.textbbox((0, 0), value, font=self.fonts['circle'])
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            self.draw.text((x - text_w // 2, y + 2), value, 
                          fill=gold, font=self.fonts['circle'])
        
        return self
    
    def add_champion_splash(self, champion_url: str):
        try:
            response = urlopen(champion_url)
            champ_img = Image.open(BytesIO(response.read()))
            img_width = self.width
            img_height = self.height
            
            aspect_ratio = champ_img.width / champ_img.height
            target_aspect = img_width / img_height
            
            if aspect_ratio > target_aspect:
                new_height = img_height
                new_width = int(new_height * aspect_ratio)
                champ_img = champ_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                crop_x = (new_width - img_width) // 2
                champ_img = champ_img.crop((crop_x, 0, crop_x + img_width, img_height))
            else:
                new_width = img_width
                new_height = int(new_width / aspect_ratio)
                champ_img = champ_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                crop_y = max(0, (new_height - img_height) // 4)  # Garder le haut
                champ_img = champ_img.crop((0, crop_y, img_width, crop_y + img_height))
            
            champ_img = champ_img.convert('RGBA')
            self.image.paste(champ_img, (0, 0))
            self.draw = ImageDraw.Draw(self.image)
            
        except Exception as e:
            print(f"Error: {e}")
            for y in range(self.height):
                ratio = y / self.height
                color_val = int(40 + ratio * 20)
                self.draw.line([(0, y), (self.width, y)], fill=(color_val, color_val, color_val + 20))
        
        return self
    
    def draw_info_section(self):
        gold = (218, 165, 32)
        
        info_y = self.height - 170
        info_height = 145
        padding = 15
        
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        dark_bg = (20, 25, 35, 220)
        overlay_draw.rounded_rectangle(
            [padding, info_y, self.width - padding, info_y + info_height],
            radius=15,
            fill=dark_bg
        )
        
        self.image = Image.alpha_composite(self.image, overlay)
        self.draw = ImageDraw.Draw(self.image)
        
        bbox = self.draw.textbbox((0, 0), self.profil.name, font=self.fonts['name'])
        text_w = bbox[2] - bbox[0]
        self.draw.text((self.width // 2 - text_w // 2, info_y + 20), 
                      self.profil.name, fill=(255, 255, 255), font=self.fonts['name'])
        
        bbox = self.draw.textbbox((0, 0), self.profil.title, font=self.fonts['subtitle'])
        text_w = bbox[2] - bbox[0]
        self.draw.text((self.width // 2 - text_w // 2, info_y + 52), 
                      self.profil.title, fill=gold, font=self.fonts['subtitle'])
        
        story_y = info_y + 77
        max_width = self.width - 50
        words = self.profil.story.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = self.draw.textbbox((0, 0), test_line, font=self.fonts['story'])
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        lines = lines[:3]
        
        for i, line in enumerate(lines):
            bbox = self.draw.textbbox((0, 0), line, font=self.fonts['story'])
            text_w = bbox[2] - bbox[0]
            self.draw.text((self.width // 2 - text_w // 2, story_y + i * 14), 
                          line, fill=(220, 220, 220), font=self.fonts['story'])
        
        return self
    
    def draw_header_and_footer(self):
        gold = (218, 165, 32)
        hot_pink = (255, 76, 154)
        cyan = (0, 184, 217)
        white = (255, 255, 255)
        
        header_text = "2025 REWIND"
        bbox = self.draw.textbbox((0, 0), header_text, font=self.fonts['title'])
        text_w = bbox[2] - bbox[0]
        self.draw.text((self.width // 2 - text_w // 2, 15), 
                      header_text, fill=gold, font=self.fonts['title'])
        
        footer_y = self.height - 20
        
        word1 = "Jinx's"
        word2 = "Magical"
        word3 = "Rewind Machine"
        
        bbox1 = self.draw.textbbox((0, 0), word1, font=self.fonts['footer'])
        w1 = bbox1[2] - bbox1[0]
        
        bbox2 = self.draw.textbbox((0, 0), " " + word2, font=self.fonts['footer'])
        w2 = bbox2[2] - bbox2[0]
        
        bbox3 = self.draw.textbbox((0, 0), " " + word3, font=self.fonts['footer'])
        w3 = bbox3[2] - bbox3[0]
        
        total_width = w1 + w2 + w3
        start_x = (self.width - total_width) // 2
        current_x = start_x
        self.draw.text((current_x, footer_y), word1, fill=hot_pink, font=self.fonts['footer'])
        current_x += w1
        self.draw.text((current_x, footer_y), " " + word2, fill=cyan, font=self.fonts['footer'])
        current_x += w2
        self.draw.text((current_x, footer_y), " " + word3, fill=white, font=self.fonts['footer'])
        
        return self
    
    def save(self, filename: str):
        self.image.save(filename, 'PNG')
        return self
    
    async def create_card_async(self) -> bool:
        try:
            champion_url = await self.get_champion_splash(self.profil.champion_played)
            
            self.create_base_card()
            self.add_champion_splash(champion_url)
            self.load_fonts()
            self.draw_golden_border()
            self.draw_header_and_footer()
            left_circle_x = 50
            right_circle_x = self.width - 50
            circle_y = 50
            self.draw_circle_stat(left_circle_x, circle_y, str(self.profil.lvl), "LVL")
            self.draw_circle_stat(right_circle_x, circle_y, self.profil.rank, "RANK", is_rank=True)
            self.draw_info_section()
            filename = f"{self.profil.name}_rewind_card.png"
            self.save(filename)
            return True
=======
        self.overlay = None
        self.draw = None
        self.width = 308
        self.height = 560
        self.fonts = {}
    
    async def get_champion_url(self) -> str:
        champion = self.profil.champion_played.lower()
        base = f"https://raw.communitydragon.org/15.22/game/assets/characters/{champion}/skins/base/"
        default_character = "aatroxloadscreen.png"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(base) as response:
                    response.raise_for_status()
                    html = await response.text()
                    
                    loadscreen_pattern = r'href="([^"]*loadscreen[^"]*\.png)"'
                    matches = re.findall(loadscreen_pattern, html, re.IGNORECASE)
                    if matches:
                        loadscreen_file = matches[0]
                        return base + loadscreen_file
                    else:
                        return base + default_character
        except Exception as e:
            print(f"Error fetching champion: {e}")
            return base + default_character

    def create_image(self, background_color=(0, 0, 0, 0)):
        self.image = Image.new('RGBA', (self.width, self.height), background_color)
        self.overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.overlay)
        return self
    
    def load_background(self, source):
        if isinstance(source, tuple):
            bg = Image.new('RGB', (self.width, self.height), source)
        elif source.startswith('http'):
            response = urlopen(source)
            bg = Image.open(BytesIO(response.read()))
        else:
            bg = Image.open(source)
        
        aspect_ratio = self.width / self.height
        bg_aspect = bg.width / bg.height
        
        if bg_aspect > aspect_ratio:
            new_width = int(bg.height * aspect_ratio)
            offset = (bg.width - new_width) // 2
            bg = bg.crop((offset, 0, offset + new_width, bg.height))
        else:
            new_height = int(bg.width / aspect_ratio)
            offset = (bg.height - new_height) // 2
            bg = bg.crop((0, offset, bg.width, offset + new_height))
        
        bg = bg.resize((self.width, self.height), Image.Resampling.LANCZOS)
        self.image = bg.convert('RGBA')
        return self
    
    def load_font(self, name: str, size: int, font_path: str = "arial.ttf"):
        try:
            self.fonts[name] = ImageFont.truetype(font_path, size)
        except:
            self.fonts[name] = ImageFont.load_default()
        return self
    
    def load_fonts_preset(self):
        self.load_font('player_name', 32)
        self.load_font('title', 14)
        self.load_font('stat_number', 18)
        self.load_font('stat_label', 9)
        self.load_font('story', 10)
        self.load_font('rewind', 11)
        self.load_font('copyright', 7)
        return self
    
    def draw_text(self, text: str, x: int, y: int, font_name: str = 'story', 
                  color=(255, 255, 255, 255), align='left', stroke_width=0, stroke_fill=None):
        font = self.fonts.get(font_name)
        if not font:
            raise ValueError(f"Font '{font_name}' not loaded")
        
        if align == 'center':
            bbox = self.draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
        elif align == 'right':
            bbox = self.draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = x - text_width

        self.draw.text((x, y), text, fill=color, font=font, 
                      stroke_width=stroke_width, stroke_fill=stroke_fill)
        return self
    
    def draw_golden_frame(self):
        outer_border = 5
        inner_border = 2
        
        for i in range(outer_border):
            alpha = int(255 * (1 - i / outer_border))
            gold = (255, 215, 0, alpha)
            self.draw.rectangle([i, i, self.width-i-1, self.height-i-1], 
                               outline=gold, width=1)
        
        offset = outer_border + 2
        for i in range(inner_border):
            alpha = 180 - (i * 40)
            gold = (255, 215, 0, alpha)
            self.draw.rectangle([offset+i, offset+i, 
                                self.width-offset-i-1, self.height-offset-i-1], 
                               outline=gold, width=1)
        
        corner_size = 20
        corners = [
            (outer_border, outer_border),
            (self.width - outer_border - corner_size, outer_border),
            (outer_border, self.height - outer_border - corner_size),
            (self.width - outer_border - corner_size, self.height - outer_border - corner_size)
        ]
        
        for cx, cy in corners:
            self.draw.rectangle([cx, cy, cx+corner_size, cy+corner_size],
                               outline=(255, 215, 0, 100), width=1)
            self.draw.line([(cx, cy), (cx+corner_size, cy+corner_size)],
                          fill=(255, 215, 0, 80), width=1)
        
        return self
    
    def draw_gradient_overlay_bottom(self):
        height_px = 210
        gradient = Image.new('RGBA', (self.width, height_px))
        draw = ImageDraw.Draw(gradient)
        
        for y in range(height_px):
            ratio = 1 - (y / height_px)
            opacity = min(255, int(ratio * ratio * 400))
            draw.line([(0, y), (self.width, y)], fill=(0, 0, 0, opacity))
        
        self.image.paste(gradient, (0, self.height - height_px), gradient)
        return self
    
    def draw_gradient_overlay_top(self):
        height_px = 100
        gradient = Image.new('RGBA', (self.width, height_px))
        draw = ImageDraw.Draw(gradient)
        
        for y in range(height_px):
            ratio = y / height_px
            opacity = int((1 - ratio) * (1 - ratio) * 200)
            draw.line([(0, y), (self.width, y)], fill=(0, 0, 0, opacity))
        
        self.image.paste(gradient, (0, 0), gradient)
        return self
    
    def draw_stat_orb(self, center_x, center_y, radius, value, label):
        outer_glow = radius + 4
        for r in range(outer_glow, radius, -1):
            alpha = int(100 * (1 - (outer_glow - r) / 4))
            self.draw.ellipse([center_x - r, center_y - r, 
                              center_x + r, center_y + r],
                             outline=(255, 215, 0, alpha), width=1)
        
        self.draw.ellipse([center_x - radius, center_y - radius, 
                          center_x + radius, center_y + radius],
                         fill=(10, 10, 20, 220), 
                         outline=(255, 215, 0, 255), width=2)
        
        self.draw.ellipse([center_x - radius + 2, center_y - radius + 2, 
                          center_x + radius - 2, center_y + radius - 2],
                         outline=(255, 235, 100, 180), width=1)
        
        value_str = str(value)
        bbox = self.draw.textbbox((0, 0), value_str, font=self.fonts['stat_number'])
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        self.draw.text((center_x - text_width//2, center_y - text_height//2 - 3), 
                      value_str, fill=(255, 215, 0, 255), 
                      font=self.fonts['stat_number'],
                      stroke_width=1, stroke_fill=(0, 0, 0, 200))
        
        bbox_label = self.draw.textbbox((0, 0), label, font=self.fonts['stat_label'])
        label_width = bbox_label[2] - bbox_label[0]
        
        self.draw.text((center_x - label_width//2, center_y + 8), 
                      label, fill=(200, 200, 200, 255), 
                      font=self.fonts['stat_label'])
    
    def draw_name_frame(self, y_start):
        frame_height = 140
        padding = 15
        
        frame_top = y_start
        frame_bottom = y_start + frame_height
        
        self.draw.rounded_rectangle([padding, frame_top, 
                                     self.width - padding, frame_bottom],
                                   radius=8, fill=(30, 30, 40, 200))
        
        self.draw.rounded_rectangle([padding, frame_top, 
                                     self.width - padding, frame_bottom],
                                   radius=8, outline=(60, 60, 70, 180), width=1)
        
        return frame_top
    
    def merge_layers(self):
        if self.image and self.overlay:
            self.image = Image.alpha_composite(self.image, self.overlay)
        return self
    
    def save(self, filename: str):
        if not self.image:
            raise ValueError("No image to save")
        
        self.merge_layers()
        self.image.save(filename, 'PNG')
        return self
    
    async def image_creation_async(self) -> bool:
        try:
            champion_url = await self.get_champion_url()
            
            self.create_image()
            
            if champion_url:
                self.load_background(champion_url)
            else:
                self.load_background((15, 25, 40))
            
            self.load_fonts_preset()
            
            self.draw_gradient_overlay_top()
 
            self.draw_golden_frame()
            
            self.draw_text("2025 REWIND", self.width//2, 15, 'rewind', 
                          (255, 215, 0, 255), align='center',
                          stroke_width=1, stroke_fill=(0, 0, 0, 200))
            
            orb_radius = 24
            orb_y = 55
            self.draw_stat_orb(35, orb_y, orb_radius, self.profil.lvl, "LVL")
            self.draw_stat_orb(self.width - 35, orb_y, orb_radius, self.profil.kd, "K/D")
            
            frame_y = self.height - 165
            self.draw_name_frame(frame_y)
            
            name_y = frame_y + 10
            self.draw_text(self.profil.name, 0, name_y, 'player_name', 
                          (255, 255, 255, 255), align='center',
                          stroke_width=2, stroke_fill=(0, 0, 0, 220))
            
            title_y = frame_y + 50
            self.draw_text(self.profil.title, 0, title_y, 'title', 
                          (200, 200, 200, 255), align='center',
                          stroke_width=1, stroke_fill=(0, 0, 0, 180))
            
            story_y = title_y + 23
            
            story_lines = []
            words = self.profil.story.split()
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                bbox = self.draw.textbbox((0, 0), test_line, font=self.fonts['story'])
                if bbox[2] - bbox[0] < self.width - 50:
                    current_line = test_line
                else:
                    if current_line:
                        story_lines.append(current_line)
                    current_line = word
            
            if current_line:
                story_lines.append(current_line)
            
            story_lines = story_lines[:3]
            
            for i, line in enumerate(story_lines):
                self.draw_text(line, 0, story_y + i * 13, 'story', 
                              (220, 220, 220, 255), align='center')
            
            jinx_text = "Jinx's"
            magical_text = " Magical "
            rewind_text = "Rewind Machine"
            
            bbox_jinx = self.draw.textbbox((0, 0), jinx_text, font=self.fonts['copyright'])
            bbox_magical = self.draw.textbbox((0, 0), jinx_text + magical_text, font=self.fonts['copyright'])
            bbox_total = self.draw.textbbox((0, 0), jinx_text + magical_text + rewind_text, font=self.fonts['copyright'])
            
            total_width = bbox_total[2] - bbox_total[0]
            jinx_width = bbox_jinx[2] - bbox_jinx[0]
            magical_width = bbox_magical[2] - bbox_magical[0]
            
            start_x = (self.width - total_width) // 2
            
            self.draw.text((start_x, self.height - 22), jinx_text, 
                          fill=(255, 76, 154, 255), font=self.fonts['copyright'])
            
            self.draw.text((start_x + jinx_width, self.height - 22), magical_text, 
                          fill=(0, 184, 217, 255), font=self.fonts['copyright'])
            
            self.draw.text((start_x + magical_width, self.height - 22), rewind_text, 
                          fill=(255, 255, 255, 255), font=self.fonts['copyright'])
            self.save(f"{self.profil.name}_rewind_card.png")
            print(f"Card created: {self.profil.name}_rewind_card.png")
            return True

>>>>>>> 2116320 (feat: rewind card generation impl)
        except Exception as e:
            print(f"Error: {e}")
            return False
    
<<<<<<< HEAD
    def create_card(self) -> bool:
        return asyncio.run(self.create_card_async())


def main():
    profil = RewindExportProfil(
        player_name="Faker",
        champion_played="Ahri",
        games_played=342,
        kd=4.2,
        lvl=287,
        rank="Silver",
        title="The Unkillable Demon King",
        story="The legend continues with style and precision across the Rift"
    )
    generator = RewindCardGeneration(profil)
    generator.create_card()

if __name__ == "__main__":
=======
    def image_creation(self) -> bool:
        return asyncio.run(self.image_creation_async())

def main():
    print("Generating LOL Rewind Card...")
    profil = RewindExportProfil(
        player_name="Faker", 
        champion_played="Annie", 
        games_played=342,
        kd=4.2, 
        lvl=287, 
        story="The legend continues with style and precision across the Rift.",
        title="The Unkillable Demon King" 
    )
    rewind = RewindCardGeneration(profil)
    rewind.image_creation()

if __name__=="__main__":
>>>>>>> 2116320 (feat: rewind card generation impl)
    main()
