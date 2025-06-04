import React from "react";
import {
    IconButton,
    List,
    ListItem,
    Drawer,
    Card,
} from "@material-tailwind/react";
import {
    Bars3Icon,
    XMarkIcon,
} from "@heroicons/react/24/outline";

interface props {
    currentPage: string;
    setCurrentPage: React.Dispatch<React.SetStateAction<string>>
}

export function Header({ currentPage, setCurrentPage }: props) {
    const [isDrawerOpen, setIsDrawerOpen] = React.useState(false);

    const openDrawer = () => setIsDrawerOpen(true);
    const closeDrawer = () => setIsDrawerOpen(false);

    const onPageClick = (page: string) => {
        setCurrentPage(page);
        closeDrawer();
    }

    const currentPageParser = (string: string) => {
        switch (currentPage) {
            case 'Events':
                return 'События';
            case 'Tickets':
                return 'Билеты';
            case 'Artists':
                return 'Артисты';
            case 'Tests':
                return 'Тесты';
            case 'Promotions':
                return 'Каналы партнеров';
            case 'Promo codes':
                return 'Промокоды';
            case 'Users':
                return 'Пользователи';
            case 'Reservations':
                return 'Бронирования';
            case 'Bar control':
                return 'Управление баром';
            case 'SMM':
                return 'SMM';
            case 'PartnerGift':
                return 'Подарки от партеров';
            case 'FAQ':
                return 'FAQ'
        }
    }

    return (
        <div className="w-full bg-neutral-700 flex p-2 shadow-md rounded-b-xs">
            <div className='flex items-center w-full text-white'>
                <IconButton variant="text" size="lg" onClick={openDrawer} className=""
                            placeholder={undefined} onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined}>
                    {isDrawerOpen ? (
                        <XMarkIcon className="h-10 w-10 stroke-2 z-10" color='white' />
                    ) : (
                        <Bars3Icon className="h-10 w-10 stroke-2 text-white" />
                    )}
                </IconButton>
                <p className='text-3xl font-bold'>{currentPageParser(currentPage)}</p>
            </div>
            <Drawer open={isDrawerOpen} onClose={closeDrawer} className="w-full bg-neutral-700"
                    placeholder={undefined} onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined}>
                <button onClick={closeDrawer} className="absolute top-4 right-4 z-10">
                    <XMarkIcon className="h-8 w-8 stroke-2" />
                </button>
                <Card
                    color="transparent"
                    shadow={false}
                    className="h-[calc(100vh-2rem)] w-full p-4" placeholder={undefined}
                    onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined}>
                    <List className="text-2xl text-neutral-200 font-semibold mt-8" placeholder={undefined} onPointerEnterCapture={undefined}
                          onPointerLeaveCapture={undefined}>
                        <ListItem onClick={() => onPageClick('Events')} placeholder={undefined}
                                  onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined}>
                            События
                        </ListItem>
                        <ListItem onClick={() => onPageClick('Tickets')} placeholder={undefined}
                                  onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined}>
                            Билеты
                        </ListItem>
                        <ListItem onClick={() => onPageClick('Artists')} placeholder={undefined}
                                  onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined}>
                            Артисты
                        </ListItem>
                        <ListItem onClick={() => onPageClick('Tests')} placeholder={undefined}
                                  onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined}>
                            Тесты
                        </ListItem>
                        <ListItem onClick={() => onPageClick('Promotions')} placeholder={undefined}
                                  onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined}>
                            Каналы партнеров
                        </ListItem>
                        <ListItem onClick={() => onPageClick('PartnerGift')} placeholder={undefined}
                                  onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined}>
                            Подарки от партнеров
                        </ListItem>
                        <ListItem onClick={() => onPageClick('Promo codes')} placeholder={undefined}
                                  onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined}>
                           Промокоды
                        </ListItem>
                        <ListItem onClick={() => onPageClick('Users')} placeholder={undefined}
                                  onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined}>
                            Пользователи
                        </ListItem>
                        <ListItem onClick={() => onPageClick('Reservations')} placeholder={undefined}
                                  onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined}>
                            Бронирования
                        </ListItem>
                        <ListItem onClick={() => onPageClick('Bar control')} placeholder={undefined}
                                  onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined}>
                            Управление баром
                        </ListItem>
                        <ListItem onClick={() => onPageClick('SMM')} placeholder={undefined}
                                  onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined}>
                            SMM
                        </ListItem>
                        <ListItem onClick={() => onPageClick('FAQ')} placeholder={undefined}
                                  onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined}>
                            FAQ
                        </ListItem>
                    </List>
                </Card>
            </Drawer>
        </div>
    );
}

export default Header;
