'use client';

import { Language } from '../types';

export interface VoiceRecognitionState {
  isListening: boolean;
  transcript: string;
  interimTranscript: string;
  error: string | null;
  isSupported: boolean;
}

const LANG_MAP: Record<Language, string> = {
  en: 'en-IN',
  hi: 'hi-IN',
  mr: 'mr-IN',
};

// Global recognition instance
let recognitionInstance: any = null;

export function isSpeechRecognitionSupported(): boolean {
  if (typeof window === 'undefined') return false;
  return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
}

export function startSpeechRecognition(
  language: Language,
  onResult: (transcript: string, isFinal: boolean) => void,
  onError: (err: string) => void,
  onEnd: () => void
): () => void {
  if (!isSpeechRecognitionSupported()) {
    onError('Speech recognition is not supported in this browser. Please use Chrome, Edge, or a WebSpeech-compatible browser.');
    return () => {};
  }

  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  
  if (recognitionInstance) {
    try {
      recognitionInstance.abort();
    } catch (e) {
      // Ignored
    }
  }

  const recognition = new SpeechRecognition();
  recognitionInstance = recognition;
  
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.lang = LANG_MAP[language] || 'en-IN';

  recognition.onresult = (event: any) => {
    let interim = '';
    let final = '';

    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        final += event.results[i][0].transcript;
      } else {
        interim += event.results[i][0].transcript;
      }
    }

    if (final) {
      onResult(final.trim(), true);
    } else if (interim) {
      onResult(interim.trim(), false);
    }
  };

  recognition.onerror = (event: any) => {
    let msg = `Speech error: ${event.error}`;
    if (event.error === 'not-allowed') {
      msg = 'Microphone permission denied. Please grant microphone access in browser settings.';
    } else if (event.error === 'no-speech') {
      msg = 'No speech detected. Please try speaking again.';
    }
    onError(msg);
  };

  recognition.onend = () => {
    onEnd();
  };

  try {
    recognition.start();
  } catch (e: any) {
    onError(`Failed to start microphone: ${e.message || e}`);
    onEnd();
  }

  return () => {
    try {
      recognition.stop();
    } catch (e) {
      // Ignored
    }
  };
}

export function stopSpeechRecognition(): void {
  if (recognitionInstance) {
    try {
      recognitionInstance.stop();
    } catch (e) {
      // Ignored
    }
  }
}

/**
 * Speaks text aloud using Browser SpeechSynthesis with language matching
 */
export function speakText(
  text: string,
  language: Language,
  onStart?: () => void,
  onEnd?: () => void
): void {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
    return;
  }

  // Cancel any active speech
  window.speechSynthesis.cancel();

  // Strip emojis and demo flags for cleaner voice output
  const cleanText = text
    .replace(/[⚠️🚨✓•*]/g, '')
    .replace(/DEMO PLACEHOLDER:/gi, '')
    .replace(/डेमो सूचना:/g, '')
    .replace(/डेमो सूचना:/g, '')
    .trim();

  if (!cleanText) return;

  const utterance = new SpeechSynthesisUtterance(cleanText);
  utterance.lang = LANG_MAP[language] || 'en-IN';
  utterance.rate = 0.95; // Slightly calmer speaking rate for patient understanding
  utterance.pitch = 1.0;

  // Try to find a matching native voice
  const voices = window.speechSynthesis.getVoices();
  const targetCode = LANG_MAP[language]?.split('-')[0];
  const matchedVoice = voices.find(v => v.lang.startsWith(targetCode || 'en'));
  if (matchedVoice) {
    utterance.voice = matchedVoice;
  }

  if (onStart) utterance.onstart = onStart;
  if (onEnd) utterance.onend = onEnd;
  utterance.onerror = () => {
    if (onEnd) onEnd();
  };

  window.speechSynthesis.speak(utterance);
}

export function stopSpeech(): void {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
}
