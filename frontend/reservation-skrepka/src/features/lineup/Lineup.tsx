import React, { useEffect, useRef, useState } from "react";
import { Artist } from "../../shared/types";
import ArtistCard from "../artistCard";
import styles from './styles.module.scss';

type Props = {
    artists: Artist[],
}
const Lineup = ({ artists }: Props) => {
    const lineupRef = useRef<HTMLDivElement | null>(null);
    const [isScrolling, setIsScrolling] = useState(true);

    const stopAnimation = () => {
        lineupRef.current = null
        setIsScrolling(false)
    };

    useEffect(() => {
        if (!isScrolling) return;

        const lineupEl = lineupRef.current;
        if (lineupEl && isScrolling) {
            const cardWidth = window.innerWidth >= 375 ? 150 : 135;
            const gapWidth = 20;

            const singleSetWidth = cardWidth * artists.length + gapWidth * (artists.length - 1);
            let animationFrameId: number;

            const scroll = () => {
                if (!isScrolling || !lineupEl) {
                    cancelAnimationFrame(animationFrameId);
                    return;
                }

                if (lineupEl.scrollLeft >= singleSetWidth) {
                    lineupEl.scrollLeft = 0;
                } else {
                    lineupEl.scrollLeft += 1;
                }
                animationFrameId = requestAnimationFrame(scroll);
            };

            // @ts-ignore
            if ((!isScrolling || !lineupEl) && (animationFrameId !== undefined)) {
                cancelAnimationFrame(animationFrameId);
                return;
            } else {
                animationFrameId = requestAnimationFrame(scroll);
            }

            return () => {
                if (animationFrameId) {
                    cancelAnimationFrame(animationFrameId);
                }
            };
        }
    }, [artists, isScrolling]);

    return (
        <div className={`${styles.lineupContainer} overflow-x-hidden w-full`} ref={lineupRef} onTouchStart={stopAnimation} onClick={stopAnimation}>
            <div className={`${styles.lineup} flex justify-center items-center overflow-x-scroll w-full p-2`} onTouchStart={stopAnimation} onDrag={stopAnimation}>
                {artists.map((artist) => (
                    <ArtistCard key={artist.artist_id} artist={artist} />
                ))}

            </div>
        </div>

    );
};

export default Lineup;
