/**
 * Offline Audio Cues & Web Speech Synthesis for WalkBacker
 * Uses native browser SpeechSynthesis and AudioContext.
 * 100% offline, zero network requests, zero data usage.
 */
class OfflineAudioCueEngine {
  constructor() {
    this.synth = window.speechSynthesis;
    this.audioCtx = null;
    this.isSpeaking = false;
  }

  initAudioContext() {
    if (!this.audioCtx) {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (AudioContextClass) {
        this.audioCtx = new AudioContextClass();
      }
    }
  }

  /**
   * Synthesize natural offline voice cue into headphones
   */
  speak(text) {
    if (!this.synth) {
      console.warn("SpeechSynthesis not supported on this browser.");
      return;
    }

    // Cancel ongoing speech
    this.synth.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95; // slightly slower, mindful walking cadence
    utterance.pitch = 1.0;
    utterance.lang = "en-US";

    // Select preferred natural English voice if available
    const voices = this.synth.getVoices();
    const naturalVoice = voices.find(v => v.lang.startsWith("en") && !v.name.includes("whisper"));
    if (naturalVoice) {
      utterance.voice = naturalVoice;
    }

    utterance.onstart = () => { this.isSpeaking = true; };
    utterance.onend = () => { this.isSpeaking = false; };
    utterance.onerror = () => { this.isSpeaking = false; };

    this.synth.speak(utterance);
  }

  /**
   * Sound a gentle 2-tone melodic chime for turnaround / waypoint alerts
   */
  playTurnaroundChime() {
    this.initAudioContext();
    if (!this.audioCtx) return;

    if (this.audioCtx.state === "suspended") {
      this.audioCtx.resume();
    }

    const now = this.audioCtx.currentTime;

    // First tone (G4, 392Hz)
    const osc1 = this.audioCtx.createOscillator();
    const gain1 = this.audioCtx.createGain();
    osc1.type = "sine";
    osc1.frequency.setValueAtTime(392.00, now);
    gain1.gain.setValueAtTime(0.15, now);
    gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.8);
    osc1.connect(gain1);
    gain1.connect(this.audioCtx.destination);
    osc1.start(now);
    osc1.stop(now + 0.8);

    // Second tone (C5, 523.25Hz)
    const osc2 = this.audioCtx.createOscillator();
    const gain2 = this.audioCtx.createGain();
    osc2.type = "sine";
    osc2.frequency.setValueAtTime(523.25, now + 0.35);
    gain2.gain.setValueAtTime(0.2, now + 0.35);
    gain2.gain.exponentialRampToValueAtTime(0.001, now + 1.2);
    osc2.connect(gain2);
    gain2.connect(this.audioCtx.destination);
    osc2.start(now + 0.35);
    osc2.stop(now + 1.2);
  }

  stop() {
    if (this.synth) {
      this.synth.cancel();
      this.isSpeaking = false;
    }
  }
}

// Global instance
window.audioCueEngine = new OfflineAudioCueEngine();
