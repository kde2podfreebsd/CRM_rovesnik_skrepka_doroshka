import QrReader, {QrCodeProvider} from "./QrReader"
import {BrowserRouter, Route, Routes} from "react-router-dom";
import TicketsModal from "./modals/TicketsModal.tsx";
import PromoCodeModal from "./modals/PromoCodeModal.tsx";
import UserProfileModal from "./modals/userProfileModal/UserProfileModal.tsx";

export const api_url = 'https://rovesnik-bot.ru/api'

const App = () => {
  return (
    <BrowserRouter>
        <QrCodeProvider>
            <div className='w-full h-full min-h-screen bg-white'>
                <Routes>
                    <Route path="/hostes" element={<QrReader />} />
                    <Route path="/hostes/tickets" element={<TicketsModal />} />
                    <Route path="/hostes/promo-code" element={<PromoCodeModal />} />
                    <Route path="/hostes/user-profile" element={<UserProfileModal />} />
                </Routes>
            </div>
        </QrCodeProvider>
    </BrowserRouter>
  )


}

export default App
