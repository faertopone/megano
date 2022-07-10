from typing import Dict


class DisplayedPaginatedPagesMixin:
    """
    Добавляет возможность вывода нужного количества страниц для пагинации.
    """
    displayed_pages = 10

    def get_displayed_pages(self) -> int:
        return self.displayed_pages

    def get_paginated_range(self, page_obj, paginator) -> Dict[str, int]:
        """
        Возвращает начальное и конечное значение диапазона страниц, доступных для пагинации.

        :param page_obj: Страница пагинатора
        :param paginator: Пагинатор
        :return:
        """
        displayed_pages = self.get_displayed_pages()
        ctx = dict()

        if (page_num := page_obj.number) <= displayed_pages:
            ctx["first_page_num"] = 1

            # если число отображаемых страниц меньше общего кол-ва страниц, ...
            if self.displayed_pages <= (num_pages := paginator.num_pages):
                # ... то выводим число отображаемых страниц
                ctx["last_page_num"] = displayed_pages
            else:
                # ... в противном случае выводим общее кол-во страниц
                ctx["last_page_num"] = num_pages
        else:
            ctx["first_page_num"] = page_num - displayed_pages + 1
            ctx["last_page_num"] = page_obj.number

        return ctx
