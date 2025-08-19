"""
API de Formatação de Texto (orientada a objetos)

Módulo que expõe uma API FastAPI para quebrar e justificar texto em linhas com
largura máxima configurável. Foi organizada em estilo orientado a objetos para
separar a lógica de formatação (classe TextFormatter) da camada HTTP (FastAPI).

Endpoints
- POST /format: recebe JSON com texto e opções de formatação e retorna o texto
  formatado e uma lista com as linhas resultantes.
- GET /: rota de sanity-check que indica que a API está ativa.

Exemplo de requisição (curl):

    curl -X POST "http://localhost:3000/format" \
      -H "Content-Type: application/json" \
      -d '{"text":"Linha de exemplo","width":40,"justify":true}'

Retorno do endpoint /format (JSON):
{
  "formatted": "texto formatado com quebras de linha\n...",
  "lines": ["linha 1", "linha 2", ...]
}

Observações:
- Parágrafos são separados por linhas em branco. O formatter normaliza espaços
  internos de cada parágrafo antes de aplicar wrap/justify.
- A classe TextFormatter é independente de FastAPI e pode ser reutilizada em
  outros contextos (CLI, scripts, testes unitários, etc.).
"""

from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI(title="String Formatter API (OOP)")


class FormatRequest(BaseModel):
    """
    Modelo de requisição para o endpoint /format.

    Attributes
    ----------
    text : str
        Texto a ser formatado. Pode conter múltiplos parágrafos separados por
        uma linha em branco.
    width : int, optional
        Largura máxima (número de caracteres) por linha. Padrão: 40.
    justify : bool, optional
        Se True, aplica justificação às linhas (distributed spacing).
        Padrão: False.
    justify_last_line : bool, optional
        Se True, também justifica a última linha de cada parágrafo. Caso contrário
        a última linha fica alinhada à esquerda. Padrão: False.
    """

    text: str
    width: int = 40
    justify: bool = False
    justify_last_line: bool = False


class TextFormatter:
    """
    Classe responsável por formatar textos (quebra de linha e justificação).

    A intenção é manter a lógica de formatação separada da camada HTTP para
    facilitar testes unitários e reuso.

    Parameters
    ----------
    default_width : int, optional
        Largura padrão utilizada quando não for fornecida explicitamente.
    """

    def __init__(self, default_width: int = 40):
        """
        Inicializa o formatter com uma largura padrão.

        Parameters
        ----------
        default_width : int
            Largura padrão por linha quando `width` não for especificado.
        """
        self.default_width = default_width

    def wrap_paragraph(self, paragraph: str, width: int) -> List[str]:
        """
        Quebra um parágrafo em linhas sem ultrapassar a largura `width`.

        Regras principais:
        - Não quebra palavras no meio; se uma palavra for maior que `width` ela
          ocupará sozinha a linha (comportamento intencional).
        - Normaliza espaços internos previamente (a chamada externa deve já ter
          feito a normalização quando necessário).

        Parameters
        ----------
        paragraph : str
            Texto do parágrafo (uma única string, sem quebras de parágrafo).
        width : int
            Largura máxima permitida por linha.

        Returns
        -------
        List[str]
            Lista de linhas resultantes, cada elemento com comprimento <= width
            salvo quando houver palavras maiores que `width`.
        """
        words = paragraph.split()
        lines: List[str] = []
        current: List[str] = []
        curr_len = 0
        for w in words:
            if curr_len == 0:
                current.append(w)
                curr_len = len(w)
            elif curr_len + 1 + len(w) <= width:
                current.append(w)
                curr_len += 1 + len(w)
            else:
                lines.append(" ".join(current))
                current = [w]
                curr_len = len(w)
        if current:
            lines.append(" ".join(current))
        return lines

    def justify_line(self, words: List[str], width: int) -> str:
        """
        Justifica uma linha (lista de palavras) para que ocupe exatamente `width`.

        O algoritmo distribui os espaços entre os gaps (espaços entre palavras)
        o mais uniformemente possível; os gaps mais à esquerda recebem 1 espaço
        extra quando a divisão não for exata.

        Parameters
        ----------
        words : List[str]
            Lista de palavras que compõem a linha (não contém espaços).
        width : int
            Largura final desejada para a linha (número de caracteres).

        Returns
        -------
        str
            Linha justificada com comprimento igual a `width` (ou maior se uma
            palavra sozinha exceder `width`).
        """
        if not words:
            return ""
        if len(words) == 1:
            return words[0] + " " * max(0, width - len(words[0]))
        total_words_len = sum(len(w) for w in words)
        total_spaces = width - total_words_len
        gaps = len(words) - 1
        base_space, extra = divmod(total_spaces, gaps)
        parts: List[str] = []
        for i, w in enumerate(words):
            parts.append(w)
            if i < gaps:
                spaces = base_space + (1 if i < extra else 0)
                parts.append(" " * spaces)
        return "".join(parts)

    def justify_paragraph(self, paragraph: str, width: int, justify_last_line: bool = False) -> List[str]:
        """
        Aplica wrap e justificação a um parágrafo completo.

        A entrada é primeiro quebrada em linhas com `wrap_paragraph`. Em seguida,
        cada linha é justificada com `justify_line` exceto a última, que por
        padrão é retornada alinhada à esquerda a menos que
        `justify_last_line=True`.

        Parameters
        ----------
        paragraph : str
            Parágrafo (texto sem quebras de parágrafo internas).
        width : int
            Largura alvo para as linhas.
        justify_last_line : bool, optional
            Se True, justifica também a última linha do parágrafo.

        Returns
        -------
        List[str]
            Lista de linhas do parágrafo, justificadas conforme opção.
        """
        wrapped = self.wrap_paragraph(paragraph, width)
        justified: List[str] = []
        for i, line in enumerate(wrapped):
            words = line.split()
            if i == len(wrapped) - 1 and not justify_last_line:
                justified.append(" ".join(words))
            else:
                justified.append(self.justify_line(words, width))
        return justified

    def format_text(self, text: str, width: int | None = None, justify: bool = False, justify_last_line: bool = False) -> str:
        """
        Formata um texto completo possivelmente com múltiplos parágrafos.

        Fluxo:
        1. Se `width` for None usa `self.default_width`.
        2. Separa parágrafos por linhas em branco (regex `\n\s*\n`).
        3. Normaliza espaços internos de cada parágrafo.
        4. Para cada parágrafo aplica wrap ou justify conforme `justify`.
        5. Reúne os parágrafos com uma linha em branco entre eles.

        Parameters
        ----------
        text : str
            Texto de entrada (pode conter múltiplos parágrafos).
        width : int | None, optional
            Largura desejada por linha; se None usa `self.default_width`.
        justify : bool, optional
            Se True, aplica justificação completa nas linhas (exceto última
            a menos que `justify_last_line=True`).
        justify_last_line : bool, optional
            Determina se a última linha de cada parágrafo será justificada.

        Returns
        -------
        str
            Texto formatado, com quebras de linha (`\n`) e parágrafos
            separados por uma linha em branco.
        """
        if width is None:
            width = self.default_width
        paragraphs = re.split(r'\n\s*\n', text.strip(), flags=re.UNICODE)
        formatted_paras: List[str] = []
        for p in paragraphs:
            p_clean = " ".join(p.split())
            if justify:
                lines = self.justify_paragraph(p_clean, width, justify_last_line=justify_last_line)
            else:
                lines = self.wrap_paragraph(p_clean, width)
            formatted_paras.append("\n".join(lines))
        return "\n\n".join(formatted_paras)


# Instância do formatter (pode virar dependência com FastAPI Depends se quiser)
formatter = TextFormatter(default_width=40)


@app.post("/format")
def format_endpoint(req: FormatRequest):
    """
    Endpoint que formata o texto enviado no corpo da requisição.

    Parameters
    ----------
    req : FormatRequest
        Objeto pydantic com os parâmetros: text, width, justify e justify_last_line.

    Returns
    -------
    dict
        JSON com as chaves:
        - "formatted": string contendo o texto completo já formatado (com \n).
        - "lines": lista de strings, cada uma representando uma linha formatada.

    Observações
    ----------
    Esta função delega a lógica de formatação para a instância `formatter`, que
    pode ser trocada por injeção de dependência em cenários de produção ou
    testes.
    """
    formatted = formatter.format_text(req.text, width=req.width, justify=req.justify, justify_last_line=req.justify_last_line)
    lines = formatted.splitlines()
    return {"formatted": formatted, "lines": lines}


@app.get("/")
def read_root():
    """
    Rota raiz simples para indicar que a API está ativa.

    Returns
    -------
    dict
        Mensagem simples de status que pode ser usada para health checks.
    """
    return {"message": "API ativa. Use POST /format ou abra /docs"}
