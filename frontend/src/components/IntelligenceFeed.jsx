import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Filter, RefreshCw, AlertTriangle, CheckCircle2, 
  Clock, Users, FileSearch, X, ExternalLink, 
  BrainCircuit, Calendar
} from 'lucide-react';
import { useEmails } from '../hooks/useEmails';
import toast from 'react-hot-toast';
import axios from 'axios';

const CFG = {
  Urgent_Fire:     { label: 'Urgent',    badgeClass: 'badge-urgent',   rowClass: 'row-urgent',  icon: AlertTriangle },
  FYI_Read:        { label: 'FYI',       badgeClass: 'badge-fyi',      rowClass: 'row-fyi',     icon: CheckCircle2  },
  Action_Required: { label: 'Action',    badgeClass: 'badge-action',   rowClass: 'row-action',  icon: Clock         },
  Cold_Outreach:   { label: 'Cold',      badgeClass: 'badge-cold',     rowClass: 'row-default', icon: null          },
  Scheduling:      { label: 'Schedule',  badgeClass: 'badge-schedule', rowClass: 'row-team',    icon: Calendar      },
  Individual:      { label: 'Team',      badgeClass: 'badge-team',     rowClass: 'row-team',    icon: Users         },
};

const getCfg = (type) => CFG[type] ?? CFG['FYI_Read'];

const FILTERS = ['All', 'Urgent_Fire', 'Action_Required', 'Scheduling', 'FYI_Read'];

/* ── Detail Slide-Over ────────────────────────────────── */
const EmailDetail = ({ email, onClose }) => {
  if (!email) return null;
  return (
    <motion.div
      initial={{ x: '100%' }}
      animate={{ x: 0 }}
      exit={{ x: '100%' }}
      transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      className="detail-panel"
    >
      {/* Header */}
      <div className="p-6 border-b border-border flex justify-between items-center bg-surface">
        <div>
          <h3 className="font-bold text-lg">Intelligence Analysis</h3>
          <p className="text-xs text-text-3 uppercase tracking-widest">Signal ID: #{email.id}</p>
        </div>
        <button onClick={onClose} className="p-2 hover:bg-surface2 rounded-full transition-colors text-text-2">
          <X size={20} />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-8 bg-surface">
        {/* Profile Section */}
        <section>
          <div className="flex items-center gap-4 mb-5">
             <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-lg border border-primary/20">
               {email.sender_email?.[0].toUpperCase()}
             </div>
             <div>
               <p className="font-bold text-text text-base leading-tight">{email.sender_email}</p>
               <p className="text-sm text-text-2 mt-1 line-clamp-1">{email.subject}</p>
             </div>
          </div>
          <div className="flex gap-2">
            <span className={`badge ${getCfg(email.classification).badgeClass}`}>
              {getCfg(email.classification).label}
            </span>
            <span className="badge badge-cold">
              Urgency: {email.urgency_score || 0}%
            </span>
          </div>
        </section>

        {/* Intelligence Breakdown */}
        <section className="space-y-4">
          <h4 className="text-[11px] font-bold text-text-3 uppercase tracking-wider flex items-center gap-2">
            <ExternalLink size={12} /> Email Content
          </h4>
          <div className="bg-surface2 p-5 rounded-xl text-sm text-text-2 italic leading-relaxed whitespace-pre-wrap border border-border/50">
            {email.content || "No content extracted by pipeline."}
          </div>
        </section>

        {/* Vision Section */}
        {email.attachment_analysis && (
          <section className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-500">
            <h4 className="text-[11px] font-bold text-primary uppercase tracking-wider flex items-center gap-2">
              <BrainCircuit size={14} /> Gemini Vision Insight
            </h4>
            <div className="bg-primary/5 border border-primary/20 p-5 rounded-xl text-sm text-text border-l-4 border-l-primary leading-relaxed shadow-sm">
              {email.attachment_analysis}
            </div>
          </section>
        )}
      </div>

      {/* Footer Actions */}
      <div className="p-6 border-t border-border bg-surface shadow-[0_-4px_20px_rgba(0,0,0,0.03)]">
        <button 
          onClick={() => {
            const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
            const t = toast.loading("Promoting intelligence to Hub...");
            axios.post(`${API_BASE}/drafts`, {
              email_action_id: email.id,
              content: email.suggested_draft || "DRAFT: Manual review required.",
              recipient: email.sender_email,
              subject: `Re: ${email.subject}`,
              type: email.classification === 'Scheduling' ? 'Scheduling' : 'General',
              reasoning: email.intelligence_reasoning,
              tags: [email.classification, "Manual-Promotion"]
            }).then(() => {
              toast.success("Ready for review in Draft Hub!", { id: t });
              onClose();
            }).catch(e => toast.error("Promotion pipeline break.", { id: t }));
          }}
          className="w-full btn btn-primary py-4 justify-center text-sm font-bold shadow-lg shadow-primary/20"
        >
          Stage for Review
        </button>
      </div>
    </motion.div>
  );
};

/* ── Main Component ───────────────────────────────────── */
export default function IntelligenceFeed({ embedded = false }) {
  const { emails, loading, error, refetch } = useEmails();
  const [filter, setFilter] = useState('All');
  const [selectedEmail, setSelectedEmail] = useState(null);

  const displayed = filter === 'All' ? emails : emails.filter(e => e.classification === filter);

  return (
    <div style={{ padding: embedded ? '0' : '24px 28px' }}>
      {!embedded && (
        <div className="mb-8 flex justify-between items-end">
          <div>
            <h2 className="text-2xl font-bold tracking-tight">Intelligence Feed</h2>
            <p className="text-sm text-text-3 font-medium">Processing signals from LangGraph pipeline</p>
          </div>
          <button onClick={refetch} className="btn btn-ghost px-4 bg-surface shadow-sm">
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            <span className="font-semibold">Refresh</span>
          </button>
        </div>
      )}

      {/* Filter Row */}
      <div className="flex items-center gap-2.5 mb-6 overflow-x-auto pb-2 scrollbar-none">
        <Filter size={14} className="text-text-3 shrink-0 mr-1" />
        {FILTERS.map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`filter-pill shrink-0 ${filter === f ? 'active' : ''}`}
          >
            {f === 'All' ? 'All Signals' : getCfg(f).label}
          </button>
        ))}
      </div>

      {/* Table Container */}
      <div className="table-card relative bg-surface shadow-sm">
        <table className="data-table">
          <thead>
            <tr>
              <th className="w-1"></th>
              <th className="w-[30%]">Sender Profile</th>
              <th>Intelligence Subject</th>
              <th className="w-[15%]">Priority</th>
              <th className="w-[10%] text-right pr-8">Actions</th>
            </tr>
          </thead>
          <tbody className="relative">
            <AnimatePresence initial={false}>
              {loading && emails.length === 0 ? (
                Array.from({ length: 10 }).map((_, i) => (
                  <tr key={`skel-${i}`}>
                    <td className="w-1"></td>
                    <td colSpan={4} className="p-4"><div className="skeleton h-5 w-5/6 my-1" /></td>
                  </tr>
                ))
              ) : (
                displayed.map((email) => {
                  const cfg = getCfg(email.classification);
                  return (
                    <motion.tr
                      key={email.id}
                      initial={{ opacity: 0, scale: 0.99 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.98 }}
                      layout
                      onClick={() => setSelectedEmail(email)}
                      className={`${cfg.rowClass} cursor-pointer group active:scale-[0.99] transition-all`}
                    >
                      <td className="w-1"></td>
                      <td>
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-surface2 flex items-center justify-center text-[11px] font-bold border border-border group-hover:border-primary/30 transition-colors">
                            {email.sender_email?.[0].toUpperCase()}
                          </div>
                          <span className="truncate max-w-[180px] font-medium text-text">{email.sender_email}</span>
                        </div>
                      </td>
                      <td>
                        <div className="flex items-center gap-2">
                          <span className="truncate max-w-[320px] text-text-2 text-sm">{email.subject}</span>
                          {email.attachment_analysis && (
                            <div className="flex items-center gap-1.5 px-2 py-0.5 bg-primary/5 rounded border border-primary/10 text-primary animate-pulse">
                              <FileSearch size={12} />
                              <span className="text-[10px] font-bold uppercase tracking-wider">Vision</span>
                            </div>
                          )}
                        </div>
                      </td>
                      <td>
                        <span className={`badge ${cfg.badgeClass} shadow-sm`}>
                          {cfg.label}
                        </span>
                      </td>
                      <td className="text-right pr-8">
                        <div className="opacity-0 group-hover:opacity-100 transition-all transform translate-x-2 group-hover:translate-x-0">
                          <BrainCircuit size={17} className="text-primary" />
                        </div>
                      </td>
                    </motion.tr>
                  );
                })
              )}
            </AnimatePresence>
          </tbody>
        </table>
      </div>

      {/* Slide-Over Overlay Hub */}
      <AnimatePresence>
        {selectedEmail && (
          <div className="fixed inset-0 z-[1500]"> {/* Wrapper with high z-index */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedEmail(null)}
              className="absolute inset-0 bg-black/50 backdrop-blur-[2px]"
            />
            <EmailDetail email={selectedEmail} onClose={() => setSelectedEmail(null)} />
          </div>
        )}
      </AnimatePresence>

      {error && !loading && (
        <div className="mt-8 p-4 bg-primary/5 border border-primary/20 text-primary text-xs rounded-xl text-center font-bold tracking-tight">
          ⚠️ {error}. Trying to reconnect brain layers...
        </div>
      )}
    </div>
  );
}
