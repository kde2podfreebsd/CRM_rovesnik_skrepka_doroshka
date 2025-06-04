import React from 'react'

import { twoPersonTableLight, twoPersonTableDark } from '../../shared/assets'
import { tableCapacityCases } from '../../shared/constants'
import { useTheme } from '../../shared/ui/themeContext/ThemeContext'

import styles from './styles.module.scss'
import { ITable } from '../../api/TablesService'

type Props = {
  info: ITable
  isSelected: boolean
  onClick: () => void
}
const Table = ({ info, isSelected, onClick }: Props) => {
  const getAvailabilityColor = () => {
    switch (info.reserved) {
      case !info.reserved:
        return 'rgba(0, 211, 34, 1)'
      case info.reserved:
        return 'orange'
    }
  }

  const { theme } = useTheme()
  const rootClassName = theme === 'dark' ? styles.darkRoot : styles.lightRoot
  const mainClassName = theme === 'dark' ? styles.darkMain : styles.lightMain
  const imgTableTheme =
    theme === 'dark' ? twoPersonTableDark : twoPersonTableLight

  return (
    <div className={`${styles.root} ${rootClassName}`}>
      <div
        className={`${styles.main} ${isSelected ? styles.selected : ''} ${mainClassName}`}
        onClick={() => onClick()}
      >
        <div className={styles.tableInfo}>
          <div className={styles.tableInfoTitle}>
            <div
              className={styles.availability}
              style={{ backgroundColor: getAvailabilityColor() }}
            />
            <h1>{`Стол №${info.table_id}`.toLocaleUpperCase()}</h1>
          </div>
          <div className={styles.tableDetails}>
            <p>
              {`Стол на ${info.capacity} ${tableCapacityCases.get(info.capacity)}`}
              <span>|</span>
              {`${info.storey} этаж`}
            </p>
          </div>
        </div>
        <div className={styles.table}>
          <img src={imgTableTheme} alt={'table'} />
        </div>
      </div>
    </div>
  )
}

export default Table
