class VampScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = FloatLayout()

        # Boneco Flutuante do V.L.A.D.
        self.vampire = Button(
            text="V.L.A.D.", size_hint=(None, None), size=(120, 120),
            pos=(100, 600), font_size=16, halign="center",
            background_normal='', background_color=(0.4, 0, 0, 1), color=(1, 1, 1, 1)
        )
        self.main_layout.add_widget(self.vampire)

        self.vel_x = 4
        self.vel_y = 3
        Clock.schedule_interval(self.mover_vampiro, 1/60.0)

        # Painel Inferior de Controles
        self.painel = BoxLayout(
            orientation='vertical', padding=12, spacing=6,
            size_hint=(1, 0.46), pos_hint={'x': 0, 'y': 0}
        )
        
        self.label = Label(text="Aguardando Comando...", size_hint=(1, 0.25), font_size=15, halign="center")
        self.input = TextInput(hint_text="Invoque o V.L.A.D...", size_hint=(1, 0.2), multiline=False)
        self.input.bind(focus=self.ajustar_por_foco)
        
        # Linha de botões principais
        linha_botoes = BoxLayout(orientation='horizontal', size_hint=(1, 0.28), spacing=5)
        btn_exec = Button(text="CONJURAR", background_color=(0.3, 0, 0, 1))
        btn_exec.bind(on_press=self.executar)
        
        # CORREÇÃO: Removido o caractere especial que quebrava o layout do Android
        btn_mic = Button(text="ESCUTAR")
        btn_mic.bind(on_press=self.ouvir)
        
        linha_botoes.add_widget(btn_exec)
        linha_botoes.add_widget(btn_mic)
        
        # Botão de Visão Computacional
        # CORREÇÃO: Texto limpo e sem símbolos incompatíveis
        btn_visao = Button(text="VER E DESCREVER IMAGEM", size_hint=(1, 0.27), background_color=(0.2, 0.2, 0.3, 1))
        btn_visao.bind(on_press=self.abrir_seletor_arquivos)

        self.painel.add_widget(self.label)
        self.painel.add_widget(self.input)
        self.painel.add_widget(linha_botoes)
        self.painel.add_widget(btn_visao)
        
        self.main_layout.add_widget(self.painel)
        self.add_widget(self.main_layout)

    def ajustar_por_foco(self, instance, value):
        if value:
            self.painel.pos_hint = {'x': 0, 'y': 0.48}
        else:
            self.painel.pos_hint = {'x': 0, 'y': 0}

    def mover_vampiro(self, dt):
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

