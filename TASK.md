# Задача: транскрипция YouTube видео

## Видео
https://youtu.be/6WEsPzHyD9k

"Как пользоваться AI в 2026, если вы не технарь? Оля Маркес и Дима Мацкевич" (~103 мин, язык: русский)

## Что нужно сделать

1. Установить зависимости (если не установлены):
   - `yt-dlp` — скачать аудио с YouTube
   - `openai-whisper` — транскрибировать речь
   - `ffmpeg` — конвертация аудио

2. Скачать аудио из видео

3. Транскрибировать аудио через Whisper (модель `medium` или `large`)

4. Сохранить результат в двух файлах:
   - `transcript.txt` — чистый текст
   - `transcript.srt` — субтитры с таймкодами

## Готовый скрипт

В репозитории уже есть `transcribe.py`. Запустить так:

```bash
python3 transcribe.py "https://youtu.be/6WEsPzHyD9k" --language ru --model medium
```

Если YouTube требует авторизацию:

```bash
python3 transcribe.py "https://youtu.be/6WEsPzHyD9k" --language ru --model medium --cookies-from-browser chrome
```

## Установка зависимостей

```bash
pip install yt-dlp openai-whisper
```

**ffmpeg:**
- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt install ffmpeg`
- Windows: скачать с https://ffmpeg.org/download.html и добавить в PATH

## Примечания

- Модель `medium` — хороший баланс скорости и качества (~5 ГБ RAM)
- Модель `large` — точнее, но медленнее (~10 ГБ RAM)
- Видео длинное (~103 мин), транскрипция займёт несколько минут
- Whisper автоматически определяет язык, но `--language ru` ускоряет процесс
- Если нет GPU — работает на CPU, просто медленнее
