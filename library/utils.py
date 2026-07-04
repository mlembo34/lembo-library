def author_sort_key(author: str) -> str:
    """
    Returns a sortable key based on the first author's last name.

    Examples:
        Eric Matthes
            -> matthes eric matthes

        Donald E. Knuth
            -> knuth donald e. knuth

        J. R. R. Tolkien
            -> tolkien j. r. r. tolkien

        Thomas H. Cormen, Charles E. Leiserson
            -> cormen thomas h. cormen
    """

    if not author:
        return ""

    # Only use the first listed author
    first_author = author.split(",")[0].strip()

    if not first_author:
        return ""

    parts = first_author.split()

    if len(parts) == 1:
        return parts[0].lower()

    last_name = parts[-1]

    return f"{last_name.lower()} {first_author.lower()}"