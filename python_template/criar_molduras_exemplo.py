"""
Script para criar molduras de exemplo para o sistema de cabine fotográfica
Este script gera algumas molduras PNG com transparência para usar como exemplo
"""

from PIL import Image, ImageDraw, ImageFont
import os
import math

# Cria o diretório de molduras se não existir
if not os.path.exists('molduras'):
    os.makedirs('molduras')
    print("Pasta 'molduras' criada.")

# Configurações para as molduras
tamanho_a4 = (2480, 3508)  # A4 em 300 DPI
cores = [
    (255, 0, 0, 255),      # Vermelho
    (0, 0, 255, 255),      # Azul
    (0, 255, 0, 255),      # Verde
    (255, 0, 255, 255),    # Rosa
]

def criar_moldura_basica(nome_arquivo, cor, tamanho=tamanho_a4, borda=100):
    """Cria uma moldura básica com borda colorida e centro transparente"""
    print(f"Criando moldura {nome_arquivo}...")
    
    # Cria uma imagem transparente
    imagem = Image.new("RGBA", tamanho, (0, 0, 0, 0))
    desenho = ImageDraw.Draw(imagem)
    
    # Desenha a borda externa
    desenho.rectangle([(0, 0), (tamanho[0], tamanho[1])], outline=cor, width=borda)
    
    # Salva a imagem
    caminho_arquivo = os.path.join("molduras", nome_arquivo)
    imagem.save(caminho_arquivo, "PNG")
    print(f"Moldura salva em {caminho_arquivo}")

def criar_moldura_decorada(nome_arquivo, cor, tamanho=tamanho_a4, borda=80):
    """Cria uma moldura decorada com cantos arredondados e elementos decorativos"""
    print(f"Criando moldura decorada {nome_arquivo}...")
    
    # Cria uma imagem transparente
    imagem = Image.new("RGBA", tamanho, (0, 0, 0, 0))
    desenho = ImageDraw.Draw(imagem)
    
    # Desenha a borda com cantos arredondados
    # Como o PIL não tem método para retângulo com cantos arredondados, 
    # desenhamos a borda em quatro seções
    largura, altura = tamanho
    
    # Margens internas
    margem_x = int(largura * 0.1)
    margem_y = int(altura * 0.1)
    
    # Desenha as bordas
    # Borda superior
    desenho.rectangle([(0, 0), (largura, borda)], fill=cor)
    # Borda inferior
    desenho.rectangle([(0, altura-borda), (largura, altura)], fill=cor)
    # Borda esquerda
    desenho.rectangle([(0, borda), (borda, altura-borda)], fill=cor)
    # Borda direita
    desenho.rectangle([(largura-borda, borda), (largura, altura-borda)], fill=cor)
    
    # Adiciona elementos decorativos - círculos nos cantos
    raio_circulo = int(borda * 1.5)
    
    # Círculo superior esquerdo
    desenho.ellipse([(borda//2, borda//2), (borda//2 + raio_circulo, borda//2 + raio_circulo)], fill=cor)
    
    # Círculo superior direito
    desenho.ellipse([(largura - borda//2 - raio_circulo, borda//2), 
                     (largura - borda//2, borda//2 + raio_circulo)], fill=cor)
    
    # Círculo inferior esquerdo
    desenho.ellipse([(borda//2, altura - borda//2 - raio_circulo), 
                     (borda//2 + raio_circulo, altura - borda//2)], fill=cor)
    
    # Círculo inferior direito
    desenho.ellipse([(largura - borda//2 - raio_circulo, altura - borda//2 - raio_circulo), 
                     (largura - borda//2, altura - borda//2)], fill=cor)
    
    # Salva a imagem
    caminho_arquivo = os.path.join("molduras", nome_arquivo)
    imagem.save(caminho_arquivo, "PNG")
    print(f"Moldura decorada salva em {caminho_arquivo}")

def criar_moldura_com_texto(nome_arquivo, cor, texto, tamanho=tamanho_a4, borda=100):
    """Cria uma moldura com texto na parte inferior"""
    print(f"Criando moldura com texto {nome_arquivo}...")
    
    # Cria uma imagem transparente
    imagem = Image.new("RGBA", tamanho, (0, 0, 0, 0))
    desenho = ImageDraw.Draw(imagem)
    
    # Desenha a borda externa
    desenho.rectangle([(0, 0), (tamanho[0], tamanho[1])], outline=cor, width=borda)
    
    # Adiciona um banner na parte inferior
    altura_banner = int(tamanho[1] * 0.15)
    desenho.rectangle([(borda, tamanho[1] - altura_banner - borda), 
                      (tamanho[0] - borda, tamanho[1] - borda)], 
                      fill=(cor[0], cor[1], cor[2], 180))
    
    # Tenta usar uma fonte padrão (se não encontrar, usa fonte padrão do PIL)
    try:
        # Tenta carregar uma fonte, se não conseguir, usará a fonte padrão
        fonte = ImageFont.truetype("arial.ttf", 120)
    except IOError:
        fonte = ImageFont.load_default()
    
    # Adiciona o texto ao banner - usando método mais recente do PIL
    left, top, right, bottom = desenho.textbbox((0, 0), texto, font=fonte)
    largura_texto = right - left
    altura_texto = bottom - top
    posicao_x = (tamanho[0] - largura_texto) // 2
    posicao_y = tamanho[1] - altura_banner // 2 - altura_texto // 2 - borda
    desenho.text((posicao_x, posicao_y), texto, fill=(255, 255, 255, 255), font=fonte)
    
    # Salva a imagem
    caminho_arquivo = os.path.join("molduras", nome_arquivo)
    imagem.save(caminho_arquivo, "PNG")
    print(f"Moldura com texto salva em {caminho_arquivo}")

def criar_moldura_estrelas(nome_arquivo, cor, tamanho=tamanho_a4, borda=80, num_estrelas=12):
    """Cria uma moldura com estrelas ao redor"""
    print(f"Criando moldura com estrelas {nome_arquivo}...")
    
    # Cria uma imagem transparente
    imagem = Image.new("RGBA", tamanho, (0, 0, 0, 0))
    desenho = ImageDraw.Draw(imagem)
    
    # Desenha a borda externa
    desenho.rectangle([(borda, borda), (tamanho[0] - borda, tamanho[1] - borda)], outline=cor, width=borda//2)
    
    # Adiciona estrelas ao redor da borda
    raio = min(tamanho[0], tamanho[1]) // 2
    centro_x = tamanho[0] // 2
    centro_y = tamanho[1] // 2
    tamanho_estrela = borda * 1.5
    
    for i in range(num_estrelas):
        angulo = 2 * math.pi * i / num_estrelas
        x = centro_x + int(raio * math.cos(angulo))
        y = centro_y + int(raio * math.sin(angulo))
        
        # Desenha uma estrela simples (um asterisco)
        desenhar_estrela(desenho, (x, y), tamanho_estrela, cor)
    
    # Salva a imagem
    caminho_arquivo = os.path.join("molduras", nome_arquivo)
    imagem.save(caminho_arquivo, "PNG")
    print(f"Moldura com estrelas salva em {caminho_arquivo}")

def desenhar_estrela(desenho, centro, tamanho, cor):
    """Desenha uma estrela no canvas"""
    x, y = centro
    pontas = 5
    raio_externo = tamanho // 2
    raio_interno = raio_externo // 2
    
    pontos = []
    for i in range(pontas * 2):
        raio = raio_externo if i % 2 == 0 else raio_interno
        angulo = math.pi / pontas * i
        px = x + int(raio * math.sin(angulo))
        py = y - int(raio * math.cos(angulo))
        pontos.append((px, py))
    
    desenho.polygon(pontos, fill=cor)

# Cria as molduras de exemplo
criar_moldura_basica("moldura_vermelha.png", cores[0])
criar_moldura_decorada("moldura_azul_decorada.png", cores[1])
criar_moldura_com_texto("moldura_verde_texto.png", cores[2], "CABINE FOTOGRÁFICA")
criar_moldura_estrelas("moldura_rosa_estrelas.png", cores[3])

print("Criação de molduras de exemplo concluída!")
print("Foram criadas 4 molduras na pasta 'molduras/'")
print("Agora você pode executar o sistema de cabine fotográfica com 'python main.py'")