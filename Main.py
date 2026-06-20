import threading
import random
import json
import os
import time

# Tentativa de importação segura de bibliotecas padrão do Python
# (Não causam crash imediato na maioria dos Androids)
try:
    import base64
except ImportError:
    pass

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock

# =====================================================================
# CONFIGURAÇÃO DA CHAVE API DO GEMINI (MANTIDA)
# =====================================================================
GEMINI_API_KEY = "AIzaSyBS4mnay1koyq9HoXIvj4hYyKIRx7U_Ie8"

Window.clearcolor = (0.02, 0.01, 0.01, 1) # Preto Carmesim


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=30)
        
        titulo = Label(text="V.L.A.D. AI\n[ Mente Pura e Estável ]", font_size=26, 
                       color=(0.8, 0, 0, 1), halign="center")
        
        btn = Button(text="DESPERTAR ENTIDADE", font_size=20,
                     background_normal='', background_color=(0.35, 0, 0, 1),
                     color=(1, 1, 1, 1), size_hint=(1, 0.3))
                     
        btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(titulo)
        layout.add_widget(btn)
        self.add_widget(layout)


class VampScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = FloatLayout()

        # 🦇 MASCOTE ANIMADO
        self.vampire = Button(
            text="🦇\nV.L.A.D.", size_hint=(None, None), size=(110, 110),
            pos=(100, 700), font_size=16, halign="center",
            background_normal='', background_color=(0.35, 0, 0, 1), color=(1, 1, 1, 1)
        )
        self.main_layout.add_widget(self.vampire)

        self.vel_x = 3.5
        self.vel_y = 2.5
        Clock.schedule_interval(self.mover_vampiro, 1/60.0)

        # 🎛️ PAINEL PRINCIPAL DE CONTROLE
        self.painel = BoxLayout(
            orientation='vertical', padding=10, spacing=8,
            size_hint=(1, 0.55), pos_hint={'x': 0, 'y': 0}
        )
        
        # 📜 HISTÓRICO DE CHAT ROLÁVEL
        self.scroll = ScrollView(size_hint=(1, 0.6))
        self.chat_logs = Label(
            text="[color=880000]V.L.A.D.:[/color]\nEstou acordado. Aguardando ordens espirituais em texto...\n",
            markup=True, font_size=15, halign="left", valign="top",
            size_hint_y=None, color=(0.9, 0.9, 0.9, 1)
        )
        self.chat_logs.bind(size=self.atualizar_tamanho_chat)
        self.scroll.add_widget(self.chat_logs)
        
        # Entrada de Texto
        self.input = TextInput(hint_text="Envie um comando textual...", size_hint=(1, 0.18), 
                               multiline=False, background_color=(0.08, 0.03, 0.03, 1),
                               foreground_color=(1, 1, 1, 1), cursor_color=(1, 0.2, 0.2, 1))
        # Ajusta o layout quando o teclado abre
        self.input.bind(focus=self.ajustar_por_foco)
        
        # Botão Supremo de Conjuração
        btn_exec = Button(text="ENVIAR CONJURAÇÃO (IA REAL)", size_hint=(1, 0.22),
                          background_normal='', background_color=(0.35, 0, 0, 1),
                          color=(1, 1, 1, 1), font_size=18)
        btn_exec.bind(on_press=self.conjurar_mente)

        self.painel.add_widget(self.scroll)
        self.painel.add_widget(self.input)
        self.painel.add_widget(btn_exec)
        
        self.main_layout.add_widget(self.painel)
        self.add_widget(self.main_layout)

    def atualizar_tamanho_chat(self, instance, value):
        try:
            self.chat_logs.text_size = (self.chat_logs.width - 20, None)
            self.chat_logs.height = max(self.chat_logs.texture_size[1], self.scroll.height)
        except:
            pass

    def adicionar_mensagem(self, emissor, texto):
        try:
            if emissor == "user":
                formatted = f"[color=777777]Você:[/color] {texto}\n"
            elif emissor == "erro":
                formatted = f"[color=ff0000]⚠️ ERRO CRÍTICO:[/color] {texto}\n"
            else:
                formatted = f"[color=ff2222]V.L.A.D.:[/color] {texto}\n"
            
            self.chat_logs.text += formatted
            # Rola automaticamente para o fim do chat
            Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)
        except:
            pass

    def ajustar_por_foco(self, instance, value):
        try:
            if value: self.painel.pos_hint = {'x': 0, 'y': 0.45}
            else: self.painel.pos_hint = {'x': 0, 'y': 0}
        except:
            pass

    def mover_vampiro(self, dt):
        try:
            self.vampire.x += self.vel_x
            self.vampire.y += self.vel_y
            if self.vampire.x <= 0 or self.vampire.right >= Window.width:
                self.vel_x *= -1
            if self.vampire.top >= Window.height:
                self.vel_y *= -1
            
            limite_inferior = self.painel.y + self.painel.height
            if self.vampire.y <= limite_inferior:
                self.vampire.y = limite_inferior
                self.vel_y *= -1
        except:
            pass

    def conjurar_mente(self, instance):
        texto = self.input.text.strip()
        if texto:
            self.adicionar_mensagem("user", texto)
            self.adicionar_mensagem("vampiro", "...Conectando à névoa... (Aguarde)")
            
            self.input.text = ""
            self.input.focus = False
            
            # 🚀 THREADING: Executa em segundo plano sem travar o app!
            threading.Thread(target=self.thread_gemini_text_blindada, args=(texto,)).start()

    # =====================================================================
    # MOTOR DE CONEXÃO ASSÍNCRONA BLINDADO CONTRA FECHAMENTOS (CRASHES)
    # =====================================================================
    def thread_gemini_text_blindada(self, prompt):
        # 1. TENTATIVA DE IMPORTAÇÃO SEGURA DE 'REQUESTS'
        # Se falhar aqui, o app NÃO fecha, apenas avisa no chat.
        try:
            import requests
        except ImportError:
            time.sleep(1) # Espera um pouco para o usuário ler o "Conectando..."
            Clock.schedule_once(lambda dt: self.substituir_ultima_mensagem("Bibliotecas em falta.", "erro"), 0)
            Clock.schedule_once(lambda dt: self.adicionar_mensagem("erro", "Vá ao menu PIP do Pydroid 3 e instale: 'requests'"), 0.2)
            return

        # 2. TENTATIVA DE CONEXÃO E ENVIO À IA
        # Se der erro de internet, tempo ou chave, o app CONTINUA vivo.
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            headers = {"Content-Type": "application/json"}
            
            # Prompt do sistema integrado na mente da IA
            payload = {
                "contents": [{"parts":[{"text": f"Instrução do Sistema: Responda brevemente e aja como um assistente místico e sombrio chamado V.L.A.D. Não use marcas de negrito asteriscos. Usuário perguntou: {prompt}"}]}]
            }
            
            # Faz o envio com limite de tempo estrito para evitar travamentos
            resposta = requests.post(url, headers=headers, json=payload, timeout=20)
            
            if resposta.status_code == 200:
                dados = resposta.json()
                if 'candidates' in dados and dados['candidates']:
                    # Limpeza clássica de Markdown
                    cleaned_text = dados['candidates'][0]['content']['parts'][0]['text'].strip().replace('*', '')
                    Clock.schedule_once(lambda dt: self.substituir_ultima_mensagem(cleaned_text, "vampiro"), 0)
                else:
                    Clock.schedule_once(lambda dt: self.substituir_ultima_mensagem("Visão confusa, tente conjurar novamente.", "vampiro"), 0)
            else:
                Clock.schedule_once(lambda dt: self.substituir_ultima_mensagem(f"Falha na névoa (Erro HTTP {resposta.status_code}).", "erro"), 0)
                
        except Exception as e:
            # Captura QUALQUER erro de internet/timeout e avisa no chat pacientemente
            Clock.schedule_once(lambda dt: self.substituir_ultima_mensagem(f"A conexão espiritual falhou: {str(e)}", "erro"), 0)

    def substituir_ultima_mensagem(self, texto, emissor):
        # Remove o aviso de "Aguarde" da interface com segurança
        try:
            linhas = self.chat_logs.text.split('\n')
            if len(linhas) > 1 and "...Conectando à névoa..." in linhas[-2]:
                self.chat_logs.text = '\n'.join(linhas[:-2]) + '\n'
            
            self.adicionar_mensagem(emissor, texto)
        except:
            pass


class VladApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(VampScreen(name='main'))
        return sm

if __name__ == "__main__":
    # Garante que erros no Kivy não fechem o app imediatamente em alguns Androids
    try:
        VladApp().run()
    except Exception as e:
        print(f"Erro fatal evitado: {str(e)}")
import threading
import random
import json
import os
import time

# Tentativa de importação segura de bibliotecas padrão do Python
# (Não causam crash imediato na maioria dos Androids)
try:
    import base64
except ImportError:
    pass

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock

# =====================================================================
# CONFIGURAÇÃO DA CHAVE API DO GEMINI (MANTIDA)
# =====================================================================
GEMINI_API_KEY = "AIzaSyBS4mnay1koyq9HoXIvj4hYyKIRx7U_Ie8"

Window.clearcolor = (0.02, 0.01, 0.01, 1) # Preto Carmesim


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=30)
        
        titulo = Label(text="V.L.A.D. AI\n[ Mente Pura e Estável ]", font_size=26, 
                       color=(0.8, 0, 0, 1), halign="center")
        
        btn = Button(text="DESPERTAR ENTIDADE", font_size=20,
                     background_normal='', background_color=(0.35, 0, 0, 1),
                     color=(1, 1, 1, 1), size_hint=(1, 0.3))
                     
        btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(titulo)
        layout.add_widget(btn)
        self.add_widget(layout)


class VampScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = FloatLayout()

        # 🦇 MASCOTE ANIMADO
        self.vampire = Button(
            text="🦇\nV.L.A.D.", size_hint=(None, None), size=(110, 110),
            pos=(100, 700), font_size=16, halign="center",
            background_normal='', background_color=(0.35, 0, 0, 1), color=(1, 1, 1, 1)
        )
        self.main_layout.add_widget(self.vampire)

        self.vel_x = 3.5
        self.vel_y = 2.5
        Clock.schedule_interval(self.mover_vampiro, 1/60.0)

        # 🎛️ PAINEL PRINCIPAL DE CONTROLE
        self.painel = BoxLayout(
            orientation='vertical', padding=10, spacing=8,
            size_hint=(1, 0.55), pos_hint={'x': 0, 'y': 0}
        )
        
        # 📜 HISTÓRICO DE CHAT ROLÁVEL
        self.scroll = ScrollView(size_hint=(1, 0.6))
        self.chat_logs = Label(
            text="[color=880000]V.L.A.D.:[/color]\nEstou acordado. Aguardando ordens espirituais em texto...\n",
            markup=True, font_size=15, halign="left", valign="top",
            size_hint_y=None, color=(0.9, 0.9, 0.9, 1)
        )
        self.chat_logs.bind(size=self.atualizar_tamanho_chat)
        self.scroll.add_widget(self.chat_logs)
        
        # Entrada de Texto
        self.input = TextInput(hint_text="Envie um comando textual...", size_hint=(1, 0.18), 
                               multiline=False, background_color=(0.08, 0.03, 0.03, 1),
                               foreground_color=(1, 1, 1, 1), cursor_color=(1, 0.2, 0.2, 1))
        # Ajusta o layout quando o teclado abre
        self.input.bind(focus=self.ajustar_por_foco)
        
        # Botão Supremo de Conjuração
        btn_exec = Button(text="ENVIAR CONJURAÇÃO (IA REAL)", size_hint=(1, 0.22),
                          background_normal='', background_color=(0.35, 0, 0, 1),
                          color=(1, 1, 1, 1), font_size=18)
        btn_exec.bind(on_press=self.conjurar_mente)

        self.painel.add_widget(self.scroll)
        self.painel.add_widget(self.input)
        self.painel.add_widget(btn_exec)
        
        self.main_layout.add_widget(self.painel)
        self.add_widget(self.main_layout)

    def atualizar_tamanho_chat(self, instance, value):
        try:
            self.chat_logs.text_size = (self.chat_logs.width - 20, None)
            self.chat_logs.height = max(self.chat_logs.texture_size[1], self.scroll.height)
        except:
            pass

    def adicionar_mensagem(self, emissor, texto):
        try:
            if emissor == "user":
                formatted = f"[color=777777]Você:[/color] {texto}\n"
            elif emissor == "erro":
                formatted = f"[color=ff0000]⚠️ ERRO CRÍTICO:[/color] {texto}\n"
            else:
                formatted = f"[color=ff2222]V.L.A.D.:[/color] {texto}\n"
            
            self.chat_logs.text += formatted
            # Rola automaticamente para o fim do chat
            Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)
        except:
            pass

    def ajustar_por_foco(self, instance, value):
        try:
            if value: self.painel.pos_hint = {'x': 0, 'y': 0.45}
            else: self.painel.pos_hint = {'x': 0, 'y': 0}
        except:
            pass

    def mover_vampiro(self, dt):
        try:
            self.vampire.x += self.vel_x
            self.vampire.y += self.vel_y
            if self.vampire.x <= 0 or self.vampire.right >= Window.width:
                self.vel_x *= -1
            if self.vampire.top >= Window.height:
                self.vel_y *= -1
            
            limite_inferior = self.painel.y + self.painel.height
            if self.vampire.y <= limite_inferior:
                self.vampire.y = limite_inferior
                self.vel_y *= -1
        except:
            pass

    def conjurar_mente(self, instance):
        texto = self.input.text.strip()
        if texto:
            self.adicionar_mensagem("user", texto)
            self.adicionar_mensagem("vampiro", "...Conectando à névoa... (Aguarde)")
            
            self.input.text = ""
            self.input.focus = False
            
            # 🚀 THREADING: Executa em segundo plano sem travar o app!
            threading.Thread(target=self.thread_gemini_text_blindada, args=(texto,)).start()

    # =====================================================================
    # MOTOR DE CONEXÃO ASSÍNCRONA BLINDADO CONTRA FECHAMENTOS (CRASHES)
    # =====================================================================
    def thread_gemini_text_blindada(self, prompt):
        # 1. TENTATIVA DE IMPORTAÇÃO SEGURA DE 'REQUESTS'
        # Se falhar aqui, o app NÃO fecha, apenas avisa no chat.
        try:
            import requests
        except ImportError:
            time.sleep(1) # Espera um pouco para o usuário ler o "Conectando..."
            Clock.schedule_once(lambda dt: self.substituir_ultima_mensagem("Bibliotecas em falta.", "erro"), 0)
            Clock.schedule_once(lambda dt: self.adicionar_mensagem("erro", "Vá ao menu PIP do Pydroid 3 e instale: 'requests'"), 0.2)
            return

        # 2. TENTATIVA DE CONEXÃO E ENVIO À IA
        # Se der erro de internet, tempo ou chave, o app CONTINUA vivo.
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            headers = {"Content-Type": "application/json"}
            
            # Prompt do sistema integrado na mente da IA
            payload = {
                "contents": [{"parts":[{"text": f"Instrução do Sistema: Responda brevemente e aja como um assistente místico e sombrio chamado V.L.A.D. Não use marcas de negrito asteriscos. Usuário perguntou: {prompt}"}]}]
            }
            
            # Faz o envio com limite de tempo estrito para evitar travamentos
            resposta = requests.post(url, headers=headers, json=payload, timeout=20)
            
            if resposta.status_code == 200:
                dados = resposta.json()
                if 'candidates' in dados and dados['candidates']:
                    # Limpeza clássica de Markdown
                    cleaned_text = dados['candidates'][0]['content']['parts'][0]['text'].strip().replace('*', '')
                    Clock.schedule_once(lambda dt: self.substituir_ultima_mensagem(cleaned_text, "vampiro"), 0)
                else:
                    Clock.schedule_once(lambda dt: self.substituir_ultima_mensagem("Visão confusa, tente conjurar novamente.", "vampiro"), 0)
            else:
                Clock.schedule_once(lambda dt: self.substituir_ultima_mensagem(f"Falha na névoa (Erro HTTP {resposta.status_code}).", "erro"), 0)
                
        except Exception as e:
            # Captura QUALQUER erro de internet/timeout e avisa no chat pacientemente
            Clock.schedule_once(lambda dt: self.substituir_ultima_mensagem(f"A conexão espiritual falhou: {str(e)}", "erro"), 0)

    def substituir_ultima_mensagem(self, texto, emissor):
        # Remove o aviso de "Aguarde" da interface com segurança
        try:
            linhas = self.chat_logs.text.split('\n')
            if len(linhas) > 1 and "...Conectando à névoa..." in linhas[-2]:
                self.chat_logs.text = '\n'.join(linhas[:-2]) + '\n'
            
            self.adicionar_mensagem(emissor, texto)
        except:
            pass


class VladApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(VampScreen(name='main'))
        return sm

if __name__ == "__main__":
    # Garante que erros no Kivy não fechem o app imediatamente em alguns Androids
    try:
        VladApp().run()
    except Exception as e:
        print(f"Erro fatal evitado: {str(e)}")

