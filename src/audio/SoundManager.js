
/**
 * A singleton class to manage loading and playing audio assets for the Cathedral.
 * This ensures that audio files are loaded only once and can be triggered from anywhere.
 */
class SoundManager {
  constructor() {
    if (SoundManager.instance) {
      return SoundManager.instance;
    }
    this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    this.audioCache = new Map();
    SoundManager.instance = this;
  }

  /**
   * Loads a sound from a given URL and caches the decoded audio data.
   * @param {string} soundName - The key to identify the sound.
   * @param {string} url - The URL of the audio file.
   */
  async loadSound(soundName, url) {
    if (this.audioCache.has(soundName)) {
      return; // Sound already loaded
    }

    try {
      const response = await fetch(url);
      const arrayBuffer = await response.arrayBuffer();
      const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
      this.audioCache.set(soundName, audioBuffer);
      console.log(`Sound '${soundName}' loaded and cached.`);
    } catch (error) {
      console.error(`Error loading sound: ${soundName}`, error);
    }
  }

  /**
   * Plays a pre-loaded sound.
   * @param {string} soundName - The name of the sound to play from the cache.
   */
  playSound(soundName) {
    if (!this.audioCache.has(soundName)) {
      console.warn(`Sound '${soundName}' not found in cache.`);
      return;
    }
    if (this.audioContext.state === 'suspended') {
        this.audioContext.resume();
    }

    const source = this.audioContext.createBufferSource();
    source.buffer = this.audioCache.get(soundName);
    source.connect(this.audioContext.destination);
    source.start(0);
  }
}

// Export a single instance for the entire application to use.
const soundManager = new SoundManager();
export default soundManager;