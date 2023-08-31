def r_prefixed_docstring() -> None:
    r"""
    Wat? Why?!
    """


def function_with_codeblock_in_middle(text: str) -> None:
    """
    My comment

    .. code-block:: python
        function_with_codeblock_in_middle("Hello World")

    Some more documentation.
    """
    assert text == 'Hello World'


def function_with_single_line_codeblock_at_end(text: str) -> None:
    """
    My comment

    .. code-block:: python
        function_with_single_line_codeblock_at_end("Hello World")
    """
    assert text == 'Hello World'


def function_with_multi_line_codeblock_at_end(text):
    """
    My comment

    .. code-block:: python
        function_with_multi_line_codeblock_at_end("Hello")
        function_with_multi_line_codeblock_at_end("World")
    """
    assert text in ('Hello', 'World')
