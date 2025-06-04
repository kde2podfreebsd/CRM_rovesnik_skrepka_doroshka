import {QrCodeIcon} from "@heroicons/react/24/outline";
import {useNavigate} from "react-router-dom";

const GoBackToScanButton = () => {

    const navigate = useNavigate()


    return (
        <button onClick={() => navigate('/')}
                className='flex gap-2 text-lg justify-center items-center bg-neutral-100 px-4 py-2 rounded-md'>
            <QrCodeIcon className='h-8 w-8'/>
            Сканировать еще
        </button>
    );
};

export default GoBackToScanButton;