#!/usr/bin/env python3
"""
novel_downloader.core.parsers.qidian.main_parser
------------------------------------------------

Main parser class for handling Qidian HTML
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from novel_downloader.core.parsers.base import BaseParser
from novel_downloader.core.parsers.registry import register_parser
from novel_downloader.models import ChapterDict, ParserConfig
from novel_downloader.utils import find_cookie_value
from novel_downloader.utils.constants import DATA_DIR

from .book_info_parser import parse_book_info
from .chapter_router import parse_chapter
from .utils import is_encrypted

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from novel_downloader.utils.fontocr import FontOCR


@register_parser(
    site_keys=["qidian", "qd"],
    backends=["session", "browser"],
)
class QidianParser(BaseParser):
    """
    Parser for Qidian site.
    """

    def __init__(
        self,
        config: ParserConfig,
        fuid: str = "",
    ):
        """
        Initialize the QidianParser with the given configuration.

        :param config: ParserConfig object controlling:
        """
        super().__init__(config)

        # Extract and store parser flags from config
        self._use_truncation = config.use_truncation
        self._decode_font: bool = config.decode_font

        self._fixed_font_dir: Path = self._base_cache_dir / "fixed_fonts"
        self._fixed_font_dir.mkdir(parents=True, exist_ok=True)
        self._debug_dir: Path = Path.cwd() / "debug"

        state_files = [
            DATA_DIR / "qidian" / "browser_state.cookies",
            DATA_DIR / "qidian" / "session_state.cookies",
        ]
        self._fuid: str = fuid or find_cookie_value(state_files, "ywguid")

        self._font_ocr: FontOCR | None = None
        if self._decode_font:
            try:
                from novel_downloader.utils.fontocr import FontOCR
            except ImportError:
                logger.warning(
                    "[QidianParser] FontOCR not available, font decoding will skip"
                )
            else:
                self._font_ocr = FontOCR(
                    cache_dir=self._base_cache_dir,
                    use_freq=config.use_freq,
                    use_ocr=config.use_ocr,
                    use_vec=config.use_vec,
                    batch_size=config.batch_size,
                    gpu_mem=config.gpu_mem,
                    gpu_id=config.gpu_id,
                    ocr_weight=config.ocr_weight,
                    vec_weight=config.vec_weight,
                    font_debug=config.save_font_debug,
                )

    def parse_book_info(
        self,
        html_list: list[str],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Parse a book info page and extract metadata and chapter structure.

        :param html_list: Raw HTML of the book info page.
        :return: Parsed metadata and chapter structure as a dictionary.
        """
        if not html_list:
            return {}
        return parse_book_info(html_list[0])

    def parse_chapter(
        self,
        html_list: list[str],
        chapter_id: str,
        **kwargs: Any,
    ) -> ChapterDict | None:
        """
        :param html_list: Raw HTML of the chapter page.
        :param chapter_id: Identifier of the chapter being parsed.
        :return: Cleaned chapter content as plain text.
        """
        if not html_list:
            return None
        return parse_chapter(self, html_list[0], chapter_id)

    def is_encrypted(self, html_str: str) -> bool:
        """
        Return True if content is encrypted.

        :param html: Raw HTML of the chapter page.
        """
        return is_encrypted(html_str)

    @property
    def save_font_debug(self) -> bool:
        return self._config.save_font_debug
