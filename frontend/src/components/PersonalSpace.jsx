import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { User, Shield, CheckCircle2, Clock, Terminal, Save, Sparkles } from 'lucide-react';
import axios from 'axios';
import { useEmails } from '../hooks/useEmails';

const API_BASE = 'http://127.0.0.1:8000';

export default function PersonalSpace() {
  const { emails } = useEmails();
  const [profile, setProfile] = useState({
    name: '',
    tone_preference: 'Professional',
    signature: '',
    daily_goal: ''
  });
  const [saving, setSaving] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const res = await axios.get(`${API_BASE}/user-profile`);
      setProfile(res.data);
    } catch (err) {
      console.error("Fetch profile error:", err);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.post(`${API_BASE}/user-profile`, profile);
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 2000);
    } catch (err) {
      console.error("Save error:", err);
    } finally {
      setSaving(false);
    }
  };

  const tasks = emails.filter(e => 
    e.classification === 'Urgent_Fire' || e.classification === 'Action_Required'
  ).slice(0, 5);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-8 max-w-6xl mx-auto"
    >
      <header className="mb-10">
        <h1 className="text-3xl font-bold tracking-tight mb-2">Personal Space</h1>
        <p className="text-[var(--text-3)]">Manage your identity and how your AI brain perceives you.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: User Identity */}
        <div className="lg:col-span-2 space-y-8">
          <section className="glass-card p-6 rounded-2xl border-[var(--border)] relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10">
              <User size={80} />
            </div>
            <h2 className="text-lg font-bold mb-6 flex items-center gap-2">
              <Shield size={18} className="text-[var(--primary)]" />
              Core Identity
            </h2>
            
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-xs uppercase font-bold tracking-widest text-[var(--text-3)]">Display Name</label>
                  <input 
                    className="w-full bg-[var(--surface2)] border border-[var(--border)] rounded-lg px-4 py-2.5 outline-none focus:border-[var(--primary)] transition-all"
                    value={profile.name}
                    onChange={e => setProfile({...profile, name: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-xs uppercase font-bold tracking-widest text-[var(--text-3)]">Daily Focus Goal</label>
                  <input 
                    className="w-full bg-[var(--surface2)] border border-[var(--border)] rounded-lg px-4 py-2.5 outline-none focus:border-[var(--primary)] transition-all"
                    value={profile.daily_goal}
                    onChange={e => setProfile({...profile, daily_goal: e.target.value})}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs uppercase font-bold tracking-widest text-[var(--text-3)]">Dynamic Signature</label>
                <textarea 
                  rows={4}
                  className="w-full bg-[var(--surface2)] border border-[var(--border)] rounded-lg px-4 py-2.5 outline-none focus:border-[var(--primary)] transition-all font-mono text-sm"
                  value={profile.signature}
                  onChange={e => setProfile({...profile, signature: e.target.value})}
                />
              </div>
            </div>
          </section>

          <section className="glass-card p-6 rounded-2xl border-[var(--border)]">
            <h2 className="text-lg font-bold mb-6 flex items-center gap-2">
              <Sparkles size={18} className="text-[var(--primary)]" />
              AI Behavior Settings
            </h2>
            
            <div className="space-y-6">
              <div className="space-y-3">
                <label className="text-xs uppercase font-bold tracking-widest text-[var(--text-3)]">Response Tone</label>
                <div className="flex gap-4">
                  {['Professional', 'Casual', 'Concise'].map(tone => (
                    <button
                      key={tone}
                      onClick={() => setProfile({...profile, tone_preference: tone})}
                      className={`px-6 py-2 rounded-full border transition-all text-sm font-medium ${
                        profile.tone_preference === tone 
                        ? 'border-[var(--primary)] bg-[var(--primary)] text-white' 
                        : 'border-[var(--border)] bg-[var(--surface2)] text-[var(--text-2)] hover:border-[var(--text-3)]'
                      }`}
                    >
                      {tone}
                    </button>
                  ))}
                </div>
              </div>

              <div className="p-4 rounded-xl bg-[var(--surface2)] border border-[var(--border)] border-dashed">
                <div className="flex items-center gap-2 mb-2 text-[var(--text-3)]">
                  <Terminal size={12} />
                  <span className="text-[10px] uppercase font-bold tracking-widest">Drafting Logic Preview</span>
                </div>
                <p className="text-sm italic opacity-60">
                  "The AI will currently prioritize a <b>{profile.tone_preference}</b> tone while maintaining your goal of <b>{profile.daily_goal}</b>."
                </p>
              </div>
            </div>

            <div className="mt-8 flex items-center gap-4">
              <button 
                onClick={handleSave}
                disabled={saving}
                className={`btn btn-primary px-8 py-3 rounded-xl flex items-center gap-2 shadow-lg shadow-rose-500/20 transition-all ${showSuccess ? 'save-success' : ''}`}
              >
                {saving ? 'Saving...' : <><Save size={18} /> Save Preferences</>}
              </button>
              {showSuccess && (
                <motion.span 
                  initial={{ opacity: 0, x: -10 }} 
                  animate={{ opacity: 1, x: 0 }}
                  className="text-[var(--green)] flex items-center gap-1 text-sm font-bold"
                >
                  <CheckCircle2 size={16} /> Saved Successfully
                </motion.span>
              )}
            </div>
          </section>
        </div>

        {/* Right Column: AI-Driven Task Tracker */}
        <div className="space-y-6">
          <div className="glass-card p-6 rounded-2xl border-[var(--border)]">
            <h2 className="text-sm font-bold mb-4 flex items-center gap-2 text-[var(--text-3)] uppercase tracking-widest">
              Action Items
            </h2>
            
            {tasks.length > 0 ? (
              <div className="space-y-4">
                {tasks.map(task => (
                  <div key={task.id} className="p-3 rounded-lg bg-[var(--surface2)] border-l-2 border-[var(--primary)] hover:bg-[var(--surface)] transition-all cursor-default group">
                    <div className="flex justify-between items-start mb-1">
                      <span className="text-[10px] font-bold text-[var(--primary)] uppercase tracking-tight">
                        {task.classification.replace('_', ' ')}
                      </span>
                      <Clock size={10} className="text-[var(--text-3)]" />
                    </div>
                    <div className="text-xs font-medium truncate mb-1">{task.subject}</div>
                    <div className="text-[10px] text-[var(--text-2)] line-clamp-1 opacity-70">From: {task.sender_email}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-10 opacity-50">
                <CheckCircle2 size={32} className="mx-auto mb-2 text-[var(--green)]" />
                <p className="text-xs">All clear! No urgent signals detected.</p>
              </div>
            )}
            
            <button className="w-full mt-6 py-2 text-[11px] font-bold uppercase tracking-widest text-[var(--primary)] hover:opacity-80 transition-all">
              View All Intelligence &rarr;
            </button>
          </div>

          <div className="p-6 rounded-xl border border-[var(--border)] bg-[var(--surface2)] text-[var(--text-3)]">
            <h3 className="text-xs font-bold mb-2 uppercase tracking-widest">System Sync</h3>
            <p className="text-[11px] leading-relaxed">
              Your profile is synchronized with the Gemini 2.0 Flash long-context window. Every draft or summary produced now respects your unique identity.
            </p>
          </div>
        </div>

      </div>
    </motion.div>
  );
}
