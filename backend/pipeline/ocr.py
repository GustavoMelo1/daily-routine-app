import os
from dotenv import load_dotenv
from google import genai
import json

load_dotenv()
chave = os.getenv("GEMINI_API_KEY")


def extract(path_image):

    client = genai.Client()

    uploaded_file = client.files.upload(file=path_image)

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=[
            {
                "type": "text",
                "text": """Você é um sistema de OCR especializado em caligrafia manuscrita em português do Brasil.

                TAREFA
                Transcrever a página de caderno da imagem. É uma agenda diária: cada bloco começa com o dia da semana + data (às vezes com o tempo estudado ao lado, tipo "ESTUDEI HOJE 1:20"), seguido de itens com caixinhas de checkbox, e no fim da página costuma ter uma seção "FRASE DO DIA" com uma citação e o nome de quem a disse/escreveu.

                REGRAS
                1. Transcreva EXATAMENTE o que está escrito, sem corrigir ortografia, sem completar abreviações e sem reescrever em linguagem formal.
                2. Preserve maiúsculas/minúsculas como aparecem.
                3. Cada item tem uma caixinha à esquerda com TRÊS estados possíveis:
                - "feito" -> caixa preenchida/pintada de caneta
                - "nao_feito" -> caixa cortada por um traço
                - "aberto" -> caixa vazia
                Se não der pra distinguir com confiança, use "incerto".
                4. Palavras ilegíveis: escreva sua melhor tentativa seguida de (?). Se for impossível, use [ilegível].
                5. Não invente itens que não estão na página. Não pule itens.
                6. Linhas em branco no fim da página devem ser ignoradas.
                7. Termos técnicos comuns nesse caderno (use como referência ao desambiguar, mas NÃO force se não bater): estágio, projeto, front, Qlik, SQL, modelagem, GitHub, skincare, Ikigai.
                8. "minutos_estudados": se a página tiver um tempo de estudo anotado (tipo "1:20" ou "45min"), converta pro total em minutos (1:20 vira 80). Se não houver, use 0.
                9. "frase_do_dia" e "autor_frase": pegue especificamente da seção "FRASE DO DIA" (geralmente no fim da página), não do cabeçalho. Se não houver seção assim, use "" pros dois.

                SAÍDA
                Devolva SOMENTE um JSON válido, sem markdown, sem cercas de código, sem comentários, neste formato:

                {
                "dias": [
                    {
                    "dia_semana": "",
                    "data": "AAAA-MM-DD",
                    "minutos_estudados": 0,
                    "frase_do_dia": "",
                    "autor_frase": "",
                    "itens": [
                        { "texto": "", "status": "feito | nao_feito | aberto | incerto" }
                    ]
                    }
                ],
                "trechos_incertos": []
                }

                "trechos_incertos" lista as strings que você marcou com (?) ou [ilegível].""",
            },
            {
                "type": "image",
                "uri": uploaded_file.uri,
                "mime_type": uploaded_file.mime_type,
            },
        ],
    )

    save = json.loads(interaction.output_text)
    return save


print(extract("exemplo.jpeg"))