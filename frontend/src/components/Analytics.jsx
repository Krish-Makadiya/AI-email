import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import { Info, Search, Columns, Download } from 'lucide-react';
import { useEmails } from '../hooks/useEmails';

// Inherit global semantic variables for diagrams to guarantee perfect light/dark contrast
const AREA_CHART_COLOR = 'var(--primary)'; 

const PIE_COLORS = {
  Urgent_Fire: 'var(--primary)',     
  Action_Required: 'var(--amber)', 
  FYI_Read: 'var(--blue)',        
  Scheduling: 'var(--green)',      
  Cold_Outreach: '#8b5cf6'    
};

// Container animations
const containerVariants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1 } }
};

const itemVariants = {
  hidden: { opacity: 0, y: 15 },
  show: { opacity: 1, y: 0, transition: { type: 'spring', damping: 20, stiffness: 200 } }
};

const MiniBarChart = ({ color, isFilled }) => {
  const heights = [40, 60, 30, 80, 50, 90, 40, 70, 60, 50, 80, 40, 60, 40, 70];
  return (
    <div className="flex items-end justify-between h-24 w-full gap-[2px] mt-2">
      {heights.map((h, i) => (
        <div 
          key={i} 
          className="w-full rounded-t-sm" 
          style={{ 
            height: `${h}%`, 
            backgroundColor: isFilled ? 'white' : color,
            opacity: isFilled ? (i % 2 === 0 ? 0.9 : 0.6) : (i % 2 === 0 ? 0.3 : 0.15) 
          }} 
        />
      ))}
    </div>
  )
}

function StatCard({ title, value, subtext, color, isFilled, trend, trendUp }) {
  return (
    <div 
      className={`p-4 rounded-xl border ${isFilled ? 'border-transparent shadow-md' : 'border-border shadow-sm bg-surface text-text'} flex flex-col h-[230px] relative overflow-hidden`} 
      style={isFilled ? { backgroundColor: 'var(--primary)', color: 'white', boxShadow: `0 4px 14px 0 var(--primary-bg)` } : {}}
    >
      <div className="flex justify-between items-center mb-1">
        <span className={`text-xs font-semibold ${isFilled ? 'text-white/95' : 'text-text-2'}`}>{title}</span>
        <Info size={14} className={isFilled ? 'text-white/70' : 'text-text-3'} />
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-bold tracking-tight">{value}</span>
        {trend && (
           <span className={`text-[10px] px-1.5 py-0.5 rounded flex items-center font-bold ${isFilled ? 'bg-white/20 text-white' : 'bg-surface2 text-text-2'}`}>
             {trendUp ? '↗' : '↘'} {trend}
           </span>
        )}
      </div>
      <div className={`text-[11px] mt-1 font-medium ${isFilled ? 'text-white/80' : 'text-text-3'}`}>
        {value} {subtext}
      </div>
      <div className="mt-auto">
        <MiniBarChart color={isFilled ? '#ffffff' : color} isFilled={isFilled} />
      </div>
    </div>
  )
}

export default function Analytics() {
  const { emails, loading } = useEmails();

  const analyticsData = useMemo(() => {
    if (!emails.length) return null;

    // 1. Sender Frequency
    const senderCounts = {};
    emails.forEach(e => {
      senderCounts[e.sender_email] = (senderCounts[e.sender_email] || 0) + 1;
    });
    const topSenders = Object.entries(senderCounts)
      .map(([name, value]) => ({ name: name.split('@')[0], fullName: name, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 8);

    // 2. Classification Mix
    const classCounts = {};
    emails.forEach(e => {
      const cls = e.classification || 'FYI_Read';
      classCounts[cls] = (classCounts[cls] || 0) + 1;
    });
    const classificationMix = Object.entries(classCounts).map(([name, value]) => ({ name, value }));

    // 3. Rising Relationships (First 25 vs Last 25)
    const newHalf = emails.slice(0, 25);
    const oldHalf = emails.slice(25, 50);

    const newCounts = {};
    newHalf.forEach(e => newCounts[e.sender_email] = (newCounts[e.sender_email] || 0) + 1);

    const oldCounts = {};
    oldHalf.forEach(e => oldCounts[e.sender_email] = (oldCounts[e.sender_email] || 0) + 1);

    const rising = Object.keys(newCounts)
      .map(email => {
        const countNew = newCounts[email];
        const countOld = oldCounts[email] || 0;
        return { email, diff: countNew - countOld, count: countNew };
      })
      .filter(item => item.diff > 0)
      .sort((a, b) => b.diff - a.diff)
      .slice(0, 5);

    return { topSenders, classificationMix, rising, total: emails.length };
  }, [emails]);

  if (loading && !analyticsData) {
    return (
      <div className="w-full max-w-[1800px] px-3 md:px-5 mx-auto space-y-3 h-full bg-bg py-4">
        <div className="h-8 w-48 bg-surface2 animate-pulse rounded-md" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="h-[130px] bg-surface border border-border animate-pulse rounded-xl" />
          <div className="h-[130px] bg-surface2 animate-pulse rounded-xl" />
          <div className="h-[130px] bg-surface border border-border animate-pulse rounded-xl" />
          <div className="h-[130px] bg-surface border border-border animate-pulse rounded-xl" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
          <div className="lg:col-span-2 h-[300px] bg-surface border border-border animate-pulse rounded-xl" />
          <div className="h-[300px] bg-surface border border-border animate-pulse rounded-xl" />
        </div>
      </div>
    );
  }

  if (!analyticsData) return null;

  return (
    <div className="min-h-full bg-bg font-sans pb-6 pt-3">
      <motion.div 
        className="w-full max-w-[1800px] px-3 md:px-5 mx-auto"
        variants={containerVariants}
        initial="hidden"
        animate="show"
      >
        {/* HEADER SECTION */}
        <div className="mb-3 flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-border pb-2.5">
          <h1 className="text-lg font-bold tracking-tight text-text flex items-center gap-2">
             Email Analytics
          </h1>
          <div className="flex items-center gap-3">
             <div className="w-7 h-7 rounded-full bg-surface2 flex items-center justify-center text-text-2 font-bold text-xs">
                MJ
             </div>
             <span className="text-xs font-semibold text-text-2">Michael Jack</span>
          </div>
        </div>

        <div className="flex items-center justify-between mb-3">
          <h2 className="text-[13px] font-bold text-text uppercase tracking-wider">Overview Delivery</h2>
          <button className="text-xs font-semibold text-text-2 bg-surface shadow-sm border border-border px-3 py-1.5 rounded-md hover:bg-surface2 transition-colors">
            Save Report
          </button>
        </div>

        {/* TOP ROW: KEY METRICS */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
          <StatCard 
            title="Urgency Rate" 
            value={analyticsData.classificationMix.find(c => c.name === 'Urgent_Fire')?.value || 0} 
            subtext="Urgent"
            color="var(--primary)" 
            trend="1.2%"
            trendUp={true}
            isFilled={false}
          />
          <StatCard 
            title="Information Rate" 
            value={analyticsData.classificationMix.find(c => c.name === 'FYI_Read')?.value || 0} 
            subtext="Delivered"
            color="var(--primary)" 
            trend="0.9%"
            trendUp={true}
            isFilled={true}
          />
          <StatCard 
            title="Action Required" 
            value={(analyticsData.classificationMix.find(c => c.name === 'Scheduling')?.value || 0) + (analyticsData.classificationMix.find(c => c.name === 'Action_Required')?.value || 0)} 
            subtext="Actionable"
            color="var(--amber)" 
            trend="0.5%"
            trendUp={false}
            isFilled={false}
          />
          <StatCard 
            title="Spam Report Rate" 
            value={analyticsData.topSenders.length} 
            subtext="Unique Senders"
            color="var(--primary)" 
            trend="0.7%"
            trendUp={false}
            isFilled={false}
          />
        </div>

        {/* MIDDLE ROW: CHARTS */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 mb-4">
          {/* RELATIONSHIP HEATMAP */}
          <motion.div variants={itemVariants} className="lg:col-span-2 bg-surface border border-border rounded-xl shadow-sm p-4">
            <div className="flex justify-between items-center mb-3">
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-sm text-text">Email Data Cart</h3>
                <Info size={14} className="text-text-3" />
              </div>
              <div className="flex items-center gap-3 text-[11px] font-semibold text-text-2">
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: AREA_CHART_COLOR }}></div>
                  Sender Frequency
                </div>
              </div>
            </div>
            
            <div className="h-[200px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={analyticsData.topSenders} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={AREA_CHART_COLOR} stopOpacity={0.25}/>
                      <stop offset="95%" stopColor={AREA_CHART_COLOR} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
                  <XAxis 
                    dataKey="name" 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: 'var(--text-3)', fontSize: 10, fontWeight: 500 }}
                    dy={10}
                  />
                  <YAxis 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: 'var(--text-3)', fontSize: 10, fontWeight: 500 }} 
                  />
                  <RechartsTooltip 
                    contentStyle={{ borderRadius: '8px', border: '1px solid var(--border)', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', background: 'var(--surface)' }}
                    itemStyle={{ color: AREA_CHART_COLOR, fontWeight: 700 }}
                    labelStyle={{ color: 'var(--text-2)', fontWeight: 600, marginBottom: 4 }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="value" 
                    stroke={AREA_CHART_COLOR} 
                    strokeWidth={2.5} 
                    fillOpacity={1} 
                    fill="url(#colorValue)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* SIGNALS BREAKDOWN (DONUT) */}
          <motion.div variants={itemVariants} className="bg-surface border border-border rounded-xl shadow-sm p-4 flex flex-col">
            <div className="flex justify-between items-center mb-2">
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-sm text-text">Performance by Mix</h3>
                <Info size={14} className="text-text-3" />
              </div>
            </div>
            
            <div className="flex-1 min-h-[160px] flex items-center justify-center relative">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={analyticsData.classificationMix}
                    innerRadius={65}
                    outerRadius={90}
                    paddingAngle={2}
                    dataKey="value"
                    stroke="none"
                  >
                    {analyticsData.classificationMix.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={PIE_COLORS[entry.name] || 'var(--text-3)'} />
                    ))}
                  </Pie>
                  <RechartsTooltip 
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', background: 'var(--surface)' }}
                    itemStyle={{ fontWeight: 600, color: 'var(--text)' }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <span className="text-xl font-bold text-text">{analyticsData.total}</span>
                <span className="text-[9px] font-semibold text-text-3 mt-0.5">Total Signals</span>
              </div>
            </div>
            
            <div className="flex flex-wrap justify-center gap-x-3 gap-y-2 mt-2">
               {analyticsData.classificationMix.map(item => (
                 <div key={item.name} className="flex items-center gap-1.5 text-[10px] font-bold text-text-2">
                   <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: PIE_COLORS[item.name] || 'var(--text-3)' }}></div>
                   {item.name.split('_')[0]}
                 </div>
               ))}
            </div>
          </motion.div>
        </div>

        {/* BOTTOM ROW: RISING RELATIONSHIPS TABLE */}
        <motion.div variants={itemVariants} className="bg-surface border border-border rounded-xl shadow-sm p-4 mb-2">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-3">
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-sm text-text">All Email Performance</h3>
              <Info size={14} className="text-text-3" />
            </div>
            <div className="flex flex-wrap items-center gap-2 mt-2 md:mt-0">
              <div className="relative">
                <input 
                  type="text" 
                  placeholder="Search" 
                  className="pl-7 pr-3 py-1.5 w-[160px] bg-surface2 border border-border rounded-md text-xs focus:outline-none focus:ring-1 focus:ring-primary transition-shadow text-text" 
                />
                <Search size={12} className="absolute left-2.5 top-2 text-text-3" />
              </div>
            </div>
          </div>

          <div className="flex gap-4 mb-2 border-b border-border">
            <button className="px-1 py-1.5 text-[11px] font-bold text-text border-b-2 border-text">
              Sent Emails
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-border bg-surface2/50">
                  <th className="py-2.5 px-3 text-[10px] font-bold text-text-2 tracking-wide w-8">
                     <input type="checkbox" className="rounded border-border bg-surface" />
                  </th>
                  <th className="py-2.5 px-3 text-[10px] font-bold text-text-2 tracking-wide">Email</th>
                  <th className="py-2.5 px-3 text-[10px] font-bold text-text-2 tracking-wide">Publish Date</th>
                  <th className="py-2.5 px-3 text-[10px] font-bold text-text-2 tracking-wide">Sent</th>
                  <th className="py-2.5 px-3 text-[10px] font-bold text-text-2 tracking-wide">Click Through Rate</th>
                  <th className="py-2.5 px-3 text-[10px] font-bold text-text-2 tracking-wide">Delivered Rate</th>
                </tr>
              </thead>
              <tbody>
                {analyticsData.rising.map((item, idx) => (
                  <tr key={item.email} className={`border-b border-border hover:bg-surface2 transition-colors ${idx === 2 ? 'bg-surface2' : ''}`}>
                    <td className="py-2.5 px-3">
                      <input type="checkbox" defaultChecked={idx === 2} className="rounded border-border focus:ring-primary" />
                    </td>
                    <td className="py-2.5 px-3">
                       <div className="font-semibold text-xs text-text">{item.email}</div>
                    </td>
                    <td className="py-2.5 px-3">
                       <div className="text-xs font-semibold text-text-2">17/8/2022</div>
                    </td>
                    <td className="py-2.5 px-3">
                       <div className="text-xs font-bold text-text">{item.count}</div>
                    </td>
                    <td className="py-2.5 px-3 text-xs font-bold text-text">
                       {item.diff}.04%
                    </td>
                    <td className="py-2.5 px-3">
                       <span className="text-[11px] font-bold text-text">100%</span>
                    </td>
                  </tr>
                ))}
                {analyticsData.rising.length === 0 && (
                  <tr>
                    <td colSpan="6" className="py-6 text-center text-xs font-medium text-text-3">
                      Insufficient data for performance metrics.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </motion.div>

      </motion.div>
    </div>
  );
}
