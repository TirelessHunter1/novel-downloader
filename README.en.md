# novel-downloader

A novel downloading tool/library based on [Playwright](https://playwright.dev/) and [aiohttp](https://github.com/aio-libs/aiohttp).

> This project is developed with Python 3.12. Please ensure your runtime environment is Python 3.11 or above.

## Features

* Supports resuming interrupted downloads automatically
* Automatically merges all chapters and exports to:

  * TXT
  * EPUB (optionally includes chapter illustrations)
* Active ad filtering support:

  * [x] Chapter titles
  * [ ] Chapter content

---

## Quick Start

### Installation

Install via pip:

```bash
pip install novel-downloader
```

To use **browser mode** (`mode: browser`), ensure Playwright dependencies are installed:

```bash
playwright install
```

To enable **font decryption** (`decode_font`, used to handle recent font obfuscation on Qidian), install with extras:

```bash
pip install novel-downloader[font-recovery]
```

* For details, see: [Installation](docs/1-installation.md)

---

### CLI Mode

```bash
# Initialize default config (creates settings.toml)
novel-cli config init

# Edit ./settings.toml to set site/book_ids
# Refer to docs/3-settings-schema.md for schema details

# Run download task
novel-cli download 123456
```

* See also: [Supported Sites List](docs/4-supported-sites.md)
* More examples: [CLI Usage Examples](docs/6-cli-usage-examples.md)

---

### TUI Mode (Terminal UI)

**Note:** TUI mode is still under development. Login and settings modification are currently unsupported. CLI mode is recommended for now.

```bash
# Initialize default config (creates settings.toml)
novel-cli config init

# Edit ./settings.toml for network configuration
# Refer to docs/3-settings-schema.md for schema details

# Launch TUI interface
novel-tui
```

* See also: [Supported Sites List](docs/4-supported-sites.md)
* More examples: [TUI Usage Examples](docs/5-tui-usage-examples.md)

---

### GUI Mode (Graphical Interface)

Not yet implemented.

---

## Install from GitHub (Development Version)

To try the latest development features, install directly from GitHub:

```bash
git clone https://github.com/BowenZ217/novel-downloader.git
cd novel-downloader
pip install .
# Or with optional features:
# pip install .[font-recovery]
```

---

## Documentation Structure

* [Project Overview](#项目简介)
* [Installation](docs/1-installation.md)
* [Configuration](docs/2-configuration.md)
* [settings.toml Schema](docs/3-settings-schema.md)
* [Supported Sites List](docs/4-supported-sites.md)
* [TUI Usage Examples](docs/5-tui-usage-examples.md)
* [CLI Usage Examples](docs/6-cli-usage-examples.md)
* [Copying Cookies](docs/copy-cookies.md)
* [File Saving](docs/file-saving.md)
* [Modules & API Reference](docs/api/README.md)
* [TODO](docs/todo.md)
* [Development Guide](docs/develop.md)
* [Project Notice](#项目说明)

---

## Project Notice

* This project is intended for educational and research purposes only. It must not be used for any commercial or illegal activities. Please comply with the target site's `robots.txt` and all applicable laws and regulations.
* The developer bears no responsibility for any legal consequences resulting from the use of this tool.
* Site structure changes or other issues may cause the program to malfunction. You are encouraged to adjust the code or seek alternative solutions if needed.
