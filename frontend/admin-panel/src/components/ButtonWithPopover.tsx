import React, { useState, ReactNode } from "react";
import {
    Popover,
    PopoverHandler,
    PopoverContent,
    Button,
    ButtonProps,
} from "@material-tailwind/react";

interface ButtonWithPopoverProps {
    onClick: () => void;
    popoverText: string;
    children: ReactNode;
    variant?: ButtonProps['variant'];
    color?: ButtonProps['color'];
}

const ButtonWithPopover: React.FC<ButtonWithPopoverProps> = ({ onClick, popoverText, children, variant = 'filled', color }) => {
    const [isOpen, setIsOpen] = useState(false);

    const handleNoClick = () => {
        setIsOpen(false);
    };

    const handleYesClick = () => {
        onClick();
        setIsOpen(false);
    };

    const togglePopover = () => {
        setIsOpen(!isOpen);
    };

    return (
        <Popover open={isOpen} placement='top' onClose={handleNoClick}>
            <PopoverHandler onClick={togglePopover}>
                <Button
                    onClick={togglePopover}
                    variant={variant}
                    color={color}
                >
                    {children}
                </Button>
            </PopoverHandler>
            <PopoverContent>
                <div className="p-2">
                    <p className='font-bold'>{popoverText}</p>
                    <div className="mt-4 flex justify-center space-x-2">
                        <Button variant="filled" color="green" onClick={handleYesClick}>
                            Yes
                        </Button>
                        <Button variant="outlined" color="red" onClick={handleNoClick}>
                            No
                        </Button>
                    </div>
                </div>
            </PopoverContent>
        </Popover>
    );
};

export default ButtonWithPopover;
