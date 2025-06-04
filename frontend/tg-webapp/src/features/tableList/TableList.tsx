import { List } from '@mui/material'
import React, { useState } from 'react'

import { ITable } from '../../api/TablesService'
import Table from '../table'

import styles from './styles.module.scss'

const TableList = ({
  onTableSelect,
  tables,
  selectedFloor,
   setSelectedTable,
  selectedTable
}: {
  onTableSelect: (table: ITable) => void
  tables: ITable[]
  selectedFloor: number
  setSelectedTable: (table: ITable) => void
  selectedTable: ITable | null
}) => {

  const handleTableClick = (table: ITable) => {
    setSelectedTable(table)
  }

  return (
    <div className='max-h-80 overflow-y-scroll'>
      <List style={{ maxHeight: '100%', overflow: 'auto' }}>
        {tables
          .filter((table) => selectedFloor === table.storey)
          .map((table) => (
            <Table
              key={table?.table_uuid}
              info={table}
              isSelected={selectedTable && selectedTable.table_uuid! === table.table_uuid!}
              onClick={() => handleTableClick(table)}
            />
          ))}
      </List>
    </div>
  )
}

export default TableList
