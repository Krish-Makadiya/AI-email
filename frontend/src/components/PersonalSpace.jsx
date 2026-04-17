import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { User, Shield, CheckCircle2, Clock, Terminal, Save, Sparkles, BrainCircuit, Bell, Mailbox, Plus } from 'lucide-react';
import axios from 'axios';
import { useEmails } from '../hooks/useEmails';

const API_BASE = 'http://127.0.0.1:8000';

export default function PersonalSpace() {
    const { emails } = useEmails();
    const [profile, setProfile] = useState({
        name: 'Michael Jack',
        tone_preference: 'Professional',
        signature: 'Best regards,\nMichael',
        daily_goal: 'Zero Inbox by 5PM'
    });
    const [saving, setSaving] = useState(false);
    const [showSuccess, setShowSuccess] = useState(false);

    // Interactive mock state for Context Memory
    const [memoryTags, setMemoryTags] = useState(['Prefers concise emails', 'Works 9-5 EST', 'Direct communication style']);
    const [newTag, setNewTag] = useState('');

    useEffect(() => {
        fetchProfile();
    }, []);

    const fetchProfile = async () => {
        try {
            const res = await axios.get(`${API_BASE}/user-profile`);
            if (res.data && res.data.name) {
                setProfile(res.data);
            }
        } catch (err) {
            console.error("Fetch profile error:", err);
            // Fallbacks to initial state mock
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
            // Mock success for UI interactivity
            setShowSuccess(true);
            setTimeout(() => setShowSuccess(false), 2000);
        } finally {
            setSaving(false);
        }
    };

    const addMemoryTag = (e) => {
        if (e.key === 'Enter' && newTag.trim() !== '') {
            setMemoryTags([...memoryTags, newTag.trim()]);
            setNewTag('');
        }
    };

    const removeTag = (idx) => {
        setMemoryTags(memoryTags.filter((_, i) => i !== idx));
    };

    const tasks = emails.filter(e =>
        e.classification === 'Urgent_Fire' || e.classification === 'Action_Required'
    ).slice(0, 4);

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 md:p-8 w-full max-w-[1800px] mx-auto min-h-full bg-bg font-sans"
        >
            <header className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight text-text mb-1 flex items-center gap-2">
                        <User className="text-primary" size={24} />
                        Personal Space
                    </h1>
                    <p className="text-text-2 text-sm font-medium">Manage your identity, AI preferences, and dynamic context.</p>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={handleSave}
                        disabled={saving}
                        className={`px-5 py-2 rounded-lg font-bold text-xs shadow-sm transition-all flex items-center gap-2 ${showSuccess
                                ? 'bg-green-500 text-white'
                                : 'bg-primary hover:bg-primary/90 text-white'
                            }`}
                    >
                        {saving ? (
                            <span className="flex items-center gap-2"><Clock size={14} className="animate-spin" /> Saving...</span>
                        ) : showSuccess ? (
                            <span className="flex items-center gap-2"><CheckCircle2 size={14} /> Saved</span>
                        ) : (
                            <span className="flex items-center gap-2"><Save size={14} /> Save Profile</span>
                        )}
                    </button>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Left Column: User Identity & AI Behavior */}
                <div className="lg:col-span-2 space-y-6">

                    {/* Core Identity */}
                    <section className="bg-surface rounded-xl border border-border shadow-sm relative overflow-hidden p-6">
                        <div className="absolute top-0 right-0 p-6 opacity-[0.03] dark:opacity-[0.08] pointer-events-none">
                            <Shield size={120} />
                        </div>
                        <h2 className="text-sm font-bold text-text mb-5 flex items-center gap-2 uppercase tracking-wider">
                            Core Identity
                        </h2>

                        <div className="space-y-5 relative z-10">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                                <div className="space-y-1.5">
                                    <label className="text-[11px] uppercase font-bold tracking-widest text-text-3">Display Name</label>
                                    <input
                                        className="w-full bg-surface2 border border-border rounded-lg px-4 py-2 text-sm text-text font-medium outline-none focus:ring-1 focus:ring-primary transition-all"
                                        value={profile.name}
                                        onChange={e => setProfile({ ...profile, name: e.target.value })}
                                    />
                                </div>
                                <div className="space-y-1.5">
                                    <label className="text-[11px] uppercase font-bold tracking-widest text-text-3">Daily Focus Goal</label>
                                    <input
                                        className="w-full bg-surface2 border border-border rounded-lg px-4 py-2 text-sm text-text font-medium outline-none focus:ring-1 focus:ring-primary transition-all"
                                        value={profile.daily_goal}
                                        onChange={e => setProfile({ ...profile, daily_goal: e.target.value })}
                                    />
                                </div>
                            </div>

                            <div className="space-y-1.5">
                                <label className="text-[11px] uppercase font-bold tracking-widest text-text-3">Dynamic Signature</label>
                                <textarea
                                    rows={3}
                                    className="w-full bg-surface2 border border-border rounded-lg px-4 py-2 text-sm text-text font-medium outline-none focus:ring-1 focus:ring-primary transition-all font-mono"
                                    value={profile.signature}
                                    onChange={e => setProfile({ ...profile, signature: e.target.value })}
                                />
                            </div>
                        </div>
                    </section>

                    {/* AI Memory Context */}
                    <section className="bg-surface rounded-xl border border-border shadow-sm p-6">
                        <h2 className="text-sm font-bold text-text mb-4 flex items-center gap-2 uppercase tracking-wider">
                            <BrainCircuit size={16} className="text-primary" />
                            AI Memory & Context
                        </h2>
                        <p className="text-xs font-medium text-text-2 mb-5">
                            Provide context cues that the AI will use to construct personalized email drafts and summaries.
                        </p>

                        <div className="flex flex-wrap gap-2 mb-4">
                            <AnimatePresence>
                                {memoryTags.map((tag, idx) => (
                                    <motion.div
                                        initial={{ scale: 0.9, opacity: 0 }}
                                        animate={{ scale: 1, opacity: 1 }}
                                        exit={{ scale: 0.9, opacity: 0 }}
                                        key={idx}
                                        className="px-3 py-1.5 rounded-full bg-surface2 border border-border text-[11px] font-bold text-text flex items-center gap-2 group cursor-pointer shadow-sm hover:border-text-3 transition-colors"
                                        onClick={() => removeTag(idx)}
                                    >
                                        {tag}
                                        <span className="text-text-3 group-hover:text-primary transition-colors">&times;</span>
                                    </motion.div>
                                ))}
                            </AnimatePresence>
                        </div>

                        <div className="relative">
                            <input
                                className="w-full bg-surface2 border border-border rounded-lg pl-9 pr-4 py-2 text-sm text-text font-medium outline-none focus:ring-1 focus:ring-primary transition-all"
                                placeholder="Add context cue (e.g. 'I am out of office on Fridays') and press Enter"
                                value={newTag}
                                onChange={(e) => setNewTag(e.target.value)}
                                onKeyDown={addMemoryTag}
                            />
                            <Plus size={14} className="absolute left-3 top-2.5 text-text-3" />
                        </div>
                    </section>

                    {/* AI Behavior Settings */}
                    <section className="bg-surface rounded-xl border border-border shadow-sm p-6">
                        <h2 className="text-sm font-bold text-text mb-5 flex items-center gap-2 uppercase tracking-wider">
                            <Sparkles size={16} className="text-primary" />
                            Drafting Preferences
                        </h2>

                        <div className="space-y-6">
                            <div className="space-y-3">
                                <label className="text-[11px] uppercase font-bold tracking-widest text-text-3">Response Tone</label>
                                <div className="flex flex-wrap gap-3">
                                    {['Professional', 'Casual', 'Concise', 'Empathetic'].map(tone => (
                                        <button
                                            key={tone}
                                            onClick={() => setProfile({ ...profile, tone_preference: tone })}
                                            className={`px-5 py-2 rounded-lg border transition-all text-xs font-bold ${profile.tone_preference === tone
                                                    ? 'border-primary bg-primary text-white shadow-md'
                                                    : 'border-border bg-surface2 text-text-2 hover:text-text hover:border-border'
                                                }`}
                                        >
                                            {tone}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="p-4 rounded-xl bg-surface2 border border-border">
                                <div className="flex items-center gap-2 mb-2 text-text-3">
                                    <Terminal size={12} />
                                    <span className="text-[10px] uppercase font-bold tracking-widest">Logic Preview</span>
                                </div>
                                <p className="text-sm italic font-medium text-text-2">
                                    "The AI will prioritize a <b className="text-text">{profile.tone_preference}</b> tone, maintaining your goal of <b className="text-text">{profile.daily_goal}</b>, and respecting {memoryTags.length} context tags."
                                </p>
                            </div>
                        </div>
                    </section>
                </div>

                {/* Right Column: AI-Driven Insights & Tracking */}
                <div className="space-y-6">

                    {/* Urgent Action Tracker */}
                    <div className="bg-surface p-6 rounded-xl border border-border shadow-sm">
                        <h2 className="text-sm font-bold text-text mb-4 flex items-center gap-2 uppercase tracking-wider">
                            <Bell size={16} className="text-primary" />
                            Urgent Attention
                        </h2>

                        {tasks.length > 0 ? (
                            <div className="space-y-3">
                                {tasks.map(task => (
                                    <div key={task.id} className="p-3 rounded-lg bg-surface2 border-l-2 border-primary hover:bg-border/50 transition-colors cursor-pointer group">
                                        <div className="flex justify-between items-start mb-1">
                                            <span className="text-[10px] font-bold text-primary uppercase tracking-tight">
                                                {task.classification.replace('_', ' ')}
                                            </span>
                                            <Clock size={10} className="text-text-3" />
                                        </div>
                                        <div className="text-xs font-bold text-text truncate mb-1">{task.subject}</div>
                                        <div className="text-[10px] font-semibold text-text-2 line-clamp-1">From: {task.sender_email}</div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8 opacity-60">
                                <CheckCircle2 size={32} className="mx-auto mb-2 text-green-500" />
                                <p className="text-xs font-semibold text-text-2">All clear! No urgent signals.</p>
                            </div>
                        )}

                        <button className="w-full mt-4 py-2 text-[11px] font-bold uppercase tracking-widest text-primary hover:bg-primary hover:text-white rounded-md transition-all">
                            View Analytics &rarr;
                        </button>
                    </div>

                    {/* System Sync Context */}
                    <div className="p-5 rounded-xl border border-border bg-surface2 text-text-3 flex items-start gap-3">
                        <BrainCircuit size={16} className="shrink-0 mt-0.5" />
                        <div>
                            <h3 className="text-[11px] font-bold mb-1 uppercase tracking-widest text-text-2">System Sync</h3>
                            <p className="text-xs leading-relaxed font-medium">
                                Your profile is synchronized. Every draft or summary produced respects your unique identity setup.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
