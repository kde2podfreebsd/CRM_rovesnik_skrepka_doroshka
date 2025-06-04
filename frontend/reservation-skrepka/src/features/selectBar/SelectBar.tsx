import React, { useState } from 'react'
import styles from './styles.module.scss';

type TOption = 'oneBar' | 'allBars';

const SelectBar: React.FC = () => {
  const [selectedOption, setSelectedOption] = useState<TOption>('oneBar');


  const options: { value: TOption; label: string }[] = [
    { value: 'oneBar', label: 'Для одного бара' },
    { value: 'allBars', label: 'Для всех 3-х баров' },
  ];
  const handleButtonClick = (option: TOption) => {
    setSelectedOption(option);
  }


  return (
    <div>
      {options.map((option) => (
        <button
          key={option.value}
          className={selectedOption === option.value ? styles.selectedButton : ''}
          onClick={() => handleButtonClick(option.value)}
        >
          {option.label}
        </button>
      ))}
    </div>
  )
}

export default SelectBar;