import { useState, useContext, createContext, ReactNode, useEffect } from 'react';
import { useNavigate } from "react-router-dom";
import { QrCodeIcon } from "@heroicons/react/24/outline";

interface QrCodeContextType {
  qrCodeData: string;
  setQrCodeData: (qrText: string) => void;
}

const QrCodeContext = createContext<QrCodeContextType | undefined>(undefined);

export const useQrCodeContext = () => {
  const context = useContext(QrCodeContext);
  if (!context) {
    throw new Error('useQrCodeContext must be used within a QrCodeProvider');
  }
  return context;
};

const QrReader = () => {
  const navigate = useNavigate();
  const { setQrCodeData } = useQrCodeContext();

  const handleQrTextReceived = (qrText: string) => {
    setQrCodeData(qrText);

    if (qrText.length === 64) {
      navigate('/hostes/tickets');
    } else if (qrText.length === 32) {
      navigate('/hostes/promo-code');
    } else {
      navigate('/hostes/user-profile');
    }
    return true;
  };

  const startScanning = () => {
    if (window.Telegram.WebApp.showScanQrPopup) {
      window.Telegram.WebApp.showScanQrPopup({}, handleQrTextReceived);
    } else {
      console.log("Функция showScanQrPopup недоступна в этой среде");
    }
  };

  useEffect(() => {
    window.Telegram.WebApp.ready();
    window.Telegram.WebApp.expand();
    startScanning();
  }, []);

  return (
      <div className='w-full h-screen flex flex-col items-center justify-center'>
        <QrCodeIcon className='w-20 h-20' />
      </div>
  );
};

export default QrReader;

interface QrCodeProviderProps {
  children: ReactNode;
}

export const QrCodeProvider = ({ children }: QrCodeProviderProps) => {
  const [qrCodeData, setQrCodeData] = useState('');

  return (
      <QrCodeContext.Provider value={{ qrCodeData, setQrCodeData }}>
        {children}
      </QrCodeContext.Provider>
  );
};
