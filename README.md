**Sobre a interface:** A interface é simples e intuitiva, com botões grandes adaptados para tela sensível ao toque. Inicialmente, você verá miniaturas das molduras disponíveis para seleção. Após escolher uma moldura, aparecerá um botão grande “TIRAR FOTO”. Depois de tirar uma foto, você verá uma prévia da imagem já com a moldura aplicada antes da impressão.

**Como adicionar suas próprias molduras:**

**As molduras devem estar em formato PNG com  tamanho recomendado é de 1280x720 pixels (ou proporção 16:9)Basta colocar seus arquivos PNG na pasta “molduras” do projeto A área transparente ao centro é onde aparecerá a foto tirada Foi incluído um script `criar_molduras_exemplo.py`que mostra como criar molduras de exemplo**

- As molduras devem estar em formato PNG com transparência
- O tamanho recomendado é de 1280x720 pixels (ou proporção 16:9)
- Basta colocar seus arquivos PNG na pasta “molduras” do projeto
- A área transparente ao centro é onde aparecerá a foto tirada
- Foi incluído um script `criar_molduras_exemplo.py`
    
    **que mostra como criar molduras de exemplo**
    

**Exemplo de moldura:** Suas molduras devem ter um fundo transparente na área central onde a foto será inserida, com elementos decorativos nas bordas. O sistema redimensionará automaticamente as molduras para ajustar a resolução da câmera.

**Instalação rápida:** Sim, a instalação é simples! Basta seguir as instruções no início do código:

**Instalar as dependências:`pip install -r requirements.txt`Certifique-se de que sua câmera está conectadaExecutar`python main.py`**

- Instalar as dependências:`pip install -r requirements.txt`
- Certifique-se de que sua câmera está conectada
- Executar`python main.py`

O código possui instruções feitas em português sobre como configurar a câmera, verificar impressoras e fazer ajustes se necessário.

PIP

Sim, além das bibliotecas Python que são instaladas automaticamente seguindo as instruções do código (via pip), você precisará instalar o seguinte no PC da cabine:

**Python 3.7 ou superior - Necessário instalar manualmente no Windows. Você pode baixá-lo em https://www.python.org/downloads/ . Durante a instalação, marque a opção “Adicionar Python ao PATH”.**

**Drivers da câmera Canon - Se você estiver usando uma câmera Canon, precisará instalar drivers especiais específicos para o seu modelo de câmera.** 

**Configuração de impressora - O padrão da impressora do Windows deve estar instalado e configurado corretamente.**

- **Python 3.7 ou superior** - Necessário instalar manualmente no Windows. Você pode baixá-lo em https://www.python.org/downloads/ . Durante a instalação, marque a opção “Adicionar Python ao PATH”.
- **Drivers da câmera Canon** - Se você estiver usando uma câmera Canon, precisará instalar drivers especiais específicos para o seu modelo de câmera.
- **Configuração de impressora** - O padrão da impressora do Windows deve estar instalado e configurado corretamente.

O código foi desenvolvido para minimizar dependências externas. As bibliotecas Python permitidas (Kivy, OpenCV, Pillow e pywin32) serão instaladas automaticamente usando o comando `pip install -r requirements.txt`conforme as instruções incluídas no código.

Depois disso, o sistema deve funcionar sem a necessidade de outros softwares externos, pois ele utiliza os sistemas já presentes no Windows para comunicação com a câmera (via DirectShow) e a impressora (via serviço de impressão do Windows).
