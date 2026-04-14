class RedisPaginationMixin:
    """Mixin class to provide pagination functionality for Redis queries."""

    def paginate(self, items: list, page: int, page_size: int) -> list:
        """Paginate a list of items.

        Args:
            items (list[dict]): The list of items to paginate.
            page (int): The page number to return.
            page_size (int): The number of items per page.

        Returns:
            list: A list of items for the requested page.
        """
        return items[(page - 1) * page_size : page * page_size]
