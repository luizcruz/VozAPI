#!/usr/bin/env python3
"""
Script para transcrever arquivos de áudio com o Whisper da OpenAI.

Este utilitário usa a biblioteca `whisper` para carregar um modelo de
reconhecimento de fala e transcrever arquivos de áudio em texto.

Funcionalidades principais:
  * Permite especificar um arquivo de áudio de entrada (`--input`/`-i`).
  * Permite definir explicitamente o idioma do áudio (`--language`/`-l`).
  * Permite indicar o arquivo de saída para gravar a transcrição (`--output`/`-o`).
  * Permite escolher o tamanho do modelo (`--model`/`-m`) entre as opções
    `'tiny'`, `'base'`, `'small'`, `'medium'` e `'large'`.  O tamanho do
    modelo influencia a memória utilizada e a velocidade/precisão.  Segundo a
    documentação oficial, modelos menores como `tiny` e `base` ocupam ~1 GB
    de memória e são até 10× e 7× mais rápidos, respectivamente, que o
    modelo `large`, enquanto modelos como `small` (~2 GB) e `medium`
    (~5 GB) apresentam um compromisso entre velocidade e precisão【49796542301246†L374-L392】.
    O modelo `large` (~10 GB) é mais lento, porém oferece maior precisão【49796542301246†L374-L392】.

Comportamento padrão:
  * Se nenhum arquivo de entrada for especificado, o script procura no
    diretório corrente por arquivos chamados `gravacao.m4u`, `gravacao.mp3`
    ou `gravacao.wav` (nesta ordem). Caso encontre um destes arquivos,
    ele será utilizado como fonte de áudio. Caso contrário, é exibida
    uma mensagem de erro.
  * Se nenhum idioma for informado, o idioma padrão usado é `Portuguese`.
    Observe que o Whisper possui suporte a múltiplos idiomas; ao
    transcrever fala em língua estrangeira, é recomendável passar o
    idioma explicitamente【49796542301246†L420-L427】.
  * Se nenhum arquivo de saída for fornecido, o script salvará a
    transcrição em um arquivo com o mesmo nome-base do arquivo de
    entrada, mas com extensão `.txt`.

Exemplo de uso:

    python transcribe_whisper.py -i audio.mp3 -l Portuguese -o texto.txt
    python transcribe_whisper.py --model small --language en --input entrevista.wav
    python transcribe_whisper.py  # procura gravacao.mp3/gravacao.wav e gera gravacao.txt

Dependências:
    pip install openai-whisper
    pip install ffmpeg-python (caso necessário para manipulação de certos formatos)

"""

import argparse
import os
from pathlib import Path
import sys

try:
    import whisper
except ImportError as exc:
    raise SystemExit(
        "Erro: biblioteca 'whisper' não encontrada. Instale com 'pip install openai-whisper'."
    ) from exc


def parse_args() -> argparse.Namespace:
    """Configura e analisa os argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description=(
            "Transcreve áudio para texto utilizando o modelo Whisper da OpenAI. "
            "É possível especificar o arquivo de entrada, idioma, arquivo de saída e modelo."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        help=(
            "Caminho para o arquivo de áudio de entrada. Se omitido, o script procura "
            "no diretório atual por 'gravacao.m4u', 'gravacao.mp3' ou 'gravacao.wav'."
        ),
    )
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        default=None,
        help=(
            "Idioma do áudio (ex.: 'Portuguese', 'pt', 'English'). Se não for definido, "
            "o idioma padrão será Português. Para transcrição de idiomas não-ingleses, "
            "recomenda-se especificar explicitamente.'"
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help=(
            "Arquivo de saída para salvar a transcrição. Se omitido, será utilizado o "
            "nome-base do arquivo de entrada com extensão '.txt'."
        ),
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help=(
            "Modelo Whisper a ser utilizado. Modelos menores são mais rápidos e "
            "consomem menos memória, enquanto modelos maiores oferecem maior precisão "
            "【49796542301246†L374-L392】."
        ),
    )
    return parser.parse_args()


def find_default_recording() -> str | None:
    """Procura por um arquivo chamado 'gravacao' nas extensões m4u, mp3 ou wav."""
    for ext in ("m4u", "mp3", "wav"):
        candidate = Path(f"gravacao.{ext}")
        if candidate.exists():
            return str(candidate)
    return None


def main() -> None:
    args = parse_args()

    # Determinar o arquivo de entrada
    input_path: str | None = args.input
    if not input_path:
        input_path = find_default_recording()
        if not input_path:
            sys.exit(
                "Erro: nenhum arquivo de entrada foi especificado e não foi encontrado "
                "'gravacao.m4u', 'gravacao.mp3' ou 'gravacao.wav' no diretório atual."
            )

    input_file = Path(input_path)
    if not input_file.exists():
        sys.exit(f"Erro: arquivo de entrada '{input_file}' não encontrado.")

    # Determinar o idioma; se não fornecido, usar Português
    language: str = args.language or "Portuguese"

    # Determinar o arquivo de saída
    output_path: str
    if args.output:
        output_path = args.output
    else:
        # Substituir extensão por .txt
        output_path = str(input_file.with_suffix(".txt"))

    # Carregar o modelo Whisper
    try:
        model = whisper.load_model(args.model)
    except RuntimeError as exc:
        sys.exit(f"Erro ao carregar o modelo '{args.model}': {exc}")

    # Realizar transcrição
    try:
        result = model.transcribe(str(input_file), language=language)
    except Exception as exc:
        sys.exit(f"Erro durante a transcrição: {exc}")

    # Salvar resultado
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result.get("text", ""))
    except Exception as exc:
        sys.exit(f"Erro ao salvar a transcrição em '{output_path}': {exc}")

    print(f"Transcrição concluída. Arquivo salvo em '{output_path}'.")


if __name__ == "__main__":
    main()
