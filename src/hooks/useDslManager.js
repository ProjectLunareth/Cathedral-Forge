// /src/hooks/useDslManager.js
import { useCallback } from 'react';

const getMirrorName = (name) => {
    if (name.endsWith('_mirror')) return name.replace('_mirror', '');
    return `${name}_mirror`;
};

export const useDslManager = (dsl, setDsl) => {

    const updateAttribute = useCallback((glyphName, command, params = [], symmetry = {x:false, y:false, z:false}) => {
        const commandRegex = new RegExp(`^\\s*${command}\\s+"${glyphName}".*?;`, 'm');
        const newCommandString = `${command} "${glyphName}" ${params.join(' ')};`;

        let tempDsl = dsl || "";
        if (commandRegex.test(tempDsl)) {
            tempDsl = tempDsl.replace(commandRegex, newCommandString);
        } else {
            tempDsl = `${tempDsl.trim()}\n${newCommandString}`;
        }
        
        const mirrorName = getMirrorName(glyphName);
        const mirrorRegex = new RegExp(`^\\s*PLACE\\s+"${mirrorName}"`, 'm');
        
        if (mirrorRegex.test(tempDsl)) {
            let mirroredParams = [...params];
            let needsMirrorUpdate = false;

            if (command === 'PLACE') {
                const atIndex = params.indexOf('AT');
                if (atIndex !== -1) {
                    let [x, y, z] = params.slice(atIndex + 1).map(parseFloat);
                    if (symmetry.x) { x = -x; needsMirrorUpdate = true; }
                    if (symmetry.y) { y = -y; needsMirrorUpdate = true; }
                    if (symmetry.z) { z = -z; needsMirrorUpdate = true; }
                    mirroredParams = ['AT', x.toFixed(2), y.toFixed(2), z.toFixed(2)];
                }
            } else if(command === 'COLOR' || command === 'SCALE') {
                needsMirrorUpdate = true;
            }

            if (needsMirrorUpdate) {
                const mirrorCommandRegex = new RegExp(`^\\s*${command}\\s+"${mirrorName}".*?;`, 'm');
                const mirrorCommandString = `${command} "${mirrorName}" ${mirroredParams.join(' ')};`;
                if (mirrorCommandRegex.test(tempDsl)) {
                    tempDsl = tempDsl.replace(mirrorCommandRegex, mirrorCommandString);
                } else {
                    tempDsl = `${tempDsl.trim()}\n${mirrorCommandString}`;
                }
            }
        }
        
        setDsl(tempDsl);

    }, [dsl, setDsl]);
    
    const addGlyph = useCallback((baseName, position, symmetry) => {
        let newDsl = dsl ? dsl.trim() : '';
        const placeCommand = `PLACE "${baseName}" AT ${position.join(' ')};`;
        newDsl = `${newDsl}\n${placeCommand}`;

        if(symmetry.x || symmetry.y || symmetry.z) {
            const mirrorName = getMirrorName(baseName);
            const mirroredPosition = [
                symmetry.x ? -position[0] : position[0],
                symmetry.y ? -position[1] : position[1],
                symmetry.z ? -position[2] : position[2],
            ];
            const mirrorPlaceCommand = `PLACE "${mirrorName}" AT ${mirroredPosition.join(' ')};`;
            newDsl = `${newDsl}\n${mirrorPlaceCommand}`;
        }
        setDsl(newDsl);
    }, [dsl, setDsl]);

    const removeAttribute = useCallback((glyphName, command) => {
        // Special handling for EMIT command structure
        const commandRegex = command === 'EMIT'
            ? new RegExp(`^\\s*EMIT\\s+FROM\\s+"${glyphName}".*?;\\n?`, 'gm')
            : new RegExp(`^\\s*${command}\\s+"${glyphName}".*?;\\n?`, 'gm');
        
        let newDsl = dsl.replace(commandRegex, '');
        
        const mirrorName = getMirrorName(glyphName);
        const mirrorCommandRegex = command === 'EMIT'
            ? new RegExp(`^\\s*EMIT\\s+FROM\\s+"${mirrorName}".*?;\\n?`, 'gm')
            : new RegExp(`^\\s*${command}\\s+"${mirrorName}".*?;\\n?`, 'gm');
        newDsl = newDsl.replace(mirrorCommandRegex, '');
        
        setDsl(newDsl);
    }, [dsl, setDsl]);

    const getGlyphData = useCallback((glyphName, compiledLayout) => {
        if (!compiledLayout || !compiledLayout.steps || !glyphName) return null;
        
        const glyphData = { name: glyphName, position: [0,0,0], color: '#ffffff', scale: 1.0, animations: {}, forces: {}, emitter: null };

        const placeStep = compiledLayout.steps.find(s => s.command === 'PLACE' && s.arguments[1].replace(/"/g, '') === glyphName);
        if (placeStep) {
            glyphData.position = [ parseFloat(placeStep.arguments[3] || 0), parseFloat(placeStep.arguments[4] || 0), parseFloat(placeStep.arguments[5] || 0) ];
        }

        compiledLayout.steps.forEach(step => {
            // CORE FIX: Correctly identify the glyph name for different command structures
            let stepGlyphName;
            if (step.command === 'EMIT') {
                stepGlyphName = step.arguments[2]?.replace(/"/g, '');
            } else {
                stepGlyphName = step.arguments[1]?.replace(/"/g, '');
            }

            if (stepGlyphName !== glyphName) return;

            switch(step.command) {
                case 'COLOR': glyphData.color = step.arguments[3]; break;
                case 'SCALE': glyphData.scale = parseFloat(step.arguments[3] || 1.0); break;
                case 'PULSE': glyphData.animations.PULSE = { interval: parseFloat(step.arguments[3] || 2000) }; break;
                case 'ORBIT': glyphData.animations.ORBIT = { center: step.arguments[3].replace(/"/g, ''), speed: parseFloat(step.arguments[5] || 1.0) }; break;
                case 'ROTATE': glyphData.animations.ROTATE = { speed: parseFloat(step.arguments[3] || 1.0) }; break;
                case 'ATTRACT':
                    glyphData.forces.ATTRACT = { target: step.arguments[3].replace(/"/g, ''), strength: parseFloat(step.arguments[5] || 1.0) };
                    break;
                case 'REPEL':
                    glyphData.forces.REPEL = { target: step.arguments[3].replace(/"/g, ''), strength: parseFloat(step.arguments[5] || 1.0) };
                    break;
                case 'EMIT':
                    const rateArg = step.arguments.indexOf('RATE');
                    const lifeArg = step.arguments.indexOf('LIFESPAN');
                    const speedArg = step.arguments.indexOf('SPEED');
                    const colorArg = step.arguments.indexOf('COLOR');
                    glyphData.emitter = {
                        rate: rateArg !== -1 ? parseFloat(step.arguments[rateArg + 1]) : 50,
                        lifespan: lifeArg !== -1 ? parseFloat(step.arguments[lifeArg + 1]) : 2000,
                        speed: speedArg !== -1 ? parseFloat(step.arguments[speedArg + 1]) : 1,
                        color: colorArg !== -1 ? step.arguments[colorArg + 1] : '#FFFFFF',
                    };
                    break;
                default: break;
            }
        });

        return glyphData;
    }, []);

    return { updateAttribute, removeAttribute, getGlyphData, addGlyph };
};
