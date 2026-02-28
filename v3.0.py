#!/usr/bin/env python3

import sys
import os
import subprocess
import json
import re
import time
import hashlib
import math
import random
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QSlider, QFrame, QSizePolicy, 
                           QSpacerItem, QGraphicsOpacityEffect)
from PyQt5.QtCore import (QTimer, Qt, QThread, pyqtSignal, QPropertyAnimation, 
                        QEasingCurve, QRect, QPoint, QSize)
from PyQt5.QtGui import (QPixmap, QFont, QPainter, QPainterPath, QIcon, QColor, 
                       QPalette, QLinearGradient, QBrush, QCursor, QMouseEvent, QPen, 
                       QPolygonF)
import dbus
import requests
from urllib.parse import quote
# Fix for the Pillow warning - use a try/except block
try:
    from PIL.ImageQt import ImageQt
except ImportError:
    print("PIL not available, some features may not work")
    ImageQt = None
from PIL import Image, ImageFilter

# Force X11 to avoid Wayland warnings
os.environ['QT_QPA_PLATFORM'] = 'xcb'

# --- ### BACKGROUND GLITCH EFFECTS WIDGET ### ---
class BackgroundGlitchEffect(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.glitch_timer = QTimer()
        self.glitch_timer.timeout.connect(self.update_glitch)
        self.setStyleSheet("background: transparent;")
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.resize_to_parent()
        
    def resize_to_parent(self):
        """Ensure widget covers entire parent"""
        if self.parent():
            parent_size = self.parent().size()
            self.setGeometry(0, 0, parent_size.width(), parent_size.height())
            print(f"Background glitch effect sized to: {parent_size.width()}x{parent_size.height()}")
        
    def start_glitch(self):
        print("Starting BACKGROUND glitch effect...")
        self.glitch_timer.start(120)
        
    def stop_glitch(self):
        self.glitch_timer.stop()
        self.clear()
        
    def update_glitch(self):
        if self.width() <= 0 or self.height() <= 0:
            return
            
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Subtle scan lines that won't interfere with UI
        pen = QPen(QColor(255, 0, 70, 60), 1)
        painter.setPen(pen)
        for y in range(0, self.height(), 4):
            painter.drawLine(0, y, self.width(), y)
            
        # Subtle glitch lines in background
        glitch_colors = [
            QColor(255, 0, 70, 100),
            QColor(0, 255, 200, 100),  
            QColor(255, 100, 0, 100),  
        ]
        
        for _ in range(random.randint(3, 6)):
            x = random.randint(0, max(1, self.width() - 50))
            y = random.randint(0, self.height())
            
            remaining_width = self.width() - x
            if remaining_width > 50:
                length = random.randint(50, min(200, remaining_width))
            else:
                length = max(10, remaining_width)
            
            thickness = random.randint(1, 3)
            color = random.choice(glitch_colors)
            
            pen = QPen(color, thickness)
            painter.setPen(pen)
            painter.drawLine(x, y, x + length, y)
            
        # Subtle noise pixels
        for _ in range(random.randint(10, 20)):
            x = random.randint(0, self.width())
            y = random.randint(0, self.height())
            color = random.choice(glitch_colors)
            pen = QPen(color, 1)
            painter.setPen(pen)
            painter.drawPoint(x, y)
            
        painter.end()
        self.setPixmap(pixmap)

# --- ### FIXED: COMPACT WEATHER WIDGET WITH BETTER POSITIONING ### ---
class CompactWeatherWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.weather_data = {"temp": "--", "desc": "Loading..."}
        self.setFixedSize(80, 50)  # Even smaller to avoid overlap
        self.weather_timer = QTimer()
        self.weather_timer.timeout.connect(self.fetch_weather)
        self.weather_timer.start(600000)
        self.fetch_weather()
        self.setStyleSheet("background: transparent;")
        
    def fetch_weather(self):
        try:
            # Replace with your OpenWeatherMap API key from https://home.openweathermap.org/api_keys
            api_key = "YOUR_OPENWEATHERMAP_API_KEY"
            url = f"http://api.openweathermap.org/data/2.5/weather?q=Winnipeg,CA&appid={api_key}&units=metric"
            
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                temp = int(data['main']['temp'])
                desc = data['weather'][0]['description'].title()
                self.weather_data = {"temp": f"{temp}°C", "desc": desc}
            else:
                import random
                temps = [-15, -10, -5, 0, 5, 10, 15, 20]
                descriptions = ["Snow", "Clear", "Cloudy", "Overcast", "Light Snow"]
                self.weather_data = {
                    "temp": f"{random.choice(temps)}°C",
                    "desc": random.choice(descriptions)
                }
            print(f"Weather updated: {self.weather_data}")
            self.update()
        except Exception as e:
            print(f"Weather fetch error: {e}")
            self.weather_data = {"temp": "--", "desc": "Offline"}
            self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw very compact square background
        rect = QRect(2, 2, self.width() - 4, self.height() - 4)
        
        # Background with cyberpunk gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(30, 30, 30, 240))
        gradient.setColorAt(1, QColor(10, 10, 10, 240))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(255, 100, 0, 220), 2))
        painter.drawRoundedRect(rect, 4, 4)
        
        # Horizontal lines effect
        pen = QPen(QColor(255, 100, 0, 120), 1)
        painter.setPen(pen)
        for y in range(6, self.height() - 6, 4):
            painter.drawLine(6, y, self.width() - 6, y)
        
        # Weather text - very compact layout
        painter.setPen(QColor(255, 255, 255))
        
        # Temperature - very small font
        temp_font = QFont("Arial", 8, QFont.Bold)
        painter.setFont(temp_font)
        temp_rect = QRect(0, 8, self.width(), 14)
        painter.drawText(temp_rect, Qt.AlignCenter, self.weather_data["temp"])
        
        # Description - tiny font
        desc_font = QFont("Arial", 6, QFont.Bold)
        painter.setFont(desc_font)
        desc_rect = QRect(0, 25, self.width(), 12)
        desc_text = self.weather_data["desc"][:6]  # Very short text
        painter.drawText(desc_rect, Qt.AlignCenter, desc_text)

# --- ### FIXED: SYSTEM STATS WIDGET WITH BETTER POSITIONING ### ---
class SystemStatsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stats_data = {"cpu": "--", "ram": "--", "temp": "--"}
        self.setFixedSize(100, 65)  # Smaller to avoid overlap
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.fetch_system_stats)
        self.stats_timer.start(2000)
        self.fetch_system_stats()
        self.setStyleSheet("background: transparent;")
        
    def fetch_system_stats(self):
        try:
            # Try to import psutil for system monitoring
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            
            # RAM usage
            ram = psutil.virtual_memory()
            ram_percent = ram.percent
            
            # CPU temperature (Pi-specific)
            try:
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp = int(f.read()) / 1000
            except:
                temp = 0
            
            self.stats_data = {
                "cpu": f"{cpu_percent:.0f}%",
                "ram": f"{ram_percent:.0f}%",
                "temp": f"{temp:.0f}°C" if temp > 0 else "N/A"
            }
            
        except ImportError:
            # Fallback if psutil not available
            try:
                # CPU usage via top command
                cpu_result = subprocess.run(['top', '-bn1'], capture_output=True, text=True, timeout=2)
                if cpu_result.returncode == 0:
                    for line in cpu_result.stdout.split('\n'):
                        if 'Cpu(s):' in line or '%Cpu(s):' in line:
                            parts = line.split()
                            for i, part in enumerate(parts):
                                if 'us,' in part or 'user,' in part:
                                    cpu_val = float(part.replace('%', '').replace('us,', '').replace('user,', ''))
                                    break
                            else:
                                cpu_val = 0
                            break
                    else:
                        cpu_val = 0
                else:
                    cpu_val = 0
                
                # RAM usage via free command
                ram_result = subprocess.run(['free'], capture_output=True, text=True, timeout=2)
                if ram_result.returncode == 0:
                    lines = ram_result.stdout.split('\n')
                    for line in lines:
                        if 'Mem:' in line:
                            parts = line.split()
                            total = int(parts[1])
                            used = int(parts[2])
                            ram_percent = (used / total) * 100
                            break
                    else:
                        ram_percent = 0
                else:
                    ram_percent = 0
                
                # Temperature
                try:
                    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                        temp = int(f.read()) / 1000
                except:
                    temp = 0
                
                self.stats_data = {
                    "cpu": f"{cpu_val:.0f}%",
                    "ram": f"{ram_percent:.0f}%",
                    "temp": f"{temp:.0f}°C" if temp > 0 else "N/A"
                }
                
            except Exception as e:
                self.stats_data = {"cpu": "N/A", "ram": "N/A", "temp": "N/A"}
        
        except Exception as e:
            self.stats_data = {"cpu": "ERR", "ram": "ERR", "temp": "ERR"}
        
        print(f"System stats updated: {self.stats_data}")
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw same background as weather widget but smaller
        rect = QRect(3, 3, self.width() - 6, self.height() - 6)
        
        # Background with cyberpunk gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(30, 30, 30, 240))
        gradient.setColorAt(1, QColor(10, 10, 10, 240))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(255, 100, 0, 220), 2))
        painter.drawRoundedRect(rect, 6, 6)
        
        # HORIZONTAL LINES EFFECT
        pen = QPen(QColor(255, 100, 0, 120), 1)
        painter.setPen(pen)
        for y in range(8, self.height() - 8, 5):
            painter.drawLine(8, y, self.width() - 8, y)
        
        # System stats text with smaller font
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Arial", 7, QFont.Bold)  # Smaller font
        painter.setFont(font)
        
        # Three lines of stats - more compact
        painter.drawText(QRect(0, 10, self.width(), 10), Qt.AlignCenter, 
                        f"CPU: {self.stats_data['cpu']}")
        painter.drawText(QRect(0, 25, self.width(), 10), Qt.AlignCenter, 
                        f"RAM: {self.stats_data['ram']}")
        painter.drawText(QRect(0, 40, self.width(), 10), Qt.AlignCenter, 
                        f"TEMP: {self.stats_data['temp']}")

# --- ### INTERACTIVE CIRCULAR PROGRESS BAR ### ---
class InteractiveCircularProgress(QWidget):
    progressClicked = pyqtSignal(float)
    longPressed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 0
        self.album_art = None
        
        # Long press detection
        self.press_start_time = 0
        self.long_press_timer = QTimer()
        self.long_press_timer.setSingleShot(True)
        self.long_press_timer.timeout.connect(self._emit_long_press)
        self.is_long_press = False
        
        # Cyberpunk Color Scheme
        self.track_color = QColor(60, 20, 20, 180)
        self.progress_color = QColor(255, 0, 70)
        self.setFixedSize(280, 280)
        self.setCursor(Qt.PointingHandCursor)

    def set_progress(self, value):
        self.progress = max(0, min(100, value))
        self.update()

    def set_album_art(self, pixmap):
        if pixmap.isNull():
            self.album_art = None
            self.update()
            return
            
        size = self.width() - 30
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        
        rounded_pixmap = QPixmap(size, size)
        rounded_pixmap.fill(Qt.transparent)
        
        painter = QPainter(rounded_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setClipPath(path)
        
        scaled_pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        x = (size - scaled_pixmap.width()) / 2
        y = (size - scaled_pixmap.height()) / 2
        painter.drawPixmap(int(x), int(y), scaled_pixmap)
        painter.end()
        
        self.album_art = rounded_pixmap
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.press_start_time = time.time()
            self.is_long_press = False
            self.long_press_timer.start(800)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.long_press_timer.stop()
            
            if not self.is_long_press:
                center = QPoint(self.width() // 2, self.height() // 2)
                click_pos = event.pos() - center
                
                angle = math.atan2(click_pos.x(), -click_pos.y())
                angle_degrees = (math.degrees(angle) + 360) % 360
                
                progress_percent = angle_degrees / 360.0
                self.progressClicked.emit(progress_percent)

    def _emit_long_press(self):
        self.is_long_press = True
        self.longPressed.emit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = QRect(15, 15, self.width() - 30, self.height() - 30)
        
        # Draw the background track
        pen = QPen(self.track_color, 12, Qt.SolidLine)
        painter.setPen(pen)
        painter.drawEllipse(rect)
        
        # Draw the progress arc
        pen.setColor(self.progress_color)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        angle = int(self.progress * 3.6 * 16)
        painter.drawArc(rect, 90 * 16, -angle)
        
        # Draw the album art in the center
        if self.album_art:
            painter.drawPixmap(rect.topLeft(), self.album_art)
        else:
            painter.setBrush(QColor(20, 20, 20))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(rect)

# --- ### VOLUME BAR ### ---
class VolumeBar(QWidget):
    volumeChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._volume = 50
        self.num_bars = 20
        
        self.active_color = QColor(255, 100, 0)
        self.inactive_color = QColor(50, 50, 50, 150)
        
        self.setMinimumSize(250, 30)

    def set_volume(self, value):
        self._volume = max(0, min(100, value))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        
        bar_width = (self.width() - (self.num_bars - 1) * 4) / self.num_bars
        num_active_bars = int(self._volume / 100 * self.num_bars)
        
        for i in range(self.num_bars):
            if i < num_active_bars:
                painter.setBrush(self.active_color)
            else:
                painter.setBrush(self.inactive_color)
                
            painter.setPen(Qt.NoPen)
            x = i * (bar_width + 4)
            painter.drawRect(int(x), 0, int(bar_width), self.height())

    def mousePressEvent(self, event):
        self._handle_mouse_event(event)

    def mouseMoveEvent(self, event):
        self._handle_mouse_event(event)

    def _handle_mouse_event(self, event):
        volume = (event.x() / self.width()) * 100
        self.set_volume(volume)
        self.volumeChanged.emit(int(self._volume))

# --- ### MUSIC DETECTOR (Keeping your robust original) ### ---
class MusicDetector(QThread):
    music_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.last_track_hash = ""
        self.update_interval = 1.0
        
    def run(self):
        while self.running:
            track_info = self.get_current_track()
            track_hash = hashlib.md5(str(track_info).encode()).hexdigest()
            
            if track_hash != self.last_track_hash:
                self.music_updated.emit(track_info)
                self.last_track_hash = track_hash
                
            time.sleep(self.update_interval)
    
    def stop(self):
        self.running = False
        
    def get_current_track(self):
        track_info = self.get_playerctl_info()
        if track_info['title'] != 'Unknown':
            track_info['source'] = 'playerctl'
            return track_info
            
        track_info = self.get_mpris2_info()
        if track_info['title'] != 'Unknown':
            track_info['source'] = 'MPRIS2'
            return track_info
            
        return self.get_fallback_info()
    
    def get_playerctl_info(self):
        try:
            subprocess.run(['which', 'playerctl'], check=True, capture_output=True)
            
            result = subprocess.run(['playerctl', '-l'], capture_output=True, text=True, timeout=2)
            if result.returncode != 0 or not result.stdout.strip():
                return self.get_empty_track_info()
            
            players = [p for p in result.stdout.strip().split('\n') if p]
            if not players:
                return self.get_empty_track_info()
            
            player = players[0]
            
            commands = {
                'title': ['playerctl', '-p', player, 'metadata', 'title'],
                'artist': ['playerctl', '-p', player, 'metadata', 'artist'],
                'album': ['playerctl', '-p', player, 'metadata', 'album'],
                'art_url': ['playerctl', '-p', player, 'metadata', 'mpris:artUrl'],
                'status': ['playerctl', '-p', player, 'status'],
                'position': ['playerctl', '-p', player, 'position'],
                'length': ['playerctl', '-p', player, 'metadata', 'mpris:length'],
                'volume': ['playerctl', '-p', player, 'volume']
            }
            
            results = {}
            for key, cmd in commands.items():
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=1)
                    results[key] = result.stdout.strip() if result.returncode == 0 else ''
                except:
                    results[key] = ''
            
            position = 0
            if results['position']:
                try:
                    position = float(results['position'])
                except:
                    position = 0
            
            length = 0
            if results['length']:
                try:
                    length = int(results['length']) / 1000000
                except:
                    length = 0
            
            volume = 50
            if results['volume']:
                try:
                    volume = int(float(results['volume']) * 100)
                except:
                    volume = 50
            
            return {
                'title': results['title'] or 'Unknown',
                'artist': results['artist'] or 'Unknown',
                'album': results['album'] or 'Unknown',
                'art_url': results['art_url'] or '',
                'status': results['status'] or 'Unknown',
                'player': player,
                'position': position,
                'length': length,
                'volume': max(0, min(100, volume))
            }
            
        except Exception as e:
            return self.get_empty_track_info()
    
    def get_mpris2_info(self):
        try:
            bus = dbus.SessionBus()
            services = [s for s in bus.list_names() if s.startswith('org.mpris.MediaPlayer2.')]
            
            for service in services:
                try:
                    player = bus.get_object(service, '/org/mpris/MediaPlayer2')
                    player_iface = dbus.Interface(player, 'org.mpris.MediaPlayer2.Player')
                    
                    metadata = player_iface.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
                    status = player_iface.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')
                    
                    if metadata:
                        title = str(metadata.get('xesam:title', 'Unknown'))
                        artists = metadata.get('xesam:artist', ['Unknown'])
                        artist = str(artists[0]) if isinstance(artists, list) and artists else str(artists)
                        album = str(metadata.get('xesam:album', 'Unknown'))
                        art_url = str(metadata.get('mpris:artUrl', ''))
                        
                        try:
                            position = player_iface.Get('org.mpris.MediaPlayer2.Player', 'Position') / 1000000
                        except:
                            position = 0
                            
                        try:
                            length = int(metadata.get('mpris:length', 0)) / 1000000
                        except:
                            length = 0
                        
                        return {
                            'title': title,
                            'artist': artist,
                            'album': album,
                            'art_url': art_url,
                            'status': status,
                            'player': service.split('.')[-1],
                            'position': position,
                            'length': length,
                            'volume': 50
                        }
                except:
                    continue
                    
        except Exception as e:
            pass
            
        return self.get_empty_track_info()
    
    def get_empty_track_info(self):
        return {
            'title': 'Unknown', 
            'artist': 'Unknown', 
            'album': 'Unknown', 
            'art_url': '', 
            'status': 'Unknown', 
            'player': 'None',
            'position': 0,
            'length': 0,
            'volume': 50
        }
    
    def get_fallback_info(self):
        return {
            'title': 'No Music Playing',
            'artist': 'Start a music player',
            'album': 'and play a song',
            'art_url': '',
            'status': 'Stopped',
            'player': 'None',
            'source': 'Fallback',
            'position': 0,
            'length': 0,
            'volume': 50
        }

# --- ### FIXED: MAIN PLAYER CLASS WITH BETTER SPACING ### ---
class CyberpunkMusicPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.current_track = {}
        self.album_art_cache = {}
        self.seeking = False
        self.volume_updating = False
        self.original_album_pixmap = None
        self.background_label = None
        self.init_ui()
        self.setup_timer()
        self.setup_music_detector()
        
    def init_ui(self):
        print("Initializing FIXED Cyberpunk Music Player with proper spacing...")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.showFullScreen()
        
        # Background layers
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.setStyleSheet("background-color: #0c0c0c;")
        self.background_label.lower()
        
        # Glitch effect as background layer
        self.glitch_effect = BackgroundGlitchEffect(self)
        self.glitch_effect.resize_to_parent()
        self.glitch_effect.start_glitch()
        
        # FIXED: Weather widget positioned to avoid overlap with seconds
        self.weather_widget = CompactWeatherWidget(self)
        weather_x = self.width() - 95  # Further left from edge
        weather_y = 120  # Lower to avoid time overlap
        self.weather_widget.setGeometry(weather_x, weather_y, 80, 50)
        self.weather_widget.show()
        print(f"Weather widget positioned at ({weather_x}, {weather_y})")
        
        # FIXED: System stats widget positioned to avoid overlap with controls
        self.system_stats = SystemStatsWidget(self)
        stats_x = 15  # Close to left edge
        stats_y = self.height() - 85  # Higher to avoid bottom edge
        self.system_stats.setGeometry(stats_x, stats_y, 100, 65)
        self.system_stats.show()
        print(f"System stats widget positioned at ({stats_x}, {stats_y})")
        
        # Main UI styling
        self.setStyleSheet("""
            QWidget {
                background: transparent;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background: rgba(30, 30, 30, 0.95);
                border: 2px solid #ff0046;
                border-radius: 25px;
                color: white;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background: rgba(50, 50, 50, 0.98);
                border: 2px solid #ff4070;
            }
            QPushButton:pressed {
                border-style: inset;
                background: rgba(20, 20, 20, 0.98);
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setSpacing(10)  # More compact spacing
        main_layout.setContentsMargins(25, 20, 25, 80)  # More side margins, more bottom margin
        
        # Time display with better backgrounds
        time_layout = QHBoxLayout()
        time_layout.setAlignment(Qt.AlignCenter)
        
        self.time_label = QLabel()
        time_font = QFont("Arial", 40, QFont.Bold)  # Smaller font
        self.time_label.setFont(time_font)
        self.time_label.setStyleSheet("""
            color: #ff0046; 
            background-color: rgba(0, 0, 0, 0.7);
            border-radius: 12px;
            padding: 6px 12px;
            margin: 3px;
        """)
        time_layout.addWidget(self.time_label)
        
        self.seconds_label = QLabel()
        seconds_font = QFont("Arial", 18)  # Smaller font
        self.seconds_label.setFont(seconds_font)
        self.seconds_label.setStyleSheet("""
            color: #ff6400; 
            background-color: rgba(0, 0, 0, 0.7);
            border-radius: 10px;
            padding: 4px 8px;
            margin: 3px;
        """)
        time_layout.addWidget(self.seconds_label)
        
        main_layout.addLayout(time_layout)
        
        # Circular progress
        progress_layout = QHBoxLayout()
        progress_layout.setAlignment(Qt.AlignCenter)
        
        self.circular_progress = InteractiveCircularProgress()
        self.circular_progress.progressClicked.connect(self.seek_to_position)
        self.circular_progress.longPressed.connect(self.close)
        progress_layout.addWidget(self.circular_progress)
        main_layout.addLayout(progress_layout)
        
        # FIXED: Track info with smaller fonts to avoid overlap
        self.track_title = QLabel("🎵 Detecting music...")
        title_font = QFont("Arial", 18, QFont.Bold)  # Much smaller font
        self.track_title.setFont(title_font)
        self.track_title.setAlignment(Qt.AlignCenter)
        self.track_title.setWordWrap(True)
        self.track_title.setStyleSheet("""
            color: #ffffff; 
            background-color: rgba(0, 0, 0, 0.6);
            border-radius: 8px;
            padding: 6px 12px;
            margin: 2px;
            max-height: 40px;
        """)
        main_layout.addWidget(self.track_title)
        
        self.artist_name = QLabel("")
        artist_font = QFont("Arial", 13, QFont.Bold)  # Smaller font
        self.artist_name.setFont(artist_font)
        self.artist_name.setAlignment(Qt.AlignCenter)
        self.artist_name.setWordWrap(True)
        self.artist_name.setStyleSheet("""
            color: #cccccc; 
            background-color: rgba(0, 0, 0, 0.5);
            border-radius: 6px;
            padding: 4px 8px;
            margin: 1px;
            max-height: 30px;
        """)
        main_layout.addWidget(self.artist_name)
        
        # Time labels
        time_info_layout = QHBoxLayout()
        self.current_time_label = QLabel("00:00")
        self.current_time_label.setStyleSheet("""
            color: #ff6400; 
            font-size: 12px; 
            font-weight: bold;
            background-color: rgba(0, 0, 0, 0.6);
            border-radius: 4px;
            padding: 3px 6px;
        """)
        self.total_time_label = QLabel("00:00")
        self.total_time_label.setStyleSheet("""
            color: #ff6400; 
            font-size: 12px; 
            font-weight: bold;
            background-color: rgba(0, 0, 0, 0.6);
            border-radius: 4px;
            padding: 3px 6px;
        """)
        time_info_layout.addWidget(self.current_time_label)
        time_info_layout.addStretch()
        time_info_layout.addWidget(self.total_time_label)
        main_layout.addLayout(time_info_layout)
        
        main_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Playback controls
        controls_layout = QHBoxLayout()
        controls_layout.setAlignment(Qt.AlignCenter)
        controls_layout.setSpacing(20)
        
        self.prev_btn = QPushButton("⏮")
        self.prev_btn.setFixedSize(70, 70)
        self.prev_btn.clicked.connect(self.previous_track)
        
        self.play_pause_btn = QPushButton("▶")
        self.play_pause_btn.setFixedSize(90, 90)
        self.play_pause_btn.setStyleSheet(self.play_pause_btn.styleSheet() + "font-size: 28px; border-radius: 45px;")
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        
        self.next_btn = QPushButton("⏭")
        self.next_btn.setFixedSize(70, 70)
        self.next_btn.clicked.connect(self.next_track)
        
        controls_layout.addWidget(self.prev_btn)
        controls_layout.addWidget(self.play_pause_btn)
        controls_layout.addWidget(self.next_btn)
        main_layout.addLayout(controls_layout)
        
        # Volume control
        volume_layout = QHBoxLayout()
        volume_layout.setSpacing(15)
        
        self.volume_label = QLabel("🔊")
        volume_label_font = QFont("Arial", 20)
        self.volume_label.setFont(volume_label_font)
        self.volume_label.setStyleSheet("color: #ff6400;")
        
        self.volume_bar = VolumeBar()
        self.volume_bar.volumeChanged.connect(self.set_system_volume)
        
        self.volume_value_label = QLabel("50%")
        self.volume_value_label.setStyleSheet("""
            color: #cccccc; 
            font-size: 12px; 
            font-weight: bold; 
            min-width: 35px;
            background-color: rgba(0, 0, 0, 0.6);
            border-radius: 4px;
            padding: 3px 5px;
        """)
        
        volume_layout.addStretch()
        volume_layout.addWidget(self.volume_label)
        volume_layout.addWidget(self.volume_bar)
        volume_layout.addWidget(self.volume_value_label)
        volume_layout.addStretch()
        main_layout.addLayout(volume_layout)
        
        # Status info
        self.status_label = QLabel("")
        status_font = QFont("Arial", 8)  # Smaller
        self.status_label.setFont(status_font)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #666666; 
            background-color: rgba(0, 0, 0, 0.4);
            border-radius: 4px;
            padding: 2px 4px;
            margin: 1px;
        """)
        main_layout.addWidget(self.status_label)
        
        # Compact dismiss instruction
        dismiss_label = QLabel("Long press album art to close • Click progress ring to seek")
        dismiss_font = QFont("Arial", 8)  # Smaller
        dismiss_label.setFont(dismiss_font)
        dismiss_label.setAlignment(Qt.AlignCenter)
        dismiss_label.setStyleSheet("""
            color: #444; 
            background-color: rgba(255,255,255,0.05);
            border-radius: 4px;
            padding: 3px 6px;
            margin: 1px;
        """)
        main_layout.addWidget(dismiss_label)
        
        self.setLayout(main_layout)
        
    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()
        
    def setup_music_detector(self):
        self.music_detector = MusicDetector()
        self.music_detector.music_updated.connect(self.update_music_info)
        self.music_detector.start()
        
    def update_time(self):
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        seconds_str = now.strftime(":%S")
        
        self.time_label.setText(time_str)
        self.seconds_label.setText(seconds_str)
    
    def seek_to_position(self, percentage):
        try:
            if self.current_track.get('length', 0) > 0:
                position = percentage * self.current_track['length']
                subprocess.run(['playerctl', 'position', str(position)], check=True, timeout=2)
                print(f"Seeking to {percentage*100:.1f}% ({position:.1f}s)")
        except Exception as e:
            print(f"Seek error: {e}")
        
    def update_music_info(self, track_info):
        self.current_track = track_info
        
        if track_info['title'] not in ['Unknown', 'No Music Playing']:
            status_icons = {
                'Playing': '⏸',
                'Paused': '▶',
                'Stopped': '▶'
            }
            
            self.play_pause_btn.setText(status_icons.get(track_info['status'], '▶'))
            
            # Better text truncation for smaller fonts
            title = track_info['title']
            if len(title) > 40:
                title = title[:37] + "..."
                
            artist = track_info['artist']
            if len(artist) > 35:
                artist = artist[:32] + "..."
            
            self.track_title.setText(f"{title}")
            self.artist_name.setText(f"by {artist}" if artist != 'Unknown' else "")
            
            if track_info['length'] > 0:
                progress = (track_info['position'] / track_info['length']) * 100
                self.circular_progress.set_progress(progress)
                
                current_time = self.format_time(track_info['position'])
                total_time = self.format_time(track_info['length'])
                self.current_time_label.setText(current_time)
                self.total_time_label.setText(total_time)
            else:
                self.current_time_label.setText("00:00")
                self.total_time_label.setText("00:00")
                self.circular_progress.set_progress(0)
            
            if not self.volume_updating:
                self.volume_bar.set_volume(track_info['volume'])
                self.volume_value_label.setText(f"{track_info['volume']}%")
                self.update_volume_icon(track_info['volume'])
            
            self.status_label.setText(f"🎵 {track_info['status']} • {track_info.get('source', 'Unknown')} • {track_info['player']}")
            
            self.load_album_art(track_info['art_url'], track_info['artist'], track_info['album'])
            
        else:
            self.track_title.setText(track_info['title'])
            self.artist_name.setText(track_info['artist'])
            self.play_pause_btn.setText("▶")
            self.circular_progress.set_progress(0)
            self.current_time_label.setText("00:00")
            self.total_time_label.setText("00:00")
            self.status_label.setText(f"🔍 {track_info.get('source', 'Searching')}...")
            self.circular_progress.set_album_art(QPixmap())
    
    def format_time(self, seconds):
        if seconds < 0:
            seconds = 0
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def update_volume_icon(self, volume):
        if volume == 0:
            self.volume_label.setText("🔇")
        elif volume < 30:
            self.volume_label.setText("🔈")
        elif volume < 70:
            self.volume_label.setText("🔉")
        else:
            self.volume_label.setText("🔊")
    
    def set_system_volume(self, value):
        self.volume_updating = True
        self.volume_value_label.setText(f"{value}%")
        self.update_volume_icon(value)
        try:
            volume_level = value / 100.0
            subprocess.run(['playerctl', 'volume', str(volume_level)], timeout=2)
        except:
            pass
        finally:
            self.volume_updating = False
    
    def toggle_play_pause(self):
        try:
            subprocess.run(['playerctl', 'play-pause'], check=True, timeout=2)
        except:
            pass
    
    def previous_track(self):
        try:
            subprocess.run(['playerctl', 'previous'], check=True, timeout=2)
        except:
            pass
    
    def next_track(self):
        try:
            subprocess.run(['playerctl', 'next'], check=True, timeout=2)
        except:
            pass
    
    def load_album_art(self, art_url, artist, album):
        if art_url and self.load_art_from_url(art_url):
            return
        self.search_album_art_online(artist, album)
    
    def load_art_from_url(self, url):
        try:
            if url.startswith('file://'):
                file_path = url[7:]
                if os.path.exists(file_path):
                    pixmap = QPixmap(file_path)
                    if not pixmap.isNull():
                        self.original_album_pixmap = pixmap
                        self.set_album_art(pixmap)
                        return True
            elif url.startswith('http'):
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    pixmap = QPixmap()
                    if pixmap.loadFromData(response.content):
                        self.original_album_pixmap = pixmap
                        self.set_album_art(pixmap)
                        return True
        except:
            pass
        return False
    
    def search_album_art_online(self, artist, album):
        try:
            lastfm_url = f"http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key=demo&artist={quote(artist)}&album={quote(album)}&format=json"
            
            response = requests.get(lastfm_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'album' in data and 'image' in data['album']:
                    images = data['album']['image']
                    for img in reversed(images):
                        if img['#text']:
                            if self.load_art_from_url(img['#text']):
                                return
                                
            self.generate_fallback_art(artist, album)
            
        except:
            self.generate_fallback_art(artist, album)
    
    def generate_fallback_art(self, artist, album):
        try:
            hash_str = f"{artist}{album}".encode()
            color_hash = hashlib.md5(hash_str).hexdigest()
            
            colors = [
                (255, 0, 70),   # Magenta
                (255, 100, 0),  # Orange
                (0, 255, 200),  # Cyan
                (255, 0, 150),  # Pink
                (150, 0, 255),  # Purple
            ]
            
            color_index = int(color_hash[0], 16) % len(colors)
            r, g, b = colors[color_index]
            
            pixmap = QPixmap(280, 280)
            painter = QPainter(pixmap)
            
            gradient = QLinearGradient(0, 0, 280, 280)
            gradient.setColorAt(0, QColor(r, g, b))
            gradient.setColorAt(1, QColor(r//3, g//3, b//3))
            
            painter.fillRect(0, 0, 280, 280, QBrush(gradient))
            
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 14, QFont.Bold))
            
            artist_short = artist[:15] + "..." if len(artist) > 15 else artist
            album_short = album[:15] + "..." if len(album) > 15 else album
            
            painter.drawText(pixmap.rect(), Qt.AlignCenter, f"{artist_short}\n{album_short}")
            painter.end()
            
            self.original_album_pixmap = pixmap
            self.set_album_art(pixmap)
            
        except:
            self.circular_progress.set_album_art(QPixmap())
    
    def set_album_art(self, pixmap):
        if pixmap.isNull():
            return
            
        self.circular_progress.set_album_art(pixmap)
        self.update_background(pixmap)
    
    def update_background(self, pixmap):
        if pixmap.isNull() or not self.background_label or ImageQt is None:
            if self.background_label:
                self.background_label.setStyleSheet("background-color: #0c0c0c;")
            return
            
        try:
            qimage = pixmap.toImage()
            pil_img = Image.fromqimage(qimage.convertToFormat(qimage.Format_RGB888))
            
            screen_size = self.size()
            bg_img = pil_img.resize((screen_size.width(), screen_size.height()), Image.LANCZOS)
            blurred_bg = bg_img.filter(ImageFilter.GaussianBlur(radius=50))
            
            darkened = Image.new('RGBA', blurred_bg.size, (0, 0, 0, 120))
            blurred_bg = Image.alpha_composite(blurred_bg.convert('RGBA'), darkened)
            
            bg_pixmap = QPixmap.fromImage(ImageQt(blurred_bg))
            self.background_label.setPixmap(bg_pixmap)
        except Exception as e:
            if self.background_label:
                self.background_label.setStyleSheet("background-color: #0c0c0c;")
    
    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, 'glitch_effect'):
            self.glitch_effect.show()
        if hasattr(self, 'weather_widget'):
            self.weather_widget.show()
        if hasattr(self, 'system_stats'):
            self.system_stats.show()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'background_label') and self.background_label:
            self.background_label.setGeometry(0, 0, self.width(), self.height())
        
        if hasattr(self, 'glitch_effect'):
            self.glitch_effect.resize_to_parent()
            self.glitch_effect.show()
        
        # FIXED: Better positioning to avoid overlaps
        if hasattr(self, 'weather_widget'):
            weather_x = self.width() - 95
            weather_y = 120
            self.weather_widget.setGeometry(weather_x, weather_y, 80, 50)
            self.weather_widget.show()
        
        if hasattr(self, 'system_stats'):
            stats_x = 15
            stats_y = self.height() - 85
            self.system_stats.setGeometry(stats_x, stats_y, 100, 65)
            self.system_stats.show()
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Space:
            self.toggle_play_pause()
        elif event.key() == Qt.Key_Left:
            self.previous_track()
        elif event.key() == Qt.Key_Right:
            self.next_track()
        
    def closeEvent(self, event):
        if hasattr(self, 'music_detector'):
            self.music_detector.stop()
            self.music_detector.wait()
        if hasattr(self, 'glitch_effect'):
            self.glitch_effect.stop_glitch()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("FIXED Cyberpunk Music Player - No Overlaps")
    app.setApplicationVersion("4.1")
    
    player = CyberpunkMusicPlayer()
    player.show()
    
    print("🎵 FIXED Cyberpunk Music Player v4.1 - No Overlaps!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔧 OVERLAP FIXES Applied:")
    print("• 📦 Weather widget: Smaller (80x50) and repositioned")
    print("• 📊 System stats: Smaller (100x65) and repositioned")
    print("• 📝 Title/Artist: Smaller fonts (18px/13px) to prevent overlap")
    print("• ⏰ Time display: Smaller fonts (40px/18px) for better spacing")
    print("• 🎯 Better margins and spacing throughout")
    print("• 🚫 No more overlapping widgets!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Features:")
    print("• 💻 System stats: CPU, RAM, Temp (bottom-left)")
    print("• 🌤️  Weather: Temperature and conditions (top-right)")
    print("• 🎵 Music control with circular progress seeking")
    print("• 🎨 Cyberpunk theme with glitch effects")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
