import { createContext } from "react";

export const FormValidationContext = createContext<{
    isValid: boolean,
    setIsValid: React.Dispatch<React.SetStateAction<boolean>>,
    showErrorLabel: boolean,
    setShowErrorLabel: React.Dispatch<React.SetStateAction<boolean>>
} | null>(null);
