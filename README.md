# Reddit Search & Monitor (No API)

Desktop GUI application for searching Reddit and discovering related subreddits  
**without using Reddit API keys**.

Десктопное GUI-приложение для поиска по Reddit и обнаружения связанных сабреддитов  
**без использования Reddit API**.

---

## 🔍 Overview | Обзор

**Reddit Search & Monitor** is a desktop tool built with **Python + PyQt6** that allows you to:
- search Reddit posts,
- filter results by time,
- discover related or newly created subreddits,
- manage a blacklist of unwanted content,

all **without OAuth, tokens, or API keys**.

**Reddit Search & Monitor** — это десктопное приложение на **Python + PyQt6**, которое позволяет:
- искать посты в Reddit,
- фильтровать результаты по времени,
- находить связанные или новые сабреддиты,
- управлять чёрным списком нежелательного контента,

и всё это **без OAuth, токенов и Reddit API**.

---

## ✨ Features | Возможности

### 🔎 Search | Поиск
- Keyword search
- Search across multiple subreddits
- Strict limit on number of subreddits
- Time filter:
  - hours / days / weeks / months
- Sort by newest posts
- Blacklist filtering (title, text, URL, flair)

**Поиск по ключевым словам**
- Поиск сразу по нескольким сабреддитам
- Жёсткий лимит количества сабреддитов
- Фильтр по времени:
  - часы / дни / недели / месяцы
- Сортировка по новизне
- Фильтрация по чёрному списку (заголовок, текст, URL, flair)

---

### 🧭 Subreddit Discovery | Поиск сабреддитов
- Find related subreddits by topic
- Discover newly created or active communities
- Useful for research and trend analysis

**Поиск и анализ сабреддитов**
- Нахождение связанных сабреддитов по теме
- Поиск новых или активных сообществ
- Полезно для исследования и анализа трендов

---

### 🚫 Blacklist | Чёрный список
- Built-in filters:
  - Question / Discussion / Humor / Вопрос
- Custom blacklist words
- Persistent storage
- Works for search and subreddit discovery

**Чёрный список**
- Встроенные фильтры:
  - Question / Discussion / Humor / Вопрос
- Пользовательские запрещённые слова и фразы
- Сохранение между запусками
- Работает и для поиска, и для поиска сабреддитов

---

## 🖥 Interface | Интерфейс
- PyQt6 GUI
- Tabs:
  - Search
  - Subreddit discovery
  - Blacklist
- Double-click opens post or subreddit in browser

Графический интерфейс на PyQt6 с вкладками:
- Поиск
- Поиск сабреддитов
- Чёрный список

Двойной клик открывает пост или сабреддит в браузере.

---

## 📦 Installation | Установка

### 1. Clone repository | Клонировать репозиторий
```bash
git clone https://github.com/nikitinsergey1998-debug/reddit-search-monitor.git
cd reddit-search-monitor
