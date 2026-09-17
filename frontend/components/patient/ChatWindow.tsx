'use client';

import React, { useState, useRef, useEffect } from 'react';
import {
  Send, Mic, MicOff, AlertOctagon, Bot, User, Volume2, VolumeX,
  Radio, RotateCcw, Stethoscope
} from 'lucide-react';
import { Message, Priority, Language } from '../../types';
import { translations } from '../../lib/translations';
import {
  startSpeechRecognition, stopSpeechRecognition,
  speakText, stopSpeech, isSpeechRecognitionSupported
} from '../../lib/voice';

interface ChatWindowProps {
  messages: Message[];
  onSendMessage: (text: string) => void;
  isLoading: boolean;
  priority: Priority;
  isEscalated: boolean;
  language: Language;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  onSendMessage,
  isLoading,
  priority,
  isEscalated,
  language,
}) => {
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const [autoSpeak, setAutoSpeak] = useState(true);
  const [speakingMessageId, setSpeakingMessageId] = useState<number | null>(null);
  const [autoSendCountdown, setAutoSendCountdown] = useState<number | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const lastSpokenMsgId = useRef<number | null>(null);
  const typingTimerRef = useRef<NodeJS.Timeout | null>(null);
  const countdownIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const latestInputRef = useRef('');
  const isListeningRef = useRef(false);
  const isLoadingRef = useRef(isLoading);

  const t = translations[language] || translations.en;

  useEffect(() => {
    latestInputRef.current = input;
  }, [input]);

  useEffect(() => {
    isListeningRef.current = isListening;
  }, [isListening]);

  useEffect(() => {
    isLoadingRef.current = isLoading;
    if (isLoading) {
      if (typingTimerRef.current) clearTimeout(typingTimerRef.current);
      if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current);
      setAutoSendCountdown(null);
    }
  }, [isLoading]);

  // Clean up timers on unmount
  useEffect(() => {
    return () => {
      if (typingTimerRef.current) clearTimeout(typingTimerRef.current);
      if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current);
    };
  }, []);

  const sendCurrentMessage = (textToSend?: string) => {
    const text = (textToSend !== undefined ? textToSend : latestInputRef.current).trim();
    if (!text || isLoadingRef.current) return;

    if (typingTimerRef.current) clearTimeout(typingTimerRef.current);
    if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current);
    setAutoSendCountdown(null);

    if (isListeningRef.current) {
      stopSpeechRecognition();
      setIsListening(false);
    }
    stopSpeech();

    onSendMessage(text);
    setInput('');
    latestInputRef.current = '';
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });

    // Auto-speak latest assistant or staff message if autoSpeak is enabled
    if (autoSpeak && messages.length > 0) {
      const latestMsg = messages[messages.length - 1];
      if ((latestMsg.sender === 'ASSISTANT' || latestMsg.sender === 'CLINICAL_STAFF') && latestMsg.id !== lastSpokenMsgId.current) {
        lastSpokenMsgId.current = latestMsg.id;
        handleSpeak(latestMsg);
      }
    }
  }, [messages, isLoading, autoSpeak]);

  const handleSpeak = (msg: Message) => {
    stopSpeech();
    setSpeakingMessageId(msg.id);
    speakText(
      msg.content,
      language,
      () => setSpeakingMessageId(msg.id),
      () => setSpeakingMessageId(null)
    );
  };

  const handleToggleListening = () => {
    if (isListening) {
      stopSpeechRecognition();
      setIsListening(false);
      // Automatically send message when mic is stopped and input is present
      if (latestInputRef.current.trim()) {
        sendCurrentMessage();
      }
    } else {
      stopSpeech();
      setVoiceError(null);
      setIsListening(true);
      startSpeechRecognition(
        language,
        (transcript, isFinal) => {
          setInput(transcript);
          latestInputRef.current = transcript;
          // Automatically send when voice recognition completes speech!
          if (isFinal && transcript.trim()) {
            setIsListening(false);
            stopSpeechRecognition();
            sendCurrentMessage(transcript.trim());
          }
        },
        (err) => {
          setVoiceError(err);
          setIsListening(false);
        },
        () => {
          setIsListening(false);
          // Automatically send when speech pause/silence ends recording
          if (latestInputRef.current.trim() && !isLoadingRef.current) {
            sendCurrentMessage();
          }
        }
      );
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setInput(val);
    latestInputRef.current = val;

    if (typingTimerRef.current) clearTimeout(typingTimerRef.current);
    if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current);

    if (!val.trim() || val.trim().length < 2 || isLoadingRef.current) {
      setAutoSendCountdown(null);
      return;
    }

    // Auto-enter countdown: 1.8 seconds of pause after typing
    let timeLeft = 2;
    setAutoSendCountdown(timeLeft);

    countdownIntervalRef.current = setInterval(() => {
      timeLeft -= 1;
      if (timeLeft > 0) {
        setAutoSendCountdown(timeLeft);
      } else {
        if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current);
        setAutoSendCountdown(null);
      }
    }, 900);

    typingTimerRef.current = setTimeout(() => {
      if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current);
      setAutoSendCountdown(null);
      if (latestInputRef.current.trim() && !isLoadingRef.current) {
        sendCurrentMessage();
      }
    }, 1800);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendCurrentMessage();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendCurrentMessage();
  };

  return (
    <div className="flex flex-col h-[640px] bg-white rounded-2xl shadow-xl shadow-slate-200/50 border border-slate-200 overflow-hidden">
      {/* Top Voice Controls Bar */}
      <div className="bg-slate-100/90 px-4 py-2 border-b border-slate-200 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2 text-slate-700 font-medium">
          <Volume2 className="w-3.5 h-3.5 text-blue-600" />
          <span>Spoken Voice Guidance:</span>
          <button
            type="button"
            onClick={() => {
              if (autoSpeak) stopSpeech();
              setAutoSpeak(!autoSpeak);
            }}
            className={`px-2 py-0.5 rounded font-semibold transition ${
              autoSpeak
                ? 'bg-blue-600 text-white'
                : 'bg-slate-200 text-slate-600'
            }`}
          >
            {autoSpeak ? 'Auto-Voice ON' : 'Auto-Voice OFF'}
          </button>
        </div>

        {speakingMessageId !== null && (
          <div className="flex items-center space-x-1.5 text-blue-700 animate-pulse font-medium">
            <Radio className="w-3 h-3 text-blue-600" />
            <span>Speaking instruction aloud...</span>
            <button
              onClick={() => {
                stopSpeech();
                setSpeakingMessageId(null);
              }}
              className="ml-2 underline text-slate-500 hover:text-slate-800"
            >
              Stop Audio
            </button>
          </div>
        )}
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 bg-slate-50/50">
        {messages.map((msg) => {
          const isPatient = msg.sender === 'PATIENT';
          const isStaff = msg.sender === 'CLINICAL_STAFF';
          const isUrgent = (msg.content.includes('⚠️') || msg.content.includes('ALERT') || isEscalated) && !isStaff;
          const isCurrentlySpeaking = speakingMessageId === msg.id;

          return (
            <div
              key={msg.id}
              className={`flex items-start space-x-2.5 max-w-[88%] sm:max-w-[80%] ${
                isPatient ? 'ml-auto flex-row-reverse space-x-reverse' : 'mr-auto'
              }`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-white shadow-xs ${
                  isPatient
                    ? 'bg-blue-600'
                    : isStaff
                    ? 'bg-emerald-600 ring-2 ring-emerald-300 shadow-md'
                    : isUrgent
                    ? 'bg-red-600'
                    : 'bg-indigo-600'
                }`}
              >
                {isPatient ? (
                  <User className="w-4 h-4" />
                ) : isStaff ? (
                  <Stethoscope className="w-4 h-4" />
                ) : isUrgent ? (
                  <AlertOctagon className="w-4 h-4" />
                ) : (
                  <Bot className="w-4 h-4" />
                )}
              </div>

              {/* Message Bubble */}
              <div
                className={`rounded-2xl px-4 py-3 text-sm shadow-xs relative group ${
                  isPatient
                    ? 'bg-blue-600 text-white rounded-tr-xs'
                    : isStaff
                    ? 'bg-emerald-50 text-emerald-950 border-2 border-emerald-400 rounded-tl-xs shadow-md shadow-emerald-100/50'
                    : isUrgent
                    ? 'bg-red-50 text-red-950 border border-red-200 rounded-tl-xs'
                    : 'bg-white text-slate-800 border border-slate-200/90 rounded-tl-xs'
                }`}
              >
                <div className="text-[11px] font-semibold opacity-75 mb-1 flex items-center justify-between gap-4">
                  <span className="flex items-center space-x-1">
                    {isStaff && <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 mr-1.5 animate-pulse" />}
                    <span>
                      {isPatient
                        ? 'You (Patient)'
                        : isStaff
                        ? '👨‍⚕️ Clinical / Nursing Staff (Guidance & Instructions)'
                        : 'Hospital OPD Assistant'}
                    </span>
                  </span>
                  <div className="flex items-center space-x-2">
                    {/* Read Aloud Button for Assistant and Staff Messages */}
                    {!isPatient && (
                      <button
                        type="button"
                        onClick={() => handleSpeak(msg)}
                        title="Listen to this message"
                        className={`p-1 rounded hover:bg-slate-200/60 transition ${
                          isCurrentlySpeaking ? 'text-emerald-700 font-bold' : 'text-slate-400 hover:text-slate-700'
                        }`}
                      >
                        <Volume2 className="w-3.5 h-3.5" />
                      </button>
                    )}
                    <span>
                      {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </div>

                <div className="whitespace-pre-line leading-relaxed font-normal">
                  {msg.content}
                </div>

                {isStaff && (
                  <div className="mt-2.5 pt-2 border-t border-emerald-200 text-[11px] text-emerald-800 flex items-center justify-between font-medium">
                    <span>✓ Verified Clinical Staff Note</span>
                    <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full">
                      OPD Care
                    </span>
                  </div>
                )}

                {/* Extracted Structured Info Preview (if available for debugging / transparency) */}
                {msg.extracted_info && Object.keys(msg.extracted_info).length > 0 && isPatient && (
                  <div className="mt-2 pt-2 border-t border-blue-500/30 text-[11px] opacity-90">
                    <span className="font-semibold">Detected:</span>{' '}
                    {[
                      msg.extracted_info.chief_complaint && `Complaint: ${msg.extracted_info.chief_complaint}`,
                      msg.extracted_info.body_part && `Location: ${msg.extracted_info.body_part}`,
                      msg.extracted_info.symptoms?.length > 0 && `Symptoms: ${msg.extracted_info.symptoms.join(', ')}`,
                    ]
                      .filter(Boolean)
                      .join(' | ')}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {isLoading && (
          <div className="flex items-center space-x-2 text-slate-500 text-xs py-2 px-3 bg-white/80 rounded-lg w-fit border border-slate-200 shadow-xs">
            <div className="w-3.5 h-3.5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
            <span>Analyzing message and reviewing hospital safety protocols...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Voice Error Banner */}
      {voiceError && (
        <div className="bg-red-50 text-red-800 text-xs px-4 py-2 border-t border-red-200 flex items-center justify-between">
          <span>{voiceError}</span>
          <button onClick={() => setVoiceError(null)} className="font-bold ml-2">✕</button>
        </div>
      )}

      {/* Input Area with Auto-Send */}
      <form onSubmit={handleSubmit} className="p-3 sm:p-4 bg-white border-t border-slate-200">
        {/* Subtle auto-enter helper status bar */}
        <div className="flex items-center justify-between mb-2 text-[11px] px-1">
          <div className="flex items-center space-x-1.5 text-slate-500 font-medium">
            <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>Auto-send active: Enters automatically when done speaking or typing</span>
          </div>
          {autoSendCountdown !== null && (
            <span className="font-semibold text-blue-700 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded-full animate-pulse shadow-2xs">
              ⚡ Entering in {autoSendCountdown}s...
            </span>
          )}
        </div>

        <div className="flex items-center space-x-2">
          {/* Active Microphone Button */}
          <button
            type="button"
            onClick={handleToggleListening}
            title={isListening ? "Listening... enters automatically when you finish speaking" : "Click and speak in your language"}
            className={`p-2.5 rounded-xl border transition-all cursor-pointer ${
              isListening
                ? 'bg-red-600 border-red-600 text-white animate-pulse shadow-md shadow-red-500/30'
                : 'border-slate-200 text-slate-600 hover:text-blue-600 hover:bg-blue-50/60'
            }`}
          >
            {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
          </button>

          {/* Text input */}
          <input
            type="text"
            value={input}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={
              isListening
                ? 'Listening... speaks and it enters automatically...'
                : isEscalated
                ? 'Clinical staff notified. Enter additional details...'
                : 'Type or speak (enters automatically)...'
            }
            className={`flex-1 text-sm px-4 py-2.5 rounded-xl border transition ${
              isListening
                ? 'border-red-400 ring-2 ring-red-500/20 bg-red-50/20'
                : 'border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500'
            }`}
          />

          {/* Send button (optional manual click) */}
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            title="Press Enter or wait for auto-send"
            className="p-2.5 px-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium rounded-xl shadow-sm transition flex items-center space-x-1.5 cursor-pointer"
          >
            <span className="hidden sm:inline text-xs font-semibold">{t.send}</span>
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
};
