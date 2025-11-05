import logging

from app.config import settings


def setup_logging():
    """Configure application-wide logging.

    Sets up logging with the configured log level and format.
    This should be called once at application startup.
    """
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(levelname)s:     %(message)s - %(name)s:%(lineno)d",
        handlers=[logging.StreamHandler()],
    )
    logger = logging.getLogger(__name__)
    logger.info("Logging configured with level: %s", settings.LOG_LEVEL)


def get_page_count(item_count: int, page_size: int):
    """Calculate the total number of pages based on item count and page size.

    Args:
        item_count: Total number of items to paginate.
        page_size: Number of items per page.

    Returns:
        int: The total number of pages.
    """
    if item_count == 0:
        return 0
    return (item_count + page_size - 1) // page_size


def get_prev_page(page_number: int):  # noqa: E501
    """Get the previous page number if it exists.

    Args:
        page_number: Current page number (0-indexed).

    Returns:
        int | None: The previous page number, or None if on the first page.
    """
    return page_number - 1 if page_number > 0 else None


def get_next_page(item_count: int, page_number: int, page_size: int):
    """Get the next page number if it exists.

    Args:
        item_count: Total number of items to paginate.
        page_number: Current page number (0-indexed).
        page_size: Number of items per page.

    Returns:
        int | None: The next page number, or None if on the last page.
    """
    page_count = get_page_count(item_count, page_size)
    if page_number >= page_count:
        return None

    return page_number + 1
