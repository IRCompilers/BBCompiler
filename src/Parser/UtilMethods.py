

def update_table(table, head, symbol, production) -> bool:
    """
    Updates the parsing table

    :param table: current parsing table
    :param head:
    :param symbol:
    :param production:
    :return:
    Boolean: If the table was updated
    """
    if not head in table:
        table[head] = {}

    if not symbol in table[head]:
        table[head][symbol] = []

    if production not in table[head][symbol]:
        table[head][symbol].append(production)

    return len(table[head][symbol]) <= 1
