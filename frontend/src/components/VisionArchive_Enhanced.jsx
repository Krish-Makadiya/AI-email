import React from 'react';
import { motion } from 'framer-motion';
import { FileText, Image as ImageIcon, FilePieChart, ExternalLink, Search, Calendar, DollarSign, CheckCircle2 } from 'lucide-react';
import { useEmails } from '../hooks/useEmails';

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const item = {
  hidden: { opacity: 0, scale: 0.9 },
  show: { opacity: 1, scale: 1, transition: { type: 'spring', stiffness: 260, damping: 20 } }
};

function getIcon(docType = '') {
  const t = docType.toLowerCase();
  if (t.includes('invoice') || t.includes('receipt')) return DollarSign;
  if (t.includes('image') || t.includes('photo') || t.includes('picture')) return ImageIcon;
  if (t.includes('data') || t.includes('chart') || t.includes('table') || t.includes('report')) return FilePieChart;
  if (t.includes('schedule') || t.includes('meeting') || t.includes('calendar')) return Calendar;
  return FileText;
}

function VisionCard({ email }) {
  const visionData = email.vision_data;
  
  if (!visionData) {
    return null;
  }

  const Icon = getIcon(visionData.type);

  return (
    <motion.div
      variants={item}
      whileHover={{ scale: 1.05 }}
      className="glass-card neon-glow rounded-xl p-6 flex flex-col cursor-pointer relative overflow-hidden group"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="p-2 bg-[var(--primary-bg)] rounded-lg text-[var(--primary)]">
          <Icon size={20} />
        </div>
        <span className="text-[10px] font-bold uppercase tracking-widest text-[var(--text-3)] group-hover:text-[var(--primary)] transition-colors">
          {visionData.type}
        </span>
      </div>

      {/* Subject */}
      <h3 className="font-bold text-[15px] mb-3 line-clamp-2 group-hover:text-[var(--primary)] transition-colors">
        {email.subject || 'Untitled Document'}
      </h3>

      {/* Short raw vision snippet to make card content variation obvious */}
      {visionData.raw && (
        <div className="mb-3 text-[12px] text-[var(--text-2)] line-clamp-3">
          {visionData.raw.length > 140 ? `${visionData.raw.slice(0,140)}...` : visionData.raw}
        </div>
      )}

      {/* Key Intelligence */}
      {visionData.intelligence && visionData.intelligence.length > 0 && (
        <div className="mb-4 pb-4 border-b border-[var(--border)]">
          <div className="text-[10px] font-bold uppercase tracking-widest text-[var(--text-3)] mb-2">Key Points</div>
          <ul className="space-y-1">
            {visionData.intelligence.slice(0, 3).map((item, idx) => (
              <li key={idx} className="text-[12px] text-[var(--text-2)] flex items-start gap-2">
                <CheckCircle2 size={12} className="text-[var(--green)] mt-0.5 flex-shrink-0" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Critical Dates */}
      {visionData.dates && visionData.dates.length > 0 && (
        <div className="mb-4 pb-4 border-b border-[var(--border)]">
          <div className="text-[10px] font-bold uppercase tracking-widest text-[var(--text-3)] mb-2 flex items-center gap-1">
            <Calendar size={10} /> Dates
          </div>
          <div className="flex flex-wrap gap-2">
            {visionData.dates.map((date, idx) => (
              <span key={idx} className="px-2 py-1 bg-[var(--surface2)] rounded text-[10px] font-medium text-[var(--text-2)]">
                {date}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Financial Figures */}
      {visionData.amounts && visionData.amounts.length > 0 && (
        <div className="mb-4 pb-4 border-b border-[var(--border)]">
          <div className="text-[10px] font-bold uppercase tracking-widest text-[var(--text-3)] mb-2 flex items-center gap-1">
            <DollarSign size={10} /> Amounts
          </div>
          <div className="flex flex-wrap gap-2">
            {visionData.amounts.map((amount, idx) => (
              <span key={idx} className="px-2 py-1 bg-[var(--primary-bg)] text-[var(--primary)] rounded text-[10px] font-bold">
                {amount}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Requested Action */}
      {visionData.action && (
        <div className="mb-4 pb-4 border-b border-[var(--border)]">
          <div className="text-[10px] font-bold uppercase tracking-widest text-[var(--text-3)] mb-2">Action Required</div>
          <p className="text-[12px] text-[var(--text-2)] leading-relaxed italic">
            {visionData.action}
          </p>
        </div>
      )}

      {/* Footer */}
      <div className="mt-auto pt-4 border-t border-[var(--border)] flex items-center justify-between text-[11px] font-medium text-[var(--text-3)]">
        <div className="flex flex-col">
          <span className="truncate">{email.sender_email}</span>
          {email.timestamp && (
            <span className="text-[10px] text-[var(--text-3)]">{new Date(email.timestamp).toLocaleString()}</span>
          )}
        </div>
        <ExternalLink size={12} />
      </div>
    </motion.div>
  );
}

export default function VisionArchive() {
  const { emails, loading } = useEmails();

  const visionEmails = emails.filter(e => {
    const text = (e.attachment_analysis || '').trim().toLowerCase();
    return text !== '' && text !== 'no attachment' && text !== 'none';
  });

  if (loading && visionEmails.length === 0) {
    return (
      <div className="p-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="h-64 skeleton" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <header className="mb-8">
        <h1 className="text-2xl font-bold mb-2">Vision Archive</h1>
        <p className="text-sm text-[var(--text-3)]">
          Actionable intelligence extracted from attachments via Gemini 2.0 Flash. Dates, amounts, and next steps are automatically identified.
        </p>
      </header>

      {visionEmails.length === 0 ? (
        <div className="p-12 text-center border-2 border-dashed border-[var(--border)] rounded-xl">
          <div className="mb-4 inline-flex p-4 bg-[var(--surface2)] rounded-full text-[var(--text-3)]">
            <Search size={24} />
          </div>
          <h3 className="font-semibold text-lg">No Vision Data Found</h3>
          <p className="text-[var(--text-3)] max-w-sm mx-auto mt-2">
            Processed emails with attachments will appear here automatically once analyzed by the vision pipeline.
          </p>
        </div>
      ) : (
        <motion.div 
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          variants={container}
          initial="hidden"
          animate="show"
        >
          {visionEmails.map((email) => (
            <VisionCard key={email.id} email={email} />
          ))}
        </motion.div>
      )}
    </div>
  );
}
