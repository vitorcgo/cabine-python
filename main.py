"""
SISTEMA DE CABINE FOTOGRÁFICA
----------------------------
Desenvolvido em Python 3 para Windows
Interface gráfica: Kivy
Captura de imagem: OpenCV
Manipulação de imagens: Pillow (PIL)
Impressão: pywin32
"""

"""
========== INSTRUÇÕES DE INSTALAÇÃO ==========

1. INSTALAÇÃO DAS DEPENDÊNCIAS:
   Abra o Prompt de Comando como administrador e execute:
   pip install -r requirements.txt
   
   Ou instale manualmente cada pacote:
   pip install kivy==2.1.0
   pip install opencv-python==4.7.0.72
   pip install pillow==9.4.0
   pip install pywin32==305
   pip install kivy_garden.filebrowser

2. CONFIGURAÇÃO DA CÂMERA:
   - Certifique-se de que a câmera está conectada ao computador
   - Para webcam USB padrão: Conecte e Windows detectará automaticamente
   - Para câmera DSLR Canon: Instale o software EOS Utility da Canon e configure
     para modo "Live View" antes de iniciar este programa

3. CONFIGURAÇÃO DA IMPRESSORA:
   - Configure uma impressora como padrão no Windows
   - Verifique se a impressora está ligada e com papel
   - Teste a impressora padrão no Painel de Controle do Windows

4. EXECUTANDO O PROGRAMA:
   - Navegue até a pasta do programa no Prompt de Comando
   - Execute: python main.py
   - Para sair do programa: pressione ESC + Q simultaneamente

5. PERSONALIZAÇÃO:
   - Coloque molduras (PNG com transparência) na pasta "molduras"
   - Molduras recomendadas: resolução 2480x3508 pixels (A4) ou proporcionais
   - Ajuste a resolução de captura modificando a variável CAMERA_RESOLUTION
"""

# Importações necessárias
import os
import sys
import time
from datetime import datetime

# Configurações da interface gráfica Kivy
from kivy.app import App
from kivy.config import Config
# Forçar exibição em tela cheia
Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'window_state', 'maximized')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # Desativa multitouch simulado

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image as KivyImage
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics.texture import Texture

# Biblioteca de captura de vídeo
import cv2

# Biblioteca para processamento de imagem
from PIL import Image, ImageDraw, ImageFont

# Biblioteca para impressão no Windows (com tratamento para ambientes não-Windows)
try:
    import win32print
    import win32ui
    from PIL import ImageWin
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    print("[AVISO] Bibliotecas do Windows não disponíveis. A impressão não funcionará.")

# Definições globais
CAMERA_ID = 0  # ID da câmera (geralmente 0 para webcam interna, 1 para externa)
CAMERA_RESOLUTION = (1280, 720)  # Resolução da captura (ajuste conforme sua câmera)
PRINT_SIZE = (2480, 3508)  # Tamanho de impressão A4 em pixels (300 DPI)
COUNTDOWN_TIME = 3  # Tempo de contagem regressiva em segundos
PREVIEW_TIME = 5  # Tempo de exibição do preview em segundos

class PhotoBoothApp(App):
    def __init__(self, **kwargs):
        super(PhotoBoothApp, self).__init__(**kwargs)
        self.title = "Cabine Fotográfica"
        self.moldura_selecionada = None
        self.camera = None
        self.ultima_foto = None

    def build(self):
        # Registra teclas para sair (ESC + Q)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self.root)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        
        # Configuração do gerenciador de telas
        self.sm = ScreenManager()
        
        # Tela de boas-vindas
        self.welcome_screen = WelcomeScreen(name='welcome')
        self.sm.add_widget(self.welcome_screen)
        
        # Tela de seleção de moldura
        self.frame_select_screen = FrameSelectScreen(name='frame_select')
        self.sm.add_widget(self.frame_select_screen)
        
        # Tela de captura
        self.capture_screen = CaptureScreen(name='capture')
        self.sm.add_widget(self.capture_screen)
        
        # Tela de exibição da foto final
        self.preview_screen = PreviewScreen(name='preview')
        self.sm.add_widget(self.preview_screen)
        
        return self.sm

    def on_start(self):
        """Método chamado quando o aplicativo inicia"""
        print("[INFO] Iniciando aplicativo...")
        
        # Verifica se a pasta de molduras existe
        if not os.path.exists('molduras'):
            os.makedirs('molduras')
            print("[INFO] Pasta 'molduras' criada. Adicione os arquivos PNG das molduras.")
        
        # Verifica se existem molduras na pasta
        molduras = [f for f in os.listdir('molduras') if f.lower().endswith('.png')]
        if not molduras:
            print("[AVISO] Não foram encontradas molduras na pasta 'molduras'.")
            print("[AVISO] Adicione arquivos PNG com transparência e reinicie o aplicativo.")

    def on_stop(self):
        """Método chamado quando o aplicativo é encerrado"""
        print("[INFO] Encerrando aplicativo...")
        # Libera a câmera se estiver aberta
        if hasattr(self, 'camera') and self.camera is not None:
            self.camera.release()
            print("[INFO] Câmera liberada.")

    def carregar_molduras(self):
        """Carrega as molduras disponíveis na pasta 'molduras'"""
        molduras = []
        try:
            for arquivo in os.listdir('molduras'):
                if arquivo.lower().endswith('.png'):
                    caminho_completo = os.path.join('molduras', arquivo)
                    molduras.append(caminho_completo)
        except Exception as e:
            print(f"[ERRO] Falha ao carregar molduras: {e}")
        
        return molduras

    def selecionar_moldura(self, moldura_path):
        """Seleciona a moldura e avança para a tela de captura"""
        self.moldura_selecionada = moldura_path
        print(f"[INFO] Moldura selecionada: {moldura_path}")
        
        # Configura a tela de captura
        self.capture_screen.setup_camera()
        
        # Muda para a tela de captura
        self.sm.current = 'capture'

    def tirar_foto(self):
        """Inicia o processo de contagem regressiva e captura"""
        self.capture_screen.iniciar_contagem()

    def processar_e_mostrar_foto(self, frame):
        """Processa a foto capturada aplicando a moldura selecionada"""
        if self.moldura_selecionada is None:
            print("[ERRO] Nenhuma moldura selecionada")
            return
        
        try:
            # Converte o frame do OpenCV para o formato PIL
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_capturada = Image.fromarray(frame_rgb)
            
            # Carrega a moldura selecionada
            moldura = Image.open(self.moldura_selecionada).convert("RGBA")
            
            # Redimensiona a imagem capturada para o tamanho da moldura
            # mantendo a proporção e centralizando
            img_width, img_height = img_capturada.size
            moldura_width, moldura_height = moldura.size
            
            # Calcula a nova resolução mantendo proporção
            ratio = min(moldura_width/img_width, moldura_height/img_height)
            new_size = (int(img_width * ratio), int(img_height * ratio))
            img_redimensionada = img_capturada.resize(new_size, Image.Resampling.LANCZOS)
            
            # Cria uma nova imagem para receber a foto e a moldura
            foto_final = Image.new("RGBA", (moldura_width, moldura_height), (255, 255, 255, 0))
            
            # Centraliza a imagem capturada
            offset_x = (moldura_width - new_size[0]) // 2
            offset_y = (moldura_height - new_size[1]) // 2
            foto_final.paste(img_redimensionada, (offset_x, offset_y))
            
            # Aplica a moldura por cima da imagem capturada
            foto_final = Image.alpha_composite(foto_final, moldura)
            
            # Converte para RGB para salvar/imprimir
            foto_final_rgb = foto_final.convert("RGB")
            
            # Atualiza a referência para a última foto
            self.ultima_foto = foto_final_rgb
            
            # Exibe a foto na tela de preview
            self.preview_screen.mostrar_foto(foto_final_rgb)
            self.sm.current = 'preview'
            
            # Agenda a impressão para depois de um tempo
            Clock.schedule_once(lambda dt: self.imprimir_foto(), PREVIEW_TIME)
            
        except Exception as e:
            print(f"[ERRO] Falha ao processar a foto: {e}")

    def imprimir_foto(self):
        """Imprime a foto usando a impressora padrão do Windows"""
        if self.ultima_foto is None:
            print("[ERRO] Nenhuma foto para imprimir")
            return
        
        try:
            # Redimensiona a imagem para o tamanho de impressão
            foto_para_impressao = self.ultima_foto.copy()
            foto_para_impressao = foto_para_impressao.resize(PRINT_SIZE, Image.Resampling.LANCZOS)
            
            if WINDOWS_AVAILABLE:
                # Obtém o nome da impressora padrão
                impressora_padrao = win32print.GetDefaultPrinter()
                print(f"[INFO] Imprimindo na impressora padrão: {impressora_padrao}")
                
                # Configura o DC da impressora
                hDC = win32ui.CreateDC()
                hDC.CreatePrinterDC(impressora_padrao)
                hDC.StartDoc("Cabine Fotográfica")
                hDC.StartPage()
                
                # Imprime a imagem
                dib = ImageWin.Dib(foto_para_impressao)
                dib.draw(hDC.GetHandleOutput(), (0, 0, PRINT_SIZE[0], PRINT_SIZE[1]))
                
                hDC.EndPage()
                hDC.EndDoc()
                hDC.DeleteDC()
                
                print("[INFO] Foto enviada para impressão com sucesso!")
            else:
                print("[AVISO] Impressão não disponível - ambiente não-Windows detectado")
                # Em um ambiente não-Windows, podemos salvar a imagem como alternativa
                self.salvar_foto()
            
            # Opcional: Salvar a imagem (sempre, independente do ambiente)
            # self.salvar_foto()
            
            # Retorna à tela inicial após impressão/visualização
            Clock.schedule_once(lambda dt: self.voltar_inicio(), 2)
            
        except Exception as e:
            print(f"[ERRO] Falha ao imprimir/processar: {e}")
            # Em caso de erro, também volta para a tela inicial
            Clock.schedule_once(lambda dt: self.voltar_inicio(), 2)
    
    def salvar_foto(self):
        """Função para salvar a foto (opcional, não é usada por padrão)"""
        if self.ultima_foto is None:
            return
        
        try:
            # Cria pasta 'fotos' se não existir
            if not os.path.exists('fotos'):
                os.makedirs('fotos')
                
            # Gera nome de arquivo baseado na data e hora
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fotos/foto_{timestamp}.jpg"
            
            # Salva a imagem
            self.ultima_foto.save(filename, "JPEG", quality=95)
            print(f"[INFO] Foto salva em: {filename}")
            
        except Exception as e:
            print(f"[ERRO] Falha ao salvar a foto: {e}")

    def voltar_inicio(self):
        """Retorna à tela inicial (boas-vindas)"""
        self.sm.current = 'welcome'

    def _keyboard_closed(self):
        """Chamado quando o teclado é fechado"""
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """Gerencia pressionamentos de tecla"""
        # Combinação de tecla ESC (27) + Q (113) para sair
        if keycode[0] == 27 and 'q' in modifiers:
            self.stop()
        return True


class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super(WelcomeScreen, self).__init__(**kwargs)
        
        # Layout principal
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        # Área superior para título
        top_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.4))
        
        # Título principal
        titulo = Label(
            text="CABINE FOTOGRÁFICA",
            font_size='60sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, 0.7)
        )
        top_layout.add_widget(titulo)
        
        # Subtítulo
        subtitulo = Label(
            text="Escolha uma moldura e crie sua foto",
            font_size='30sp',
            color=(0.9, 0.9, 0.9, 1),
            size_hint=(1, 0.3)
        )
        top_layout.add_widget(subtitulo)
        layout.add_widget(top_layout)
        
        # Botão para iniciar
        btn_iniciar = Button(
            text="INICIAR",
            font_size='40sp',
            size_hint=(0.5, 0.4),
            pos_hint={'center_x': 0.5},
            background_color=(0.2, 0.7, 0.3, 1)
        )
        btn_iniciar.bind(on_release=self.go_to_frame_select)
        layout.add_widget(btn_iniciar)
        
        # Rodapé com instruções
        instrucao = Label(
            text="Toque para começar",
            font_size='24sp',
            color=(0.8, 0.8, 0.8, 1),
            size_hint=(1, 0.2)
        )
        layout.add_widget(instrucao)
        
        self.add_widget(layout)

    def go_to_frame_select(self, instance):
        """Navega para a tela de seleção de molduras"""
        app = App.get_running_app()
        app.frame_select_screen.carregar_lista_molduras()
        app.sm.current = 'frame_select'


class FrameSelectScreen(Screen):
    def __init__(self, **kwargs):
        super(FrameSelectScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Título da tela
        self.titulo = Label(
            text="SELECIONE UMA MOLDURA",
            font_size='40sp',
            bold=True,
            size_hint=(1, 0.15)
        )
        self.layout.add_widget(self.titulo)
        
        # Área de molduras com scroll
        self.scroll_view = ScrollView(size_hint=(1, 0.75))
        self.molduras_grid = GridLayout(cols=3, spacing=20, size_hint_y=None, padding=20)
        # É necessário definir a altura do grid para o scroll funcionar
        self.molduras_grid.bind(minimum_height=self.molduras_grid.setter('height'))
        
        self.scroll_view.add_widget(self.molduras_grid)
        self.layout.add_widget(self.scroll_view)
        
        # Botão para voltar à tela inicial
        self.btn_voltar = Button(
            text="VOLTAR",
            font_size='30sp',
            size_hint=(0.3, 0.1),
            pos_hint={'center_x': 0.5},
            background_color=(0.7, 0.2, 0.2, 1)
        )
        self.btn_voltar.bind(on_release=self.voltar_inicio)
        self.layout.add_widget(self.btn_voltar)
        
        self.add_widget(self.layout)

    def carregar_lista_molduras(self):
        """Carrega e exibe as molduras disponíveis"""
        # Limpa a grade existente
        self.molduras_grid.clear_widgets()
        
        # Carrega as molduras da pasta
        app = App.get_running_app()
        molduras = app.carregar_molduras()
        
        if not molduras:
            # Se não encontrar molduras, exibe mensagem
            lbl_sem_molduras = Label(
                text="Nenhuma moldura encontrada.\nAdicione arquivos PNG na pasta 'molduras'.",
                font_size='30sp',
                size_hint_y=None,
                height=200
            )
            self.molduras_grid.add_widget(lbl_sem_molduras)
        else:
            # Exibe as molduras encontradas
            for moldura_path in molduras:
                # Container para a moldura
                box = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=300,
                    spacing=10
                )
                
                # Imagem da moldura
                img = KivyImage(source=moldura_path, allow_stretch=True, keep_ratio=True)
                
                # Botão para selecionar a moldura
                btn = Button(
                    text="SELECIONAR",
                    font_size='20sp',
                    size_hint_y=0.2,
                    background_color=(0.2, 0.6, 0.8, 1)
                )
                # Salva o caminho da moldura como propriedade do botão
                btn.moldura_path = moldura_path
                btn.bind(on_release=self.selecionar_moldura)
                
                # Adiciona imagem e botão ao container
                box.add_widget(img)
                box.add_widget(btn)
                
                # Adiciona o container à grade
                self.molduras_grid.add_widget(box)

    def selecionar_moldura(self, instance):
        """Callback para quando uma moldura é selecionada"""
        app = App.get_running_app()
        app.selecionar_moldura(instance.moldura_path)

    def voltar_inicio(self, instance):
        """Retorna para a tela inicial"""
        app = App.get_running_app()
        app.sm.current = 'welcome'


class CaptureScreen(Screen):
    def __init__(self, **kwargs):
        super(CaptureScreen, self).__init__(**kwargs)
        self.camera = None
        self.contagem_ativa = False
        self.countdown_value = COUNTDOWN_TIME
        
        # Layout principal
        self.layout = FloatLayout()
        
        # Widget para exibir o feed da câmera
        self.camera_widget = KivyImage(allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.camera_widget)
        
        # Botão para tirar foto
        self.btn_tirar_foto = Button(
            text="TIRAR FOTO",
            font_size='40sp',
            size_hint=(0.5, 0.15),
            pos_hint={'center_x': 0.5, 'y': 0.05},
            background_color=(0.2, 0.7, 0.3, 1)
        )
        self.btn_tirar_foto.bind(on_release=self.on_tirar_foto)
        self.layout.add_widget(self.btn_tirar_foto)
        
        # Label para a contagem regressiva (inicialmente invisível)
        self.lbl_contagem = Label(
            text="",
            font_size='150sp',
            bold=True,
            color=(1, 0.4, 0.4, 1),
            opacity=0
        )
        self.layout.add_widget(self.lbl_contagem)
        
        # Botão para voltar à seleção de molduras
        self.btn_voltar = Button(
            text="VOLTAR",
            font_size='25sp',
            size_hint=(0.2, 0.1),
            pos_hint={'x': 0.05, 'top': 0.95},
            background_color=(0.7, 0.2, 0.2, 1)
        )
        self.btn_voltar.bind(on_release=self.voltar_selecao)
        self.layout.add_widget(self.btn_voltar)
        
        self.add_widget(self.layout)

    def setup_camera(self):
        """Configura e inicia a câmera"""
        try:
            # Libera a câmera se já estiver em uso
            if self.camera is not None:
                self.camera.release()
            
            # Inicializa a câmera
            self.camera = cv2.VideoCapture(CAMERA_ID, cv2.CAP_DSHOW)  # CAP_DSHOW para melhor compatibilidade no Windows
            
            if not self.camera.isOpened():
                print("[ERRO] Não foi possível abrir a câmera.")
                return False
            
            # Define resolução da câmera
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_RESOLUTION[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_RESOLUTION[1])
            
            print(f"[INFO] Câmera inicializada com resolução {CAMERA_RESOLUTION}")
            
            # Inicia a atualização da imagem
            Clock.schedule_interval(self.update_camera, 1.0/30.0)  # 30 FPS
            return True
            
        except Exception as e:
            print(f"[ERRO] Falha ao configurar câmera: {e}")
            return False

    def update_camera(self, dt):
        """Atualiza o feed da câmera"""
        if self.camera is None or not self.camera.isOpened():
            return
        
        ret, frame = self.camera.read()
        if ret:
            # Converte o frame para textura do Kivy
            buf = cv2.flip(frame, 0)  # 0 = flip vertical
            buf = cv2.flip(buf, 1)    # 1 = flip horizontal (efeito espelho)
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf.tobytes(), colorfmt='bgr', bufferfmt='ubyte')
            self.camera_widget.texture = texture
            
            # Salva o último frame capturado
            self.ultimo_frame = frame

    def on_tirar_foto(self, instance):
        """Chamado quando o botão de tirar foto é pressionado"""
        if not self.contagem_ativa:
            self.iniciar_contagem()

    def iniciar_contagem(self):
        """Inicia a contagem regressiva para tirar a foto"""
        self.contagem_ativa = True
        self.countdown_value = COUNTDOWN_TIME
        self.btn_tirar_foto.disabled = True
        self.btn_voltar.disabled = True
        self.lbl_contagem.opacity = 1
        self.atualizar_contagem()

    def atualizar_contagem(self):
        """Atualiza a contagem regressiva na tela"""
        if self.countdown_value > 0:
            # Ainda está contando
            self.lbl_contagem.text = str(self.countdown_value)
            self.countdown_value -= 1
            Clock.schedule_once(lambda dt: self.atualizar_contagem(), 1)
        else:
            # Fim da contagem, captura a foto
            self.lbl_contagem.text = "SORRIA!"
            Clock.schedule_once(lambda dt: self.capturar_foto(), 0.5)

    def capturar_foto(self):
        """Captura a foto após a contagem regressiva"""
        if hasattr(self, 'ultimo_frame'):
            # Pausa a atualização da câmera
            Clock.unschedule(self.update_camera)
            
            # Processa a foto
            app = App.get_running_app()
            app.processar_e_mostrar_foto(self.ultimo_frame.copy())
            
            # Reativa os botões e redefine estados
            self.contagem_ativa = False
            self.btn_tirar_foto.disabled = False
            self.btn_voltar.disabled = False
            self.lbl_contagem.opacity = 0
        else:
            print("[ERRO] Nenhum frame disponível para captura")
            self.contagem_ativa = False
            self.btn_tirar_foto.disabled = False
            self.btn_voltar.disabled = False
            self.lbl_contagem.opacity = 0

    def voltar_selecao(self, instance):
        """Volta para a tela de seleção de molduras"""
        # Para a atualização da câmera
        Clock.unschedule(self.update_camera)
        
        # Libera a câmera
        if self.camera is not None:
            self.camera.release()
            self.camera = None
        
        # Volta para a tela de seleção
        app = App.get_running_app()
        app.sm.current = 'frame_select'

    def on_leave(self):
        """Chamado quando sai desta tela"""
        # Para a atualização da câmera quando sair da tela
        Clock.unschedule(self.update_camera)


class PreviewScreen(Screen):
    def __init__(self, **kwargs):
        super(PreviewScreen, self).__init__(**kwargs)
        
        # Layout principal
        self.layout = BoxLayout(orientation='vertical', padding=20)
        
        # Área para exibir a foto
        self.preview_image = KivyImage(allow_stretch=True, keep_ratio=True)
        self.layout.add_widget(self.preview_image)
        
        # Label com informação sobre impressão
        self.lbl_info = Label(
            text="IMPRIMINDO...",
            font_size='40sp',
            color=(0.2, 0.7, 0.3, 1),
            size_hint=(1, 0.2)
        )
        self.layout.add_widget(self.lbl_info)
        
        self.add_widget(self.layout)

    def mostrar_foto(self, imagem_pil):
        """Exibe a foto processada na tela"""
        # Converte a imagem PIL para uma textura Kivy
        data = imagem_pil.tobytes()
        texture = Texture.create(size=imagem_pil.size, colorfmt='rgb')
        texture.blit_buffer(data, colorfmt='rgb', bufferfmt='ubyte')
        
        # Atualiza a imagem na tela
        self.preview_image.texture = texture


# Execução principal do programa
if __name__ == '__main__':
    try:
        app = PhotoBoothApp()
        app.run()
    except Exception as e:
        print(f"[ERRO FATAL] {e}")
        input("Pressione Enter para sair...")