import React from 'react';
import { motion } from 'framer-motion';
import { FileText, Image as ImageIcon, FilePieChart, ExternalLink, Search } from 'lucide-react';
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

function getIcon(content = '') {
  const c = content.toLowerCase();
  if (c.includes('image') || c.includes('photo') || c.includes('picture')) return ImageIcon;
  if (c.includes('data') || c.includes('chart') || c.includes('table')) return FilePieChart;
  return FileText;
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
            <div key={i} className="h-48 skeleton" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <header className="mb-8">
        <h1 className="text-xl font-bold mb-2">Vision Archive</h1>
        <p className="text-sm text-[var(--text-3)]">
          Intelligence extracted from document attachments and visual data via Gemini 2.0 Flash.
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
          {visionEmails.map((email) => {
            const Icon = getIcon(email.attachment_analysis);
            return (
              <motion.div
                key={email.id}
                variants={item}
                whileHover={{ scale: 1.05 }}
                className="glass-card neon-glow rounded-xl p-6 flex flex-col cursor-pointer relative overflow-hidden group"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="p-2 bg-[var(--primary-bg)] rounded-lg text-[var(--primary)]">
                    <Icon size={20} />
                  </div>
                  <span className="text-[10px] font-bold uppercase tracking-widest text-[var(--text-3)] group-hover:text-[var(--primary)] transition-colors">
                    Processed
                  </span>
                </div>

                <h3 className="font-bold text-[15px] mb-3 line-clamp-1 group-hover:text-[var(--primary)] transition-colors">
                  {email.subject || 'Untitled Artifact'}
                </h3>

                <p className="text-sm text-[var(--text-2)] leading-relaxed line-clamp-4 flex-1">
                  {email.attachment_analysis}
                </p>

                <div className="mt-5 pt-4 border-t border-[var(--border)] flex items-center justify-between text-[11px] font-medium text-[var(--text-3)]">
                  <span>{email.sender_email}</span>
                  <ExternalLink size={12} />
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      )}
    </div>
  );
}
