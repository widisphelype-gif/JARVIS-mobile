# ==========================================================
# CONFIGURAÇÕES PARA COMPILAÇÃO (BUILDOZER.SPEC):
# android.permissions = INTERNET, RECORD_AUDIO, QUERY_ALL_PACKAGES, MODIFY_AUDIO_SETTINGS
# requirements = python3, kivy, plyer, PyAudio, SpeechRecognition, pyjnius
# android.api = 33
# android.entrypoint = org.kivy.android.PythonActivity
# ==========================================================

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import platform

import datetime
import random
import speech_recognition as sr
from plyer import tts

# Configurações de Integração Android
if platform == 'android':
    from jnius import autoclass, cast
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    PackageManager = autoclass('android.content.pm.PackageManager')

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        titulo = Label(
            text="MATRIZ DE DADOS STARK", 
            font_size=28, 
            color=(0, 0.9, 1, 1),
            size_hint=(1, 0.4)
        )
        
        btn_acordar = Button(
            text="EXECUTAR", 
            font_size=18,
            halign="center",
            background_color=(0, 0.4, 0.8, 1),
            size_hint=(1, 0.3)
        )
        btn_acordar.bind(on_press=self.ativar_jarvis)
        
        layout.add_widget(titulo)
        layout.add_widget(btn_acordar)
        self.add_widget(layout)

    def ativar_jarvis(self, instance):
        frase = "Sistemas carregados. Estou online, senhor."
        tts.speak(frase)
        self.manager.current = 'main'

class JarvisScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        self.label = Label(
            text="Aguardando Protocolo J.A.R.V.I.S.", 
            font_size=20, 
            color=(0, 0.9, 1, 1),
            size_hint=(1, 0.2)
        )
        
        self.input = TextInput(
            hint_text="Digite: [comando]", 
            size_hint=(1, 0.2), 
            multiline=False,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(1, 1, 1, 1),
            font_size=18
        )
        
        self.btn_executar = Button(
            text="PROCESSAR", 
            size_hint=(1, 0.15), 
            background_color=(0, 0.6, 0.4, 1)
        )
        self.btn_executar.bind(on_press=self.executar)

        self.mic = Button(
            text="🎤 ESCUTA ATIVA", 
            size_hint=(1, 0.15),
            background_color=(0.2, 0.2, 0.2, 1)
        )
        self.mic.bind(on_press=self.ouvir_microfone)

        layout.add_widget(self.label)
        layout.add_widget(self.input)
        layout.add_widget(self.btn_executar)
        layout.add_widget(self.mic)
        self.add_widget(layout)

    def falar(self, texto):
        self.label.text = texto
        fala_limpa = texto.replace("J.A.R.V.I.S.:", "").strip()
        tts.speak(fala_limpa)

    def abrir_app_android(self, nome_app):
        if platform != 'android':
            return "J.A.R.V.I.S.: Erro de hardware. Protocolo de apps restrito ao mobile."
        try:
            current_activity = PythonActivity.mActivity
            context = cast('android.content.Context', current_activity)
            pm = context.getPackageManager()
            packages = pm.getInstalledApplications(PackageManager.GET_META_DATA)
            
            for i in range(packages.size()):
                app = packages.get(i)
                label = str(pm.getApplicationLabel(app)).lower()
                if nome_app in label:
                    intent = pm.getLaunchIntentForPackage(app.packageName)
                    if intent:
                        context.startActivity(intent)
                        return f"J.A.R.V.I.S.: Executando {label}. Algo mais, senhor?"
            return f"J.A.R.V.I.S.: Não encontrei o aplicativo {nome_app} no banco de dados."
        except:
            return "J.A.R.V.I.S.: Erro crítico na varredura de pacotes."

    def processar_ia(self, prompt):
        prompt = prompt.upper()
        if not prompt.startswith("J.A.R.V.I.S"):
            return "SISTEMA: Erro de protocolo. Identifique-me pelo nome para que eu possa responder."

        comando = prompt.replace("J.A.R.V.I.S", "").strip().lower()

        if "quem é você" in comando:
            return "J.A.R.V.I.S.: Sou o Just A Rather Very Intelligent System. Sua interface pessoal."
        elif "abrir" in comando:
            app_nome = comando.replace("abrir", "").strip()
            return self.abrir_app_android(app_nome)
        elif "hora" in comando:
            agora = datetime.datetime.now().strftime('%H:%M')
            return f"J.A.R.V.I.S.: São {agora}, senhor."
        return "J.A.R.V.I.S.: Comando processado. Aguardando novas instruções."

    def ouvir_microfone(self, instance):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.label.text = "J.A.R.V.I.S.: Sensores auditivos ativos..."
            try:
                audio = r.listen(source, timeout=5)
                texto = r.recognize_google(audio, language="pt-BR")
                self.input.text = f"J.A.R.V.I.S. {texto}"
                self.executar(None)
            except:
                self.falar("J.A.R.V.I.S.: A conexão de áudio falhou.")

    def executar(self, instance):
        prompt = self.input.text
        if not prompt: return
        resposta = self.processar_ia(prompt)
        self.falar(resposta)
        self.input.text = ""

class JarvisApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(JarvisScreen(name='main'))
        return sm

if __name__ == "__main__":
    JarvisApp().run()
