import clsx from 'clsx'
import React, { memo } from 'react'
import styles from './styles.module.scss'

const sizes = {
  lg: 'h-16 w-16',
  md: 'h-8 w-8',
  sm: 'h-4 w-4',
  xl: 'h-24 w-24',
}

const variants = {
  light: 'text-white',
  primary: 'text-blue-200',
}

export type SpinnerProps = {
  className?: string
  size?: keyof typeof sizes
  variant?: keyof typeof variants
}

const Spinner: React.FC<React.PropsWithChildren<SpinnerProps>> = memo(
  ({ className = '', size = 'md', variant = 'primary' }: SpinnerProps) => {
    return (
      <div className={styles.loaderContainer}>
        <div
          className={styles.tvdd}
          role="img"
          aria-label="Three intersecting rings of twelve pulsing dots that never collide"
        >
          <div className={styles.tvdd__ring}>
            <div className={styles.tvdd__ringDots}>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
            </div>
          </div>
          <div className={styles.tvdd__ring}>
            <div className={styles.tvdd__ringDots}>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
            </div>
          </div>
          <div className={styles.tvdd__ring}>
            <div className={styles.tvdd__ringDots}>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
              <div className={styles.tvdd__ringDot}></div>
            </div>
          </div>
        </div>
      </div>
    )
  },
  () => true,
)
Spinner.displayName = 'Spinner'

export default Spinner
