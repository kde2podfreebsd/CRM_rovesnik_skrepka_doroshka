from BackendApp.Database.Models.table_model import Table
from BackendApp.API.table.schemas import TableForReturn

def parse_table_into_format(table: Table):
    return TableForReturn(
        bar_id=table.bar_id,
        storey=table.storey,
        table_id=table.table_id,
        table_uuid=table.table_uuid,
        terminal_group_uuid=table.terminal_group_uuid,
        capacity=table.capacity,
        reserved=table.reserved,
        is_bowling=table.is_bowling,
        is_pool=table.is_pool,
        block_start=table.block_start,
        block_end=table.block_end
    )