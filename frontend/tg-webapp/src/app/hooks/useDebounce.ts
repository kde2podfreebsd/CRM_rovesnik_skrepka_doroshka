import {useEffect, useCallback, DependencyList, EffectCallback} from 'react';

export default function useDebounce(effect: EffectCallback, dependencies: DependencyList, delay: number) {
    const callback = useCallback(effect, dependencies);

    useEffect(() => {
        const timeout = setTimeout(callback, delay);
        return () => clearTimeout(timeout);
    }, [callback, delay]);
}