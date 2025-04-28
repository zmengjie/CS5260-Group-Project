// Enhanced React UI with avatars, mood memory, emotional tone, Whisper input, onboarding, theme features, mini games, breathing guide, chat goals, and achievements
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import musicPiano from './assets/piano.mp3';
import musicOcean from './assets/ocean.mp3';
import musicForest from './assets/forest.mp3';
import Lottie from 'lottie-react';
import onboardingAnim from './assets/onboarding.json';
import './App.css';

const themes = {
  Dream: 'linear-gradient(to right, #fbc2eb, #a6c1ee)',
  Ocean: 'linear-gradient(to right, #a1c4fd, #c2e9fb)',
  Forest: 'linear-gradient(to right, #dce35b, #45b649)',
  Dusk: 'linear-gradient(to right, #2c3e50, #4ca1af)',
  Night: 'linear-gradient(to bottom right, #0f0c29, #302b63, #24243e)'
};

const musicTracks = {
  Piano: musicPiano,
  Ocean: musicOcean,
  Forest: musicForest
};

const avatars = {
  You: '🧍',
  Luma: '🧘‍♀️'
};

const moodColors = {
  happy: '#ffeaa7',
  sad: '#dfe6e9',
  anxious: '#fab1a0',
  calm: '#a29bfe'
};

const detectMood = (text) => {
  const lower = text.toLowerCase();
  if (lower.includes('sad') || lower.includes('depressed')) return 'sad';
  if (lower.includes('anxious') || lower.includes('nervous') || lower.includes('stress')) return 'anxious';
  if (lower.includes('happy') || lower.includes('excited')) return 'happy';
  return 'calm';
};

export default function App() {
  const [input, setInput] = useState('');
  const [theme, setTheme] = useState('Dream');
  const [music, setMusic] = useState('Ocean');
  const [playing, setPlaying] = useState(true);
  const [mood, setMood] = useState('calm');
  const [showOnboarding, setShowOnboarding] = useState(true);
  const [userName, setUserName] = useState('You');
  const [companionName, setCompanionName] = useState('Luma');
  const [messages, setMessages] = useState([{ from: companionName, text: "Hello! I'm here to support you. Before scheduling an appointment, may I ask you a few questions to better understand your situation?" }]);
  const [showBreathing, setShowBreathing] = useState(false);
  const [achievements, setAchievements] = useState([]);
  const [goals, setGoals] = useState([]);
  const audioRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.load();
      if (playing) audioRef.current.play();
    }
  }, [music, playing]);

  useEffect(() => {
    inputRef.current?.focus();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const newMessages = [...messages, { from: userName, text: input }];
    setMessages(newMessages);
    setInput('');
    const res = await axios.post('http://127.0.0.1:8000/chat', { message: input });
    const softened = softenTone(res.data.reply);
    const newMood = detectMood(input);
    setMood(newMood);
    updateAchievements(newMood);
    updateGoals(input);
    setMessages([...newMessages, { from: companionName, text: softened }]);
  };

  const updateAchievements = (mood) => {
    if (!achievements.includes(mood)) {
      setAchievements(prev => [...prev, mood]);
    }
  };

  const updateGoals = (inputText) => {
    if (inputText.toLowerCase().includes('goal') && !goals.includes(inputText)) {
      setGoals(prev => [...prev, inputText]);
    }
  };

  const softenTone = (text) => {
    let msg = text;
    msg = msg.replace(/I'm sorry to hear that/g, "It sounds like you're going through a lot");
    msg = msg.replace(/Remember that/g, "Just know");
    msg = msg.replace(/Take care of yourself/g, "Be kind to yourself");
    msg = msg.replace(/You're not alone/g, "You have support");
    return msg;
  };

  if (showOnboarding) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh', animation: 'fadeIn 1s ease-in' }}>
        <Lottie animationData={onboardingAnim} loop={true} style={{ height: 300 }} />
        <h2>Welcome to Luma - Your Empathetic Companion</h2>
        <p>Let's get started with your emotional wellness journey 💖</p>
        <input type="text" placeholder="What's your name?" onChange={e => setUserName(e.target.value || 'You')} style={{ marginBottom: '0.5rem', padding: '0.5rem' }} />
        <input type="text" placeholder="What should we call your companion?" onChange={e => setCompanionName(e.target.value || 'Luma')} style={{ marginBottom: '1rem', padding: '0.5rem' }} />
        <button onClick={() => setShowOnboarding(false)} style={{ padding: '0.5rem 1rem' }}>Start my journey →</button>
      </div>
    );
  }


  return (
    <div style={{ background: themes[theme], minHeight: '100vh', padding: '1rem', transition: 'background 1s ease', display: 'flex', flexDirection: 'column' }}>
      <audio ref={audioRef} loop>
        <source src={musicTracks[music]} type="audio/mp3" />
      </audio>

      <h1 style={{ textAlign: 'center' }}>🌸 {companionName} - Your Empathetic Companion</h1>

      <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginBottom: '1rem' }}>
        <button onClick={() => setPlaying(!playing)}>{playing ? '🔇 Mute Music' : '🎵 Play Music'}</button>
        <button onClick={() => setTheme('Night')}>🌙 Night Mode</button>
        <select value={theme} onChange={e => setTheme(e.target.value)}>{Object.keys(themes).map(th => <option key={th} value={th}>{th}</option>)}</select>
        <select value={music} onChange={e => setMusic(e.target.value)}>{Object.keys(musicTracks).map(m => <option key={m} value={m}>{m}</option>)}</select>
        <button onClick={() => setShowBreathing(!showBreathing)}>🧘 Breathing</button>

      </div>

      {showBreathing && (
        <div style={{ textAlign: 'center', marginBottom: '1rem', fontSize: '1.2rem' }}>
          🌬️ Breathe in... hold... breathe out... Repeat 3x.
        </div>
      )}


      <div style={{ maxWidth: 800, margin: '0 auto', background: moodColors[mood], borderRadius: 10, padding: 20, flexGrow: 1, transition: 'background 1s ease', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        <div style={{ overflowY: 'auto', flexGrow: 1 }}>
          {messages.map((m, i) => (
            <div key={i} style={{ textAlign: m.from === userName ? 'right' : 'left', marginBottom: '1rem' }}>
              <strong>{avatars[m.from === userName ? 'You' : 'Luma']} {m.from}:</strong> {m.text}
            </div>
          ))}
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem' }}>
          <input ref={inputRef} style={{ flexGrow: 1, padding: '0.5rem', marginRight: '0.5rem' }} value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleSend()} placeholder="Type how you feel..." />
          <button onClick={handleSend} style={{ padding: '0.5rem 1rem' }}>Send</button>
        </div>
      </div>

      <div style={{ marginTop: '2rem', textAlign: 'center' }}>
        <h3>🧾 Upload Psychological Tests</h3>
        <input type="file" onChange={async (e) => {
          const file = e.target.files[0];
          const form = new FormData();
          form.append('file', file);
          const res = await axios.post('http://127.0.0.1:8000/analyze', form);
          setMessages([...messages, { from: companionName, text: res.data.feedback }]);
        }} />
      </div>

      <div style={{ marginTop: '2rem', textAlign: 'center' }}>
        <h3>🏆 Achievements</h3>
        {achievements.length === 0 ? <p>No achievements yet. Start chatting!</p> : (
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {achievements.map((a, i) => <li key={i}>🎖️ Expressed feeling: {a}</li>)}
          </ul>
        )}
      </div>

      <div style={{ marginTop: '2rem', textAlign: 'center' }}>
        <h3>🎯 Self-Care Goals</h3>
        {goals.length === 0 ? <p>No goals yet. Mention something like "My goal is to..."</p> : (
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {goals.map((g, i) => <li key={i}>🌱 {g}</li>)}
          </ul>
        )}
      </div>

      <div style={{ textAlign: 'center', marginTop: '2rem', fontSize: '0.9rem', opacity: 0.7 }}>
        💡 Tip: You can say "I'm nervous about exams" or upload a .png/.pdf of your reflections.
      </div>
    </div>
  );
}