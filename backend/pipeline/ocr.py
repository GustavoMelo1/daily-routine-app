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
                Transcrever a página de caderno da imagem. É uma agenda diária: cada bloco começa com o dia da semana + data, seguido de itens com caixinhas de checkbox.

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

                SAÍDA
                Devolva SOMENTE um JSON válido, sem markdown, sem cercas de código, sem comentários, neste formato:

                {
                "dias": [
                    {
                    "dia_semana": "",
                    "data": "DD/MM/AAAA",
                    "titulo_lateral": "",
                    "itens": [
                        { "texto": "", "status": "feito | nao_feito | aberto | incerto" }
                    ]
                    }
                ],
                "trechos_incertos": []
                }

                "titulo_lateral" é qualquer texto escrito à direita do cabeçalho da data (frase do dia, lembrete etc). Se não houver, use "".
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