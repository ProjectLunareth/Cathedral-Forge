import { useEffect, useState } from 'react';
import soundManager from '../audio/SoundManager';

const useAudioManager = (soundsToLoad) => {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    let isMounted = true;
    const loadSounds = async () => {
      // Ensure the AudioContext is resumed, as browsers require user interaction
      if (soundManager.audioContext.state === 'suspended') {
        await soundManager.audioContext.resume();
      }
      
      const loadPromises = soundsToLoad.map(sound => 
        soundManager.loadSound(sound.name, sound.url)
      );
      
      await Promise.all(loadPromises);
      
      if (isMounted) {
        setIsReady(true);
      }
    };

    loadSounds();

    return () => {
      isMounted = false;
    };
  }, [soundsToLoad]);

  return isReady;
};

export default useAudioManager;