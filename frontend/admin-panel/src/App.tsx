import Header from "./components/Header.tsx";
import {useState} from "react";
import Events from "./pages/Events.tsx";
import Tickets from "./pages/Tickets.tsx";
import Artists from "./pages/Artists.tsx";
import Tests from "./pages/Tests.tsx";
import Promotions from "./pages/Promotions.tsx";
import PromoCodes from "./pages/PromoCodes.tsx";
import Users from "./pages/users/Users.tsx";
import Reservations from "./pages/reservations/Reservations.tsx";
import BarControl from "./pages/BarControl.tsx";
import Smm from "./pages/smm/SMM.tsx";
import PartnerGift from "./pages/PartnerGift.tsx";
import Faq from "./pages/FAQ.tsx";

function App() {

    const [currentPage, setCurrentPage] = useState('Events');
    const currentPageParser = (page: string) => {
        switch (page) {
            case 'Events':
                return <Events />;
            case 'Tickets':
                return <Tickets />;
            case 'Artists':
                return <Artists />;
            case 'Tests':
                return <Tests />;
            case 'Promotions':
                return <Promotions/>;
            case 'Promo codes':
                return <PromoCodes />;
            case 'Users':
                return <Users />
            case 'Reservations':
                return <Reservations />
            case 'Bar control':
                return <BarControl />
            case 'SMM':
                return <Smm />
            case 'PartnerGift':
                return <PartnerGift />
            case 'FAQ':
                return <Faq />
        }
    }

  return (
    <>
      <header className='shadow-md'>
        <Header currentPage={currentPage} setCurrentPage={setCurrentPage}/>
      </header>

        <main className='bg-neutral-600 h-full min-h-screen'>
            {currentPageParser(currentPage)}
        </main>
      </>
  )
}

export default App
