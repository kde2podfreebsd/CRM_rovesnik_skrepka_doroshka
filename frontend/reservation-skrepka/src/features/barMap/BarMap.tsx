import { Canvas, useLoader } from "@react-three/fiber";
import { OrbitControls } from '@react-three/drei';
import { Environment } from '@react-three/drei';
import React, { Suspense } from "react";
import Spinner from "../../compoments/Spinner";
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { Selection, Select, EffectComposer, Outline } from '@react-three/postprocessing'
import styles from './styles.module.scss';
import { rovesnikFloorPaths } from "../../shared/constants";

type Props = {
    floor: number,
}
const BarMap = ({floor}: Props) => {
    const model = useLoader(GLTFLoader, rovesnikFloorPaths[floor - 1]);

    return (
         <Canvas className={styles.root}>
            <Suspense fallback={<Spinner />}>
                <primitive object={model.scene} />
            </Suspense>

            <OrbitControls />
            <directionalLight castShadow />
            <Environment preset='city' />
        </Canvas>
    )
};

export default BarMap;
